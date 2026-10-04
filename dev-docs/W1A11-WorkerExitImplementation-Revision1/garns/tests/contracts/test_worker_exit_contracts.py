from __future__ import annotations

import copy
import unittest

from garns.backends.contracts.admission import LeaseState, OperationKind, PlanStep
from garns.backends.contracts.authority import RuntimeAuthority, TrustedClaims
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import (
    ActivationEvidence, ActivationState, DeploymentGenerationState,
    ResourceIdentity, ResourceKind,
)
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.migration_reference import (
    AttemptPhase, MigrationRequestIdentity, ParticipantState,
)
from garns.backends.contracts.semantic import BindingIdentity
from garns.backends.contracts.snapshot_reference import NeutralRefreshReceipt
from garns.backends.contracts.values import (
    Capability, ContractRefusal, ParameterValues, QualifiedDeployment,
    RefetchRequired, RefreshCommitRefused, RefreshContainmentPending,
    RefreshRecordUnavailable, RevisionCursor, TransactionIdentity,
)
from garns.backends.contracts.worker_authority import (
    DeliveryPublicationCandidate, EffectKnowledge,
    ReceivingTaskLifecycleObservation, WorkerCommandSpec, WorkerCommandState,
    WorkerExitKind,
)
from tests.contracts.test_admission_contracts import build_fixture
from tests.contracts.test_lifetime_contracts import (
    make_lifetime_fixture, publish, register, settle_handoff, step,
)


class EffectFault(BaseException):
    pass


def prepare_refresh(fixture, registration, revision, rows):
    registry = fixture["registry"]
    owner = fixture["task"][0]
    lease = registry.acquire(
        fixture["handle"], OperationKind.REFRESH,
        ParameterValues({"tenant": "a"}), fixture["context"],
        resource=fixture["subscription"], owner=owner,
    )
    for plan_step in (PlanStep.FETCH, PlanStep.ASSEMBLY, PlanStep.CURSOR_ADVANCE):
        step(fixture, lease, plan_step)
    candidate = registry.setup_reference_refresh_candidate(
        lease, owner, registration,
        RevisionCursor(fixture["scope"], 1, revision - 1),
        RevisionCursor(fixture["scope"], 1, revision),
        RevisionCursor(fixture["scope"], 1, revision),
        rows, f"advance-{revision}",
    )
    return lease, candidate


class WorkerExitCausalTests(unittest.TestCase):
    def test_non_delivery_worker_publication_is_one_atomic_terminal_release(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        caller = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection"], owner=caller,
        )
        authorization = registry.dispatch_worker(lease)
        registry.dequeue_worker(lease, authorization)
        registry.worker_issuer.run_effect(authorization, 1)
        result = registry.setup_reference_worker_result(authorization, "value")
        receipt = registry.worker_exit_success(authorization, result)
        with self.assertRaises(ContractRefusal):
            registry.accept_worker_result(receipt)
        self.assertEqual(0, registry.publications)
        stop = registry.setup_reference_worker_stop(authorization)
        registry.observe_worker_stopped(stop)
        self.assertEqual("value", registry.accept_worker_result(receipt))
        step(fixture, lease, PlanStep.LOWER, "lower")
        registry.run_plan_step(
            lease, PlanStep.PUBLICATION, caller, registry.issue_consumer("publish"),
        )
        self.assertEqual(LeaseState.SUCCEEDED, registry.lease_state(lease))
        self.assertEqual((1, 0), (registry.publications, fixture["coordinator"].count()))

    def test_wrong_worker_and_lifecycle_identities_are_mutation_free(self) -> None:
        worker = object()
        fixture = build_fixture(assigned_worker_provider=lambda serial: worker)
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection"], owner=fixture["task"][0],
        )
        authorization = registry.dispatch_worker(lease)
        before = (registry.lease_state(lease), registry.worker_ordinals(authorization))
        with self.assertRaises(ContractRefusal):
            registry.dequeue_worker(lease, authorization)
        self.assertEqual(before, (registry.lease_state(lease), registry.worker_ordinals(authorization)))
        observation = registry.setup_reference_receiving_task_done(lease)
        with self.assertRaises(ContractRefusal):
            registry.observe_receiving_task_done(object.__new__(ReceivingTaskLifecycleObservation))
        self.assertEqual(before, (registry.lease_state(lease), registry.worker_ordinals(authorization)))
        observed = registry.observe_receiving_task_done(observation)
        self.assertIsNone(observed)
        self.assertIs(observed, registry.observe_receiving_task_done(observation))
        self.assertEqual(LeaseState.CANCELLED_CONFIRMED, registry.lease_state(lease))

    def test_cleanup_schedule_is_finite_and_ordered(self) -> None:
        fixture = build_fixture(
            command_schedule_provider=lambda kind: (
                WorkerCommandSpec("cleanup-order", (1,), cleanup_steps=2),
            ),
        )
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection"], owner=fixture["task"][0],
        )
        authorization = registry.dispatch_worker(lease)
        registry.dequeue_worker(lease, authorization)
        with self.assertRaises(ContractRefusal):
            registry.run_worker_cleanup(authorization, 2)
        registry.run_worker_cleanup(authorization, 1)
        with self.assertRaises(ContractRefusal):
            registry.run_worker_cleanup(authorization, 1)
        registry.run_worker_cleanup(authorization, 2)
        with self.assertRaises(ContractRefusal):
            registry.run_worker_cleanup(authorization, 3)

    def test_effect_failure_revokes_later_effect_and_retains_charge_through_stop(self) -> None:
        worker = object()

        def effects(label, ordinal):
            def fixed():
                if ordinal == 1:
                    raise EffectFault()
                return ordinal
            return fixed

        fixture = build_fixture(
            command_schedule_provider=lambda kind: (WorkerCommandSpec("two-effects", (1, 2)),),
            assigned_worker_provider=lambda serial: worker,
            effect_provider=effects,
        )
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        authorization = registry.dispatch_worker(lease)
        fixture["task"][0] = worker
        registry.dequeue_worker(lease, authorization)
        with self.assertRaises(EffectFault):
            registry.worker_issuer.run_effect(authorization, 1)
        self.assertEqual((frozenset(), frozenset()), registry.worker_ordinals(authorization))
        self.assertEqual(EffectKnowledge.BEGUN_UNCERTAIN, registry.worker_effect_knowledge(authorization))
        self.assertEqual(1, fixture["coordinator"].count())
        stop = registry.setup_reference_worker_stop(authorization)
        registry.observe_worker_stopped(stop)
        registry.complete_contained(lease)
        self.assertEqual(0, fixture["coordinator"].count())

    def test_body_cleanup_and_cancel_cleanup_have_one_primary_receipt(self) -> None:
        for winner in ("body", "cleanup", "cancel"):
            with self.subTest(winner=winner):
                worker = object()

                def cleanup(label, step_number):
                    def fixed():
                        raise EffectFault()
                    return fixed

                fixture = build_fixture(
                    command_schedule_provider=lambda kind: (
                        WorkerCommandSpec("cleanup", (1,), cleanup_steps=1),
                    ),
                    assigned_worker_provider=lambda serial: worker,
                    cleanup_provider=cleanup,
                )
                registry = fixture["registry"]
                caller = fixture["task"][0]
                lease = registry.acquire(
                    fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
                    fixture["context"], resource=fixture["connection"], owner=caller,
                )
                authorization = registry.dispatch_worker(lease)
                fixture["task"][0] = worker
                registry.dequeue_worker(lease, authorization)
                registry.worker_issuer.run_effect(authorization, 1)
                if winner == "body":
                    failure = registry.setup_reference_worker_failure(authorization)
                    primary = registry.worker_exit_failure(authorization, failure)
                elif winner == "cancel":
                    fixture["task"][0] = caller
                    primary = registry.request_worker_cancel(lease)
                    fixture["task"][0] = worker
                else:
                    primary = None
                with self.assertRaises(EffectFault):
                    registry.run_worker_cleanup(authorization, 1)
                kind, receipt, diagnostic_count, cancel_diagnostic = registry.worker_exit_facts(authorization)
                if winner == "cleanup":
                    self.assertIs(WorkerExitKind.FAILURE, kind)
                    self.assertIsNotNone(receipt)
                    self.assertEqual(0, diagnostic_count)
                else:
                    self.assertIs(primary, receipt)
                    self.assertEqual(1, diagnostic_count)
                    self.assertFalse(cancel_diagnostic)

    def test_first_and_later_queued_removal_have_distinct_terminal_outcomes(self) -> None:
        fixture = build_fixture(
            command_schedule_provider=lambda kind: (
                WorkerCommandSpec("first", (1,)),
                WorkerCommandSpec("second", (1,)),
            ),
        )
        registry = fixture["registry"]
        owner = fixture["task"][0]
        first_lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        registry.dispatch_worker(first_lease)
        registry.request_worker_cancel(first_lease)
        self.assertEqual(LeaseState.CANCELLED_CONFIRMED, registry.lease_state(first_lease))

        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        first = registry.dispatch_worker(lease)
        registry.dequeue_worker(lease, first)
        registry.worker_issuer.run_effect(first, 1)
        result = registry.setup_reference_worker_result(first, "first")
        receipt = registry.worker_exit_success(first, result)
        stop = registry.setup_reference_worker_stop(first)
        registry.observe_worker_stopped(stop)
        registry.accept_worker_result(receipt)
        registry.dispatch_worker(lease)
        registry.request_worker_cancel(lease)
        self.assertEqual(LeaseState.REFUSED, registry.lease_state(lease))
        self.assertEqual(0, fixture["coordinator"].count())

    def test_task_loss_at_each_prepublication_phase_never_publishes(self) -> None:
        phases = ("queued", "running", "success_pending", "quiescent", "accepted")
        for phase in phases:
            with self.subTest(phase=phase):
                fixture = build_fixture()
                registry = fixture["registry"]
                lease = registry.acquire(
                    fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
                    fixture["context"], resource=fixture["connection"], owner=fixture["task"][0],
                )
                authorization = registry.dispatch_worker(lease)
                if phase != "queued":
                    registry.dequeue_worker(lease, authorization)
                    registry.worker_issuer.run_effect(authorization, 1)
                if phase in {"success_pending", "quiescent", "accepted"}:
                    result = registry.setup_reference_worker_result(authorization, "private")
                    exit_receipt = registry.worker_exit_success(authorization, result)
                if phase in {"quiescent", "accepted"}:
                    stop = registry.setup_reference_worker_stop(authorization)
                    registry.observe_worker_stopped(stop)
                if phase == "accepted":
                    registry.accept_worker_result(exit_receipt)
                observation = registry.setup_reference_receiving_task_done(lease)
                registry.observe_receiving_task_done(observation)
                self.assertEqual(0, registry.publications)
                if registry.lease_state(lease) is LeaseState.CONTAINED:
                    command_state = registry.worker_command_state(authorization)
                    if command_state is WorkerCommandState.CONTAINED:
                        stop = registry.setup_reference_worker_stop(authorization)
                        registry.observe_worker_stopped(stop)
                    registry.complete_contained(lease)
                self.assertIn(
                    registry.lease_state(lease),
                    {LeaseState.CANCELLED_CONFIRMED, LeaseState.REFUSED},
                )

    def test_delivery_success_is_one_publication_fifo_terminal_release_commit(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        envelope = publish(fixture, registration)
        lease = fixture["registry"].dequeue_buffer(
            fixture["queue"], envelope, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        authorization = fixture["registry"].dispatch_worker(lease)
        baseline_publications = fixture["registry"].publications
        fixture["registry"].dequeue_worker(lease, authorization)
        fixture["registry"].worker_issuer.run_effect(authorization, 1)
        result = fixture["registry"].setup_reference_worker_result(authorization, "delivery")
        receipt = fixture["registry"].worker_exit_success(authorization, result)
        with self.assertRaises(ContractRefusal):
            fixture["registry"].accept_worker_result(receipt)
        self.assertEqual(baseline_publications, fixture["registry"].publications)
        stop = fixture["registry"].setup_reference_worker_stop(authorization)
        fixture["registry"].observe_worker_stopped(stop)
        fixture["registry"].accept_worker_result(receipt)
        candidate = fixture["registry"].prepare_delivery_publication(lease)
        self.assertEqual(1, fixture["coordinator"].count())
        self.assertEqual(baseline_publications, fixture["registry"].publications)
        with self.assertRaises(ContractRefusal):
            fixture["registry"].complete(lease, fixture["task"][0], LeaseState.SUCCEEDED)
        settlement = fixture["registry"].settle_delivery_success(lease, candidate)
        self.assertEqual(0, fixture["coordinator"].count())
        self.assertEqual(baseline_publications + 1, fixture["registry"].publications)
        self.assertEqual(
            (RevisionCursor(fixture["scope"], 1, 1),) * 2,
            fixture["registry"].delivery_cursors(registration),
        )
        self.assertIs(settlement, fixture["registry"].settle_delivery_success(lease, candidate))
        with self.assertRaises(ContractRefusal):
            fixture["registry"].settle_delivery_success(
                lease, object.__new__(DeliveryPublicationCandidate),
            )

    def test_failed_fifo_head_retires_successors_and_holds_active_charge_until_stop(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        first = publish(fixture, registration, revision=1)
        second = publish(fixture, registration, revision=2)
        lease = fixture["registry"].dequeue_buffer(
            fixture["queue"], first, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        authorization = fixture["registry"].dispatch_worker(lease)
        fixture["registry"].dequeue_worker(lease, authorization)
        failure = fixture["registry"].setup_reference_worker_failure(authorization)
        exit_receipt = fixture["registry"].worker_exit_failure(authorization, failure)
        retirement = fixture["registry"].begin_delivery_non_success(lease, exit_receipt)
        self.assertEqual(1, fixture["coordinator"].count())
        self.assertEqual(
            (RevisionCursor(fixture["scope"], 1, 2), RevisionCursor(fixture["scope"], 1, 0)),
            fixture["registry"].delivery_cursors(registration),
        )
        with self.assertRaises(ContractRefusal):
            fixture["registry"].dequeue_buffer(
                fixture["queue"], second, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )
        with self.assertRaises(ContractRefusal):
            fixture["registry"].settle_delivery_non_success(lease, retirement)
        stop = fixture["registry"].setup_reference_worker_stop(authorization)
        fixture["registry"].observe_worker_stopped(stop)
        delivery_stop = fixture["registry"].setup_reference_delivery_stop(retirement)
        fixture["registry"].observe_delivery_stopped(retirement, delivery_stop)
        self.assertIsInstance(
            fixture["registry"].settle_delivery_non_success(lease, retirement),
            RefetchRequired,
        )
        self.assertEqual(0, fixture["coordinator"].count())
        self.assertEqual(RevisionCursor(fixture["scope"], 1, 0), fixture["registry"].delivery_cursors(registration)[1])

    def test_receiver_loss_after_publication_ready_routes_to_delivery_retirement(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        envelope = publish(fixture, registration)
        successor = publish(fixture, registration, revision=2)
        baseline_publications = fixture["registry"].publications
        lease = fixture["registry"].dequeue_buffer(
            fixture["queue"], envelope, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        authorization = fixture["registry"].dispatch_worker(lease)
        fixture["registry"].dequeue_worker(lease, authorization)
        fixture["registry"].worker_issuer.run_effect(authorization, 1)
        result = fixture["registry"].setup_reference_worker_result(authorization, "delivery")
        exit_receipt = fixture["registry"].worker_exit_success(authorization, result)
        stop = fixture["registry"].setup_reference_worker_stop(authorization)
        fixture["registry"].observe_worker_stopped(stop)
        fixture["registry"].accept_worker_result(exit_receipt)
        candidate = fixture["registry"].prepare_delivery_publication(lease)
        observation = fixture["registry"].setup_reference_receiving_task_done(lease)
        fixture["registry"].observe_receiving_task_done(observation)
        retirement = fixture["registry"].begin_delivery_non_success(lease, observation)
        self.assertEqual(baseline_publications, fixture["registry"].publications)
        self.assertEqual(1, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            fixture["registry"].dequeue_buffer(
                fixture["queue"], successor, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )
        with self.assertRaises(ContractRefusal):
            fixture["registry"].settle_delivery_success(lease, candidate)
        delivery_stop = fixture["registry"].setup_reference_delivery_stop(retirement)
        fixture["registry"].observe_delivery_stopped(retirement, delivery_stop)
        fixture["registry"].settle_delivery_non_success(lease, retirement)

    def test_delivery_commit_first_cannot_be_relabelled_by_late_barriers(self) -> None:
        for late in ("receiver", "fence", "generation", "migration"):
            with self.subTest(late=late):
                fixture = make_lifetime_fixture()
                registration = register(fixture)
                envelope = publish(fixture, registration)
                registry = fixture["registry"]
                lease = registry.dequeue_buffer(
                    fixture["queue"], envelope, fixture["handle"], registration,
                    fixture["context"], fixture["task"][0],
                )
                authorization = registry.dispatch_worker(lease)
                registry.dequeue_worker(lease, authorization)
                registry.worker_issuer.run_effect(authorization, 1)
                result = registry.setup_reference_worker_result(authorization, "delivery")
                exit_receipt = registry.worker_exit_success(authorization, result)
                stop = registry.setup_reference_worker_stop(authorization)
                registry.observe_worker_stopped(stop)
                registry.accept_worker_result(exit_receipt)
                observation = registry.setup_reference_receiving_task_done(lease)
                candidate = registry.prepare_delivery_publication(lease)
                settlement = registry.settle_delivery_success(lease, candidate)
                if late == "receiver":
                    registry.observe_receiving_task_done(observation)
                elif late == "fence":
                    registry.start_close(fixture["subscription"], hard=True)
                elif late == "generation":
                    registry.revoke_generation()
                else:
                    attempt = fixture["coordinator"].begin_drain(fixture["binding"])
                    registry.migration_queue_barrier(attempt)
                self.assertEqual(LeaseState.SUCCEEDED, registry.lease_state(lease))
                self.assertEqual(0, fixture["coordinator"].count())
                self.assertIs(settlement, registry.settle_delivery_success(lease, candidate))

    def test_precommit_expiry_fence_and_migration_all_retire_the_active_head(self) -> None:
        for barrier in ("expiry", "fence", "migration"):
            with self.subTest(barrier=barrier):
                fixture = make_lifetime_fixture()
                registration = register(fixture)
                envelope = publish(fixture, registration)
                successor = publish(fixture, registration, revision=2)
                registry = fixture["registry"]
                lease = registry.dequeue_buffer(
                    fixture["queue"], envelope, fixture["handle"], registration,
                    fixture["context"], fixture["task"][0],
                )
                authorization = registry.dispatch_worker(lease)
                registry.dequeue_worker(lease, authorization)
                registry.worker_issuer.run_effect(authorization, 1)
                result = registry.setup_reference_worker_result(authorization, "delivery")
                exit_receipt = registry.worker_exit_success(authorization, result)
                stop = registry.setup_reference_worker_stop(authorization)
                registry.observe_worker_stopped(stop)
                registry.accept_worker_result(exit_receipt)
                candidate = registry.prepare_delivery_publication(lease)
                if barrier == "expiry":
                    fixture["now"][0] = 10.0
                    with self.assertRaises(ContractRefusal):
                        registry.settle_delivery_success(lease, candidate)
                    retirement = registry.begin_delivery_non_success(lease, exit_receipt)
                elif barrier == "fence":
                    registry.start_close(fixture["subscription"], hard=True)
                    retirement = registry.delivery_retirement(lease)
                else:
                    attempt = fixture["coordinator"].begin_drain(fixture["binding"])
                    registry.migration_queue_barrier(attempt)
                    retirement = registry.delivery_retirement(lease)
                self.assertEqual(1, fixture["coordinator"].count())
                with self.assertRaises(ContractRefusal):
                    registry.dequeue_buffer(
                        fixture["queue"], successor, fixture["handle"], registration,
                        fixture["context"], fixture["task"][0],
                    )
                with self.assertRaises(ContractRefusal):
                    registry.settle_delivery_success(lease, candidate)
                delivery_stop = registry.setup_reference_delivery_stop(retirement)
                registry.observe_delivery_stopped(retirement, delivery_stop)
                registry.settle_delivery_non_success(lease, retirement)
                self.assertEqual(0, fixture["coordinator"].count())

    def test_cancel_and_cleanup_failure_retire_two_range_registration(self) -> None:
        for cause in ("cancel", "cleanup"):
            with self.subTest(cause=cause):
                def cleanup(label, step_number):
                    def fixed():
                        raise EffectFault()
                    return fixed

                fixture = make_lifetime_fixture(
                    command_schedule_provider=lambda kind: (
                        WorkerCommandSpec("delivery-cleanup", (1,), cleanup_steps=1),
                    ),
                    cleanup_provider=cleanup,
                )
                registry = fixture["registry"]
                registration = register(fixture)
                first = publish(fixture, registration, revision=1)
                second = publish(fixture, registration, revision=2)
                lease = registry.dequeue_buffer(
                    fixture["queue"], first, fixture["handle"], registration,
                    fixture["context"], fixture["task"][0],
                )
                authorization = registry.dispatch_worker(lease)
                registry.dequeue_worker(lease, authorization)
                registry.worker_issuer.run_effect(authorization, 1)
                if cause == "cancel":
                    exit_receipt = registry.request_worker_cancel(lease)
                else:
                    with self.assertRaises(EffectFault):
                        registry.run_worker_cleanup(authorization, 1)
                    exit_receipt = registry.worker_exit_facts(authorization)[1]
                retirement = registry.begin_delivery_non_success(lease, exit_receipt)
                self.assertEqual(1, fixture["coordinator"].count())
                with self.assertRaises(ContractRefusal):
                    registry.dequeue_buffer(
                        fixture["queue"], second, fixture["handle"], registration,
                        fixture["context"], fixture["task"][0],
                    )
                worker_stop = registry.setup_reference_worker_stop(authorization)
                registry.observe_worker_stopped(worker_stop)
                delivery_stop = registry.setup_reference_delivery_stop(retirement)
                registry.observe_delivery_stopped(retirement, delivery_stop)
                registry.settle_delivery_non_success(lease, retirement)
                self.assertEqual(0, fixture["coordinator"].count())


class NeutralRefreshCausalTests(unittest.TestCase):
    def test_known_candidate_wrong_owner_is_retryable_without_mutation(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        lease, candidate = prepare_refresh(
            fixture, registration, 1, ({"changed": True},),
        )
        before = (
            fixture["registry"].lease_state(lease),
            fixture["coordinator"].count(),
            fixture["registry"].publications,
            fixture["registry"].current_refresh_candidates(),
        )
        self.assertIsInstance(
            fixture["registry"].publish_refresh_buffer(lease, object(), candidate),
            RefreshCommitRefused,
        )
        self.assertEqual(before, (
            fixture["registry"].lease_state(lease),
            fixture["coordinator"].count(),
            fixture["registry"].publications,
            fixture["registry"].current_refresh_candidates(),
        ))
        self.assertIsNotNone(
            fixture["registry"].publish_refresh_buffer(
                lease, fixture["task"][0], candidate,
            ),
        )

    def test_zero_queue_neutral_terminalizes_without_publication_or_buffer(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        before_publications = fixture["registry"].publications
        _, candidate = prepare_refresh(fixture, registration, 1, ())
        self.assertEqual(1, fixture["registry"].current_refresh_candidates())
        receipt = fixture["registry"].commit_refresh(candidate)
        self.assertIsInstance(receipt, NeutralRefreshReceipt)
        self.assertEqual(0, fixture["coordinator"].count())
        self.assertEqual(before_publications, fixture["registry"].publications)
        expected = RevisionCursor(fixture["scope"], 1, 1)
        self.assertEqual((expected, expected), fixture["registry"].delivery_cursors(registration))
        self.assertIs(receipt, fixture["registry"].commit_refresh(candidate))
        self.assertIs(receipt, fixture["registry"].replay_neutral(receipt))

    def test_neutral_span_cannot_overtake_changed_head_and_folds_with_success(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        changed = publish(fixture, registration, revision=1)
        for revision in range(2, 14):
            _, neutral = prepare_refresh(fixture, registration, revision, ())
            fixture["registry"].commit_refresh(neutral)
        produced, delivered = fixture["registry"].delivery_cursors(registration)
        self.assertEqual(13, produced.revision)
        self.assertEqual(0, delivered.revision)
        self.assertEqual((1, 1, 9, 9), fixture["registry"].neutral_lineage_sizes(registration))
        lease = fixture["registry"].dequeue_buffer(
            fixture["queue"], changed, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        settle_handoff(fixture, lease)
        produced, delivered = fixture["registry"].delivery_cursors(registration)
        self.assertEqual((13, 13), (produced.revision, delivered.revision))

    def test_replay_window_is_exactly_c_and_evicted_handles_are_uniformly_unavailable(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        candidates = []
        receipts = []
        for revision in range(1, 14):
            _, candidate = prepare_refresh(fixture, registration, revision, ())
            candidates.append(candidate)
            receipts.append(fixture["registry"].commit_refresh(candidate))
        changed, spans, replay, capacity = fixture["registry"].neutral_lineage_sizes(registration)
        self.assertEqual((0, 0, 9, 9), (changed, spans, replay, capacity))
        self.assertIsInstance(fixture["registry"].commit_refresh(candidates[0]), RefreshRecordUnavailable)
        self.assertIsInstance(fixture["registry"].replay_neutral(receipts[0]), RefreshRecordUnavailable)
        self.assertIs(receipts[-1], fixture["registry"].commit_refresh(candidates[-1]))
        self.assertIsInstance(fixture["registry"].commit_refresh(object()), RefreshRecordUnavailable)
        self.assertEqual(0, fixture["registry"].current_refresh_candidates())

    def test_active_plus_q_changed_entries_overflow_retires_every_successor(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        first = publish(fixture, registration, revision=1)
        active = fixture["registry"].dequeue_buffer(
            fixture["queue"], first, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        for revision in range(2, 10):
            publish(fixture, registration, revision=revision)
        self.assertEqual((9, 0, 0, 9), fixture["registry"].neutral_lineage_sizes(registration))
        refresh, candidate = prepare_refresh(fixture, registration, 10, ({"overflow": True},))
        self.assertEqual(10, fixture["coordinator"].count())
        self.assertIsInstance(fixture["registry"].commit_refresh(candidate), RefetchRequired)
        self.assertEqual(LeaseState.REFUSED, fixture["registry"].lease_state(refresh))
        self.assertEqual(1, fixture["coordinator"].count())
        retirement = fixture["registry"].delivery_retirement(active)
        stop = fixture["registry"].setup_reference_delivery_stop(retirement)
        fixture["registry"].observe_delivery_stopped(retirement, stop)
        fixture["registry"].settle_delivery_non_success(active, retirement)
        self.assertEqual(0, fixture["coordinator"].count())

    def test_changed_neutral_changed_preserves_two_exact_fifo_gaps(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        first = publish(fixture, registration, revision=1)
        _, neutral = prepare_refresh(fixture, registration, 2, ())
        fixture["registry"].commit_refresh(neutral)
        second = publish(fixture, registration, revision=3)
        first_lease = fixture["registry"].dequeue_buffer(
            fixture["queue"], first, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        settle_handoff(fixture, first_lease)
        self.assertEqual((3, 2), tuple(
            cursor.revision for cursor in fixture["registry"].delivery_cursors(registration)
        ))
        second_lease = fixture["registry"].dequeue_buffer(
            fixture["queue"], second, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        settle_handoff(fixture, second_lease)
        self.assertEqual((3, 3), tuple(
            cursor.revision for cursor in fixture["registry"].delivery_cursors(registration)
        ))

    def test_known_nonquiescent_candidate_retains_charge_until_exact_stop(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        lease, candidate = prepare_refresh(fixture, registration, 1, ())
        authorization = fixture["registry"].dispatch_worker(lease)
        fixture["registry"].dequeue_worker(lease, authorization)
        fixture["registry"].start_close(fixture["subscription"], hard=True)
        self.assertIsInstance(
            fixture["registry"].commit_refresh(candidate), RefreshContainmentPending,
        )
        self.assertEqual(1, fixture["coordinator"].count())
        stop = fixture["registry"].setup_reference_worker_stop(authorization)
        fixture["registry"].observe_worker_stopped(stop)
        result = fixture["registry"].settle_contained_refresh(lease, stop)
        self.assertIsInstance(result, RefetchRequired)
        self.assertIs(result, fixture["registry"].settle_contained_refresh(lease, stop))
        self.assertEqual(0, fixture["coordinator"].count())


class MembershipAndPhaseCausalTests(unittest.TestCase):
    def test_leave_waits_for_operation_and_unresolved_close_obligations(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        membership = registry.membership
        lease = registry.acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection_a"], owner=fixture["task"][0],
        )
        registry.start_close(fixture["runtime"])
        self.assertIs(ParticipantState.LEAVE_PENDING, fixture["coordinator"].membership_state(membership))
        transaction = TransactionIdentity(fixture["scope"], "pending")
        self.assertEqual(
            "nonquiescent",
            registry.close_outcome(fixture["runtime"], (transaction,)).knowledge.value,
        )
        registry.complete(lease, fixture["task"][0], LeaseState.REFUSED)
        self.assertEqual(
            "unresolved",
            registry.close_outcome(fixture["runtime"], (transaction,)).knowledge.value,
        )
        self.assertIs(ParticipantState.LEAVE_PENDING, fixture["coordinator"].membership_state(membership))
        registry.close_outcome(fixture["runtime"])
        self.assertIs(ParticipantState.LEFT, fixture["coordinator"].membership_state(membership))

    def test_membership_tokens_reject_copy_cross_stale_and_join_during_drain(self) -> None:
        fixture = make_lifetime_fixture()
        coordinator = fixture["coordinator"]
        membership = fixture["registry"].membership
        with self.assertRaises(TypeError):
            copy.copy(membership)
        other = make_lifetime_fixture()
        before = coordinator.membership_state(membership)
        with self.assertRaises(ContractRefusal):
            coordinator.request_leave(other["registry"].membership)
        self.assertIs(before, coordinator.membership_state(membership))
        attempt = coordinator.begin_drain(fixture["binding"])
        unjoined = ReferenceLifetimeRegistry(
            fixture["authority"], object(), coordinator,
        )
        with self.assertRaises(ContractRefusal):
            unjoined.open_lifetime()
        fixture["registry"].migration_queue_barrier(attempt)
        proof = coordinator.observe_request_released(
            attempt, coordinator.attempt_product(attempt)[3],
        )
        coordinator.reopen_no_effect(proof)
        fixture["registry"].reopen_queues_no_effect(attempt)
        fixture["registry"].start_close(fixture["runtime"])
        fixture["registry"].close_outcome(fixture["runtime"])
        self.assertIs(ParticipantState.LEFT, coordinator.membership_state(membership))
        with self.assertRaises(ContractRefusal):
            coordinator.request_leave(membership)

    def test_unjoined_runtime_has_no_admission_and_can_close_without_membership(self) -> None:
        scope = QualifiedDeployment("SALES", "PRE")
        binding = BindingIdentity(scope, "ir", "storage", 1)
        coordinator = ReferenceGenerationCoordinator(scope, binding)
        task = object()
        authority = RuntimeAuthority(lambda: 1.0, lambda: 1, lambda: task)
        context = authority.issue(TrustedClaims(
            "p", "w", scope, {Capability.QUERY}, "c", 10.0, 1,
        ))
        registry = ReferenceLifetimeRegistry(authority, object(), coordinator)
        runtime = ResourceIdentity("runtime", ResourceKind.RUNTIME)
        registry.add_resource(runtime)
        self.assertIsNone(registry.membership)
        with self.assertRaises(ContractRefusal):
            registry.setup_reference_admission(
                build_fixture()["plan"], binding,
            )
        registry.start_close(runtime)
        registry.close_outcome(runtime)
        self.assertIsNone(registry.membership)
        self.assertIs(ActivationState.UNACTIVATED, coordinator.activation)
        del context

    def test_leave_pending_stays_in_frozen_attempt_then_disappears_from_later_attempt(self) -> None:
        fixture = make_lifetime_fixture()
        membership = fixture["registry"].membership
        attempt = fixture["coordinator"].begin_drain(fixture["binding"])
        fixture["registry"].start_close(fixture["runtime"])
        self.assertIs(ParticipantState.LEAVE_PENDING, fixture["coordinator"].membership_state(membership))
        fixture["registry"].migration_queue_barrier(attempt)
        proof = fixture["coordinator"].observe_request_released(
            attempt, fixture["coordinator"].attempt_product(attempt)[3],
        )
        fixture["coordinator"].reopen_no_effect(proof)
        fixture["registry"].reopen_queues_no_effect(attempt)
        self.assertIs(ParticipantState.LEFT, fixture["coordinator"].membership_state(membership))
        later = fixture["coordinator"].begin_drain(fixture["binding"])
        state, phase, serial, request = fixture["coordinator"].attempt_product(later)
        self.assertIs(DeploymentGenerationState.DRAINING_OLD, state)
        self.assertIs(AttemptPhase.DRAINING_OLD, phase)
        self.assertEqual(1, serial)
        self.assertIsNotNone(request)

    def test_drain_proof_is_stale_in_same_attempt_pre_effect_phase(self) -> None:
        fixture = make_lifetime_fixture()
        coordinator = fixture["coordinator"]
        attempt = coordinator.begin_drain(fixture["binding"])
        fixture["registry"].migration_queue_barrier(attempt)
        draining_proof = coordinator.observe_request_released(
            attempt, coordinator.attempt_product(attempt)[3],
        )
        requested = BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2)
        coordinator.begin_migration(attempt, requested)
        state, phase, serial, _ = coordinator.attempt_product(attempt)
        self.assertEqual((DeploymentGenerationState.MIGRATING, AttemptPhase.MIGRATING_PRE_EFFECT, 2), (state, phase, serial))
        before = (coordinator.state, coordinator.binding, coordinator.admission_epoch)
        with self.assertRaises(ContractRefusal):
            coordinator.reopen_no_effect(draining_proof)
        self.assertEqual(before, (coordinator.state, coordinator.binding, coordinator.admission_epoch))
        current = coordinator.observe_request_released(
            attempt, coordinator.attempt_product(attempt)[3],
        )
        coordinator.reopen_no_effect(current)
        self.assertIs(DeploymentGenerationState.CURRENT, coordinator.state)

    def test_effect_begun_has_no_pre_effect_reopen_edge(self) -> None:
        fixture = make_lifetime_fixture()
        coordinator = fixture["coordinator"]
        attempt = coordinator.begin_drain(fixture["binding"])
        fixture["registry"].migration_queue_barrier(attempt)
        requested = BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2)
        coordinator.begin_migration(attempt, requested)
        proof = coordinator.observe_request_released(
            attempt, coordinator.attempt_product(attempt)[3],
        )
        coordinator.begin_migration_effect()
        state, phase, serial, _ = coordinator.attempt_product(attempt)
        self.assertEqual((DeploymentGenerationState.MIGRATING, AttemptPhase.EFFECT_BEGUN, 3), (state, phase, serial))
        with self.assertRaises(ContractRefusal):
            coordinator.reopen_no_effect(proof)

    def test_phase_product_and_request_identity_are_exact_at_every_stage(self) -> None:
        fixture = make_lifetime_fixture()
        coordinator = fixture["coordinator"]
        attempt = coordinator.begin_drain(fixture["binding"])
        state, phase, serial, drain_request = coordinator.attempt_product(attempt)
        self.assertEqual(
            (DeploymentGenerationState.DRAINING_OLD, AttemptPhase.DRAINING_OLD, 1),
            (state, phase, serial),
        )
        before = (state, phase, serial, drain_request, coordinator.admission_epoch)
        with self.assertRaises(ContractRefusal):
            coordinator.observe_request_released(
                attempt, object.__new__(MigrationRequestIdentity),
            )
        self.assertEqual(before, (*coordinator.attempt_product(attempt), coordinator.admission_epoch))
        fixture["registry"].migration_queue_barrier(attempt)
        requested = BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2)
        coordinator.begin_migration(attempt, requested)
        state, phase, serial, migrate_request = coordinator.attempt_product(attempt)
        self.assertEqual(
            (DeploymentGenerationState.MIGRATING, AttemptPhase.MIGRATING_PRE_EFFECT, 2),
            (state, phase, serial),
        )
        self.assertIsNot(drain_request, migrate_request)
        with self.assertRaises(ContractRefusal):
            coordinator.observe_request_released(attempt, drain_request)
        proof = coordinator.observe_request_released(attempt, migrate_request)
        coordinator.begin_migration_effect()
        self.assertEqual(
            (DeploymentGenerationState.MIGRATING, AttemptPhase.EFFECT_BEGUN, 3),
            coordinator.attempt_product(attempt)[:3],
        )
        for action in (
            lambda: coordinator.reopen_no_effect(proof),
            lambda: coordinator.observe_request_released(
                attempt, coordinator.attempt_product(attempt)[3],
            ),
        ):
            with self.assertRaises(ContractRefusal):
                action()


if __name__ == "__main__":
    unittest.main()
