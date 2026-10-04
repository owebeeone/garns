from __future__ import annotations

import copy
import gc
import sys
import unittest
import weakref

from garns.backends.contracts.admission import LeaseState, OperationKind, PlanStep
from garns.backends.contracts.authority import RuntimeAuthority, TrustedClaims
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import (
    ActivationEvidence, ActivationState, DeploymentGenerationState,
    ResourceIdentity, ResourceKind,
)
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.migration_reference import (
    AttemptPhase, MigrationAttempt, MigrationNoEffectProof, MigrationRequestIdentity,
    ParticipantState,
)
from garns.backends.contracts.semantic import BindingIdentity
from garns.backends.contracts.snapshot_reference import NeutralRefreshReceipt
from garns.backends.contracts.values import (
    Capability, ContractRefusal, ParameterValues, QualifiedDeployment,
    RefetchRequired, RefreshCommitRefused, RefreshContainmentPending,
    RefreshRecordUnavailable, RefusalCode, RevisionCursor, TransactionIdentity,
)
from garns.backends.contracts.worker_authority import (
    DeliveryPublicationCandidate, EffectKnowledge,
    ReceivingTaskLifecycleObservation, WorkerCommandSpec, WorkerCommandState,
    WorkerExitKind, WorkerExitReceipt,
)
from garns.backends.contracts.admission import OperationIdentity
from garns.backends.contracts.lifetime import BufferedDelivery, SharedGenerationCoordinator
from garns.backends.contracts.recovery import (
    ActivationUnusedWithdrawalProof, MigrationRecoveryKind, MigrationRecoveryProof,
)
from tests.contracts.test_admission_contracts import build_fixture, run_command
from tests.contracts.test_contract_source_rules import (
    COORDINATOR_ATTRIBUTES, COORDINATOR_METHODS, MEMBERSHIP_AND_PROOF_METHODS,
)
from tests.contracts.test_lifetime_contracts import (
    make_lifetime_fixture, publish, register, settle_handoff, step,
)


class EffectFault(BaseException):
    pass


def prepare_refresh(fixture, registration, revision, rows, *, worker=True):
    registry = fixture["registry"]
    owner = fixture["task"][0]
    lease = registry.acquire(
        fixture["handle"], OperationKind.REFRESH,
        ParameterValues({"tenant": "a"}), fixture["context"],
        resource=fixture["subscription"], owner=owner,
    )
    for plan_step in (PlanStep.FETCH, PlanStep.ASSEMBLY, PlanStep.CURSOR_ADVANCE):
        step(fixture, lease, plan_step)
    if worker:
        run_command(fixture, lease, rows)
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
        # Design §4.1: queue removal is QUEUE_REMOVED(exit_receipt); the CANCEL
        # receipt is returned and exact replay returns the identical receipt.
        self.assertIsInstance(observed, WorkerExitReceipt)
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
                    # Design §8: the registry-detected barrier failure begins
                    # phase one itself; a SUCCESS receipt is never a cause.
                    with self.assertRaises(ContractRefusal):
                        registry.begin_delivery_non_success(lease, exit_receipt)
                    retirement = registry.delivery_retirement(lease)
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

                def schedule(kind):
                    # The hostile cleanup step belongs to the delivery command
                    # only; registration and refresh drive the default slot.
                    if kind is OperationKind.ITERATOR_HANDOFF:
                        return (WorkerCommandSpec("delivery-cleanup", (1,), cleanup_steps=1),)
                    return (WorkerCommandSpec(f"{kind.value}-command", (1,)),)

                fixture = make_lifetime_fixture(
                    command_schedule_provider=schedule,
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
        self.assertIsInstance(
            fixture["registry"].publish_refresh_buffer(
                lease, fixture["task"][0], candidate,
            ),
            BufferedDelivery,
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
        lease, candidate = prepare_refresh(fixture, registration, 1, (), worker=False)
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
        # Design §9: close during the frozen attempt reports CLOSED while the
        # member stays LEAVE_PENDING; only attempt close makes it LEFT.
        self.assertEqual("closed", fixture["registry"].close_outcome(fixture["runtime"]).knowledge.value)
        self.assertIs(ParticipantState.LEAVE_PENDING, fixture["coordinator"].membership_state(membership))
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


# ---------------------------------------------------------------------------
# Correction 1 closure tests (RemPlan IR1-IR19).  Every refusal below asserts
# the unchanged-state vector through the registry's closed observers only.
# ---------------------------------------------------------------------------


def vector(registry, lease, authorization=None, *, coordinator=None, registration=None):
    """Closed unchanged-state vector: lease facts, publications, counts,
    command facts and lineage; identities are never read."""

    facts = [registry.lease_facts(lease), registry.publications]
    if coordinator is not None:
        facts.append(coordinator.count())
    if authorization is not None:
        facts.extend((
            registry.worker_command_state(authorization),
            registry.worker_ordinals(authorization),
            registry.worker_exit_facts(authorization),
            registry.worker_effect_knowledge(authorization),
            registry.worker_cleanup_step(authorization),
        ))
    if registration is not None:
        facts.extend((
            registry.delivery_cursors(registration),
            registry.neutral_lineage_sizes(registration),
            registry.current_refresh_candidates(),
        ))
    return tuple(facts)


def two_slot_schedule(kind):
    return (WorkerCommandSpec(f"{kind.value}-c1", (1,)), WorkerCommandSpec(f"{kind.value}-c2", (1,)))


def drive_to(fixture, lease, stage, *, worker=None):
    """Bring the active command to `stage` and return its authorization.

    Stages: queued, running_idle, success_pending, quiescent_success,
    accepted.  With a distinct `worker`, the worker task performs dequeue,
    effect and exit and the receiver task is restored afterwards.
    """

    registry = fixture["registry"]
    receiver = fixture["task"][0]
    authorization = registry.dispatch_worker(lease)
    if stage == "queued":
        return authorization
    if worker is not None:
        fixture["task"][0] = worker
    registry.dequeue_worker(lease, authorization)
    if stage == "running_idle":
        fixture["task"][0] = receiver
        return authorization
    registry.worker_issuer.run_effect(authorization, 1)
    result = registry.setup_reference_worker_result(authorization, "value")
    receipt = registry.worker_exit_success(authorization, result)
    if stage == "success_pending":
        fixture["task"][0] = receiver
        return authorization
    stop = registry.setup_reference_worker_stop(authorization)
    registry.observe_worker_stopped(stop)
    fixture["task"][0] = receiver
    if stage == "quiescent_success":
        return authorization
    registry.accept_worker_result(receipt)
    return authorization


class PublicationPreconditionTests(unittest.TestCase):
    """IR1 and IR2: one publication precondition on every non-delivery
    terminal success, and atomic registration."""

    STAGES = ("zero", "queued", "running_idle", "success_pending", "quiescent_success")

    def prepare(self, kind, *, worker_mode, two_slots=False, effect_provider=None):
        """Return (fixture, lease, worker, attempt, registration, succeed).

        `attempt` performs the kind's publication entry and raises
        ContractRefusal when it refuses (typed refresh refusals are asserted
        then re-raised uniformly); `succeed` performs it expecting success.
        The two-slot schedule and the distinct worker apply only to the kind
        under test; the registration a refresh needs runs its default slot.
        """

        target = OperationKind.REFRESH if kind in {"neutral", "changed"} else kind
        options = {}
        if two_slots:
            options["command_schedule_provider"] = lambda k: (
                two_slot_schedule(k) if k is target else (WorkerCommandSpec(f"{k.value}-command", (1,)),)
            )
        if effect_provider is not None:
            options["effect_provider"] = effect_provider
        worker = None
        switch = {"distinct": False}
        holder = {}
        if worker_mode == "distinct":
            worker = object()
            options["assigned_worker_provider"] = (
                lambda serial: worker if switch["distinct"] else holder["fixture"]["task"][0]
            )
        if kind in {OperationKind.EXECUTE, OperationKind.CONSISTENT_SNAPSHOT}:
            fixture = build_fixture(**options)
            holder["fixture"] = fixture
            switch["distinct"] = True
            lease = fixture["registry"].acquire(
                fixture["handle"], kind, ParameterValues({}), fixture["context"],
                resource=fixture["connection"], owner=fixture["task"][0],
            )
            step(fixture, lease, PlanStep.LOWER)

            def attempt():
                return fixture["registry"].run_plan_step(
                    lease, PlanStep.PUBLICATION, fixture["task"][0],
                    fixture["registry"].issue_consumer("publish"),
                )

            return fixture, lease, worker, attempt, None, attempt
        fixture = make_lifetime_fixture(**options)
        holder["fixture"] = fixture
        registry = fixture["registry"]
        owner = fixture["task"][0]
        if kind is OperationKind.SNAPSHOT_REGISTRATION:
            switch["distinct"] = True
            lease = registry.acquire(
                fixture["handle"], kind, ParameterValues({"tenant": "a"}), fixture["context"],
                resource=fixture["subscription"], owner=owner,
            )
            step(fixture, lease, PlanStep.FETCH)
            step(fixture, lease, PlanStep.SNAPSHOT_WATERMARK)
            candidate = registry.setup_reference_initial_snapshot(
                lease, owner, fixture["subscription"], fixture["queue"], ({"initial": True},),
                RevisionCursor(fixture["scope"], 1, 0),
            )
            step(fixture, lease, PlanStep.REGISTRATION)
            step(fixture, lease, PlanStep.ASSEMBLY)

            def attempt():
                return registry.register_subscription(lease, fixture["task"][0], candidate)

            return fixture, lease, worker, attempt, None, attempt
        registration = register(fixture)
        switch["distinct"] = True
        rows = () if kind == "neutral" else ({"changed": True},)
        lease = registry.acquire(
            fixture["handle"], OperationKind.REFRESH, ParameterValues({"tenant": "a"}),
            fixture["context"], resource=fixture["subscription"], owner=owner,
        )
        for plan_step in (PlanStep.FETCH, PlanStep.ASSEMBLY, PlanStep.CURSOR_ADVANCE):
            step(fixture, lease, plan_step)
        candidate = registry.setup_reference_refresh_candidate(
            lease, owner, registration,
            RevisionCursor(fixture["scope"], 1, 0), RevisionCursor(fixture["scope"], 1, 1),
            RevisionCursor(fixture["scope"], 1, 1), rows, "advance-1",
        )

        def attempt():
            refused = registry.commit_refresh(candidate)
            self.assertIsInstance(refused, RefreshCommitRefused)
            if rows:
                self.assertIsInstance(
                    registry.publish_refresh_buffer(lease, fixture["task"][0], candidate),
                    RefreshCommitRefused,
                )
            raise ContractRefusal(RefusalCode.REFRESH_COMMIT_REFUSED, "typed refusal")

        def succeed():
            result = registry.commit_refresh(candidate)
            self.assertIsInstance(result, BufferedDelivery if rows else NeutralRefreshReceipt)
            return result

        return fixture, lease, worker, attempt, registration, succeed

    def test_publication_refuses_at_every_prepublication_stage_and_succeeds_once(self) -> None:
        kinds = (
            OperationKind.EXECUTE, OperationKind.CONSISTENT_SNAPSHOT,
            OperationKind.SNAPSHOT_REGISTRATION, "neutral", "changed",
        )
        for kind in kinds:
            for worker_mode in ("default", "distinct"):
                for stage in self.STAGES:
                    with self.subTest(kind=kind, worker=worker_mode, stage=stage):
                        fixture, lease, worker, attempt, registration, _ = self.prepare(kind, worker_mode=worker_mode)
                        registry = fixture["registry"]
                        authorization = None
                        if stage != "zero":
                            authorization = drive_to(fixture, lease, stage, worker=worker)
                        before = vector(
                            registry, lease, authorization,
                            coordinator=fixture["coordinator"], registration=registration,
                        )
                        with self.assertRaises(ContractRefusal):
                            attempt()
                        self.assertEqual(before, vector(
                            registry, lease, authorization,
                            coordinator=fixture["coordinator"], registration=registration,
                        ))
                        self.assertFalse(registry.lease_state(lease).terminal)

    def test_publication_refuses_after_first_slot_of_two_and_from_inside_the_effect(self) -> None:
        for kind in (OperationKind.EXECUTE, OperationKind.SNAPSHOT_REGISTRATION, "neutral", "changed"):
            for worker_mode in ("default", "distinct"):
                with self.subTest(kind=kind, worker=worker_mode):
                    holder = {"inside": 0}

                    def effects(label, ordinal):
                        # Fixed hostile action installed at trusted setup: the
                        # publication entry is attempted from inside the effect
                        # (EFFECT_IN_FLIGHT) and must refuse without mutation.
                        def fixed():
                            if "attempt" in holder:
                                with self.assertRaises(ContractRefusal):
                                    holder["attempt"]()
                                holder["inside"] += 1
                            return ordinal
                        return fixed

                    fixture, lease, worker, attempt, registration, succeed = self.prepare(
                        kind, worker_mode=worker_mode, two_slots=True, effect_provider=effects,
                    )
                    registry = fixture["registry"]
                    coordinator = fixture["coordinator"]
                    holder["attempt"] = attempt
                    first = drive_to(fixture, lease, "accepted", worker=worker)
                    self.assertEqual(1, holder["inside"])
                    self.assertEqual(EffectKnowledge.RETURNED, registry.worker_effect_knowledge(first))
                    before = vector(registry, lease, first, coordinator=coordinator, registration=registration)
                    with self.assertRaises(ContractRefusal):
                        attempt()
                    self.assertEqual(before, vector(registry, lease, first, coordinator=coordinator, registration=registration))
                    self.assertEqual(LeaseState.RUNNING, registry.lease_state(lease))
                    second = drive_to(fixture, lease, "accepted", worker=worker)
                    self.assertIsNot(first, second)
                    self.assertEqual(2, holder["inside"])
                    del holder["attempt"]
                    publications = registry.publications
                    count = coordinator.count()
                    succeed()
                    self.assertEqual(LeaseState.SUCCEEDED, registry.lease_state(lease))
                    self.assertEqual(count if kind == "changed" else count - 1, coordinator.count())
                    self.assertEqual(publications + (0 if kind == "neutral" else 1), registry.publications)
                    if kind in {"neutral", "changed"}:
                        self.assertNotIsInstance(registry.commit_refresh(object()), BufferedDelivery)
                    else:
                        with self.assertRaises(ContractRefusal):
                            attempt()
                    self.assertEqual(LeaseState.SUCCEEDED, registry.lease_state(lease))
                    self.assertEqual(publications + (0 if kind == "neutral" else 1), registry.publications)

    def test_migration_keeps_refusing_while_a_command_can_run(self) -> None:
        fixture, lease, _, _, _, _ = self.prepare(OperationKind.EXECUTE, worker_mode="default")
        authorization = drive_to(fixture, lease, "running_idle")
        coordinator = fixture["coordinator"]
        attempt = coordinator.begin_drain(fixture["binding"])
        fixture["registry"].migration_queue_barrier(attempt)
        with self.assertRaises(ContractRefusal):
            coordinator.begin_migration(attempt, BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2))
        self.assertEqual(1, coordinator.count())
        self.assertEqual(WorkerCommandState.RUNNING_IDLE, fixture["registry"].worker_command_state(authorization))

    def test_zero_dispatch_publication_refuses_for_every_kind(self) -> None:
        for kind in (OperationKind.EXECUTE, OperationKind.CONSISTENT_SNAPSHOT, OperationKind.SNAPSHOT_REGISTRATION, "neutral", "changed"):
            with self.subTest(kind=kind):
                fixture, lease, _, attempt, registration, _ = self.prepare(kind, worker_mode="default")
                registry = fixture["registry"]
                before = vector(registry, lease, coordinator=fixture["coordinator"], registration=registration)
                self.assertEqual(0, before[0][4], "no command was dispatched")
                with self.assertRaises(ContractRefusal):
                    attempt()
                self.assertEqual(before, vector(registry, lease, coordinator=fixture["coordinator"], registration=registration))

    def test_registration_is_one_atomic_publication_terminal_release(self) -> None:
        fixture, lease, _, attempt, _, _ = self.prepare(OperationKind.SNAPSHOT_REGISTRATION, worker_mode="default")
        registry = fixture["registry"]
        coordinator = fixture["coordinator"]
        drive_to(fixture, lease, "accepted")
        published = attempt()
        self.assertEqual(LeaseState.SUCCEEDED, registry.lease_state(lease))
        self.assertEqual(0, coordinator.count())
        self.assertEqual(1, registry.publications)
        settled = vector(registry, lease, coordinator=coordinator)
        self.assertIsNone(registry.request_worker_cancel(lease))
        observation = registry.setup_reference_receiving_task_done(lease)
        self.assertIsNone(registry.observe_receiving_task_done(observation))
        registry.complete(lease, fixture["task"][0], LeaseState.SUCCEEDED)
        with self.assertRaises(ContractRefusal) as conflict:
            registry.complete(lease, fixture["task"][0], LeaseState.REFUSED)
        self.assertEqual(RefusalCode.OPERATION_OUTCOME_CONFLICT, conflict.exception.code)
        self.assertEqual(settled, vector(registry, lease, coordinator=coordinator))
        drain = coordinator.begin_drain(fixture["binding"])
        registry.migration_queue_barrier(drain)
        coordinator.begin_migration(drain, BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2))
        self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)
        self.assertEqual(
            (RevisionCursor(fixture["scope"], 1, 0),) * 2,
            registry.delivery_cursors(published.registration),
        )

    def test_registration_failure_before_commit_leaves_no_registration(self) -> None:
        fixture, lease, _, attempt, _, _ = self.prepare(OperationKind.SNAPSHOT_REGISTRATION, worker_mode="default")
        registry = fixture["registry"]
        drive_to(fixture, lease, "accepted")
        registry.start_close(fixture["queue"], hard=True)
        with self.assertRaises(ContractRefusal):
            attempt()
        self.assertEqual(0, registry.publications)
        self.assertEqual(LeaseState.CONTAINED, registry.lease_state(lease))
        self.assertEqual("containment", registry.lease_facts(lease)[2])
        self.assertEqual(1, fixture["coordinator"].count())
        registry.complete_contained(lease)
        self.assertEqual(0, fixture["coordinator"].count())


def two_range_handoff(fixture):
    """Register, publish (0,1] and (1,2], dequeue the head; return (lease, registration, successor)."""

    registration = register(fixture)
    first = publish(fixture, registration, revision=1)
    second = publish(fixture, registration, revision=2)
    lease = fixture["registry"].dequeue_buffer(
        fixture["queue"], first, fixture["handle"], registration,
        fixture["context"], fixture["task"][0],
    )
    return lease, registration, second


def settle_retirement(fixture, lease, authorization=None):
    """Exact worker stop (when a command exists) plus delivery stop, then phase two."""

    registry = fixture["registry"]
    retirement = registry.delivery_retirement(lease)
    if authorization is not None and registry.worker_command_state(authorization) is WorkerCommandState.CONTAINED:
        stop = registry.setup_reference_worker_stop(authorization)
        registry.observe_worker_stopped(stop)
    delivery_stop = registry.setup_reference_delivery_stop(retirement)
    registry.observe_delivery_stopped(retirement, delivery_stop)
    return registry.settle_delivery_non_success(lease, retirement)


class ContainmentRoutineTests(unittest.TestCase):
    """IR3, IR4, IR5 and IR12: presentation refusals never contain; every
    genuine barrier failure moves lease and command together through one
    routine; deliveries enter §8 phase one with a registry-owned cause."""

    LAZY = ("expiry", "invalidation")
    EAGER = ("epoch", "fence")

    def inject(self, fixture, cause, resource):
        if cause == "expiry":
            fixture["now"][0] = 10.0
        elif cause == "invalidation":
            fixture["authority"].invalidate(fixture["context"])
        elif cause == "epoch":
            fixture["registry"].revoke_generation()
        else:
            fixture["registry"].start_close(resource, hard=True)

    def test_wrong_task_refresh_commit_is_presentation_only(self) -> None:
        for rows in ((), ({"changed": True},)):
            with self.subTest(changed=bool(rows)):
                fixture = make_lifetime_fixture()
                registry = fixture["registry"]
                coordinator = fixture["coordinator"]
                registration = register(fixture)
                lease, candidate = prepare_refresh(fixture, registration, 1, rows)
                receiver = fixture["task"][0]
                before = vector(registry, lease, coordinator=coordinator, registration=registration)
                fixture["task"][0] = object()
                self.assertIsInstance(registry.commit_refresh(candidate), RefreshCommitRefused)
                self.assertIsInstance(registry.publish_refresh_buffer(lease, receiver, candidate), RefreshCommitRefused)
                self.assertEqual(before, vector(registry, lease, coordinator=coordinator, registration=registration))
                self.assertEqual(LeaseState.RUNNING, registry.lease_state(lease))
                fixture["task"][0] = receiver
                result = registry.commit_refresh(candidate)
                self.assertIsInstance(result, BufferedDelivery if rows else NeutralRefreshReceipt)
                self.assertEqual(LeaseState.SUCCEEDED, registry.lease_state(lease))
                if rows:
                    self.assertIsInstance(registry.commit_refresh(candidate), RefreshRecordUnavailable)
                    self.assertEqual(1, coordinator.count())
                else:
                    self.assertIs(result, registry.commit_refresh(candidate))
                    self.assertEqual(0, coordinator.count())

    def test_worker_presenting_the_current_owner_on_a_plan_step_is_refused_without_mutation(self) -> None:
        worker = object()
        fixture = build_fixture(assigned_worker_provider=lambda serial: worker)
        registry = fixture["registry"]
        receiver = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=receiver,
        )
        step(fixture, lease, PlanStep.LOWER)
        authorization = registry.dispatch_worker(lease)
        fixture["task"][0] = worker
        registry.dequeue_worker(lease, authorization)
        before = vector(registry, lease, authorization, coordinator=fixture["coordinator"])
        with self.assertRaises(ContractRefusal) as caught:
            registry.run_plan_step(lease, PlanStep.FETCH, worker, registry.issue_consumer("worker"))
        self.assertEqual(RefusalCode.CONTEXT_OWNER_MISMATCH, caught.exception.code)
        self.assertEqual(before, vector(registry, lease, authorization, coordinator=fixture["coordinator"]))
        registry.worker_issuer.run_effect(authorization, 1)
        result = registry.setup_reference_worker_result(authorization, "value")
        receipt = registry.worker_exit_success(authorization, result)
        registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization))
        fixture["task"][0] = receiver
        self.assertEqual("value", registry.accept_worker_result(receipt))
        self.assertEqual("continuation", registry.lease_facts(lease)[2])

    def contain_execute(self, stage, cause):
        fixture = build_fixture()
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        if stage != "queued":
            step(fixture, lease, PlanStep.LOWER)
        authorization = drive_to(fixture, lease, stage)
        self.inject(fixture, cause, fixture["connection"])
        if cause in self.LAZY:
            trigger = {
                "queued": lambda: registry.dequeue_worker(lease, authorization),
                "running_idle": lambda: registry.worker_issuer.run_effect(authorization, 1),
                "success_pending": lambda: (
                    registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization)),
                    registry.accept_worker_result(registry.worker_exit_facts(authorization)[1]),
                ),
                "quiescent_success": lambda: registry.accept_worker_result(registry.worker_exit_facts(authorization)[1]),
                "accepted": lambda: registry.run_plan_step(
                    lease, PlanStep.PUBLICATION, fixture["task"][0], registry.issue_consumer("publish"),
                ),
            }[stage]
            with self.assertRaises(ContractRefusal):
                trigger()
        return fixture, lease, authorization

    def test_barrier_failures_move_lease_and_command_together(self) -> None:
        for stage in ("queued", "running_idle", "success_pending", "quiescent_success", "accepted"):
            for cause in self.LAZY + self.EAGER:
                with self.subTest(stage=stage, cause=cause):
                    fixture, lease, authorization = self.contain_execute(stage, cause)
                    registry = fixture["registry"]
                    coordinator = fixture["coordinator"]
                    state = registry.lease_state(lease)
                    if stage == "queued":
                        # Authoritative queue removal is already quiescent.
                        self.assertIn(state, {LeaseState.CANCELLED_CONFIRMED, LeaseState.REFUSED})
                        self.assertEqual(0, coordinator.count())
                        continue
                    self.assertEqual(LeaseState.CONTAINED, state)
                    self.assertEqual("containment", registry.lease_facts(lease)[2])
                    self.assertEqual(0, registry.publications)
                    self.assertEqual(1, coordinator.count())
                    command = registry.worker_command_state(authorization)
                    expected = {
                        "running_idle": WorkerCommandState.CONTAINED,
                        # A lazy barrier at SUCCESS_PENDING is observed after the
                        # exact stop, so the fence lands on QUIESCENT_SUCCESS.
                        "success_pending": (
                            WorkerCommandState.QUIESCENT_CONTAINED if cause in self.LAZY
                            else WorkerCommandState.CONTAINED
                        ),
                        "quiescent_success": WorkerCommandState.QUIESCENT_CONTAINED,
                        "accepted": WorkerCommandState.RESULT_ACCEPTED,
                    }[stage]
                    self.assertIs(expected, command)
                    if stage in {"success_pending", "quiescent_success"}:
                        # No success edge out of CONTAINED: the result is closed.
                        receipt = registry.worker_exit_facts(authorization)[1]
                        with self.assertRaises(ContractRefusal):
                            registry.accept_worker_result(receipt)
                        self.assertEqual(LeaseState.CONTAINED, registry.lease_state(lease))
                    if command is WorkerCommandState.CONTAINED:
                        with self.assertRaises(ContractRefusal):
                            registry.complete_contained(lease)
                        registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization))
                    # The containment owner completes without the receiver.
                    fixture["task"][0] = object()
                    registry.complete_contained(lease)
                    self.assertEqual(LeaseState.REFUSED, registry.lease_state(lease))
                    self.assertEqual(0, coordinator.count())

    def test_barrier_inside_the_effect_contains_with_exact_knowledge(self) -> None:
        for cause in self.LAZY + self.EAGER:
            with self.subTest(cause=cause):
                holder = {}

                def effects(label, ordinal):
                    def fixed():
                        self.inject(holder["fixture"], cause, holder["fixture"]["connection"])
                        return ordinal
                    return fixed

                fixture = build_fixture(effect_provider=effects)
                holder["fixture"] = fixture
                registry = fixture["registry"]
                lease = registry.acquire(
                    fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                    resource=fixture["connection"], owner=fixture["task"][0],
                )
                authorization = drive_to(fixture, lease, "running_idle")
                if cause in self.EAGER:
                    with self.assertRaises(ContractRefusal):
                        registry.worker_issuer.run_effect(authorization, 1)
                    self.assertIs(EffectKnowledge.BEGUN_UNCERTAIN, registry.worker_effect_knowledge(authorization))
                else:
                    registry.worker_issuer.run_effect(authorization, 1)
                    result = registry.setup_reference_worker_result(authorization, "late")
                    with self.assertRaises(ContractRefusal):
                        registry.worker_exit_success(authorization, result)
                    self.assertIs(EffectKnowledge.RETURNED, registry.worker_effect_knowledge(authorization))
                self.assertEqual((LeaseState.CONTAINED, WorkerCommandState.CONTAINED), (
                    registry.lease_state(lease), registry.worker_command_state(authorization),
                ))
                self.assertEqual((frozenset(), frozenset({1})) if cause in self.LAZY else (frozenset(), frozenset()),
                                 registry.worker_ordinals(authorization))
                registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization))
                registry.complete_contained(lease)
                self.assertEqual(0, fixture["coordinator"].count())

    def test_expiry_at_dequeue_has_serial_sensitive_terminal_outcomes(self) -> None:
        fixture = build_fixture(command_schedule_provider=two_slot_schedule)
        registry = fixture["registry"]
        first = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        authorization = registry.dispatch_worker(first)
        fixture["now"][0] = 10.0
        with self.assertRaises(ContractRefusal):
            registry.dequeue_worker(first, authorization)
        self.assertEqual(LeaseState.CANCELLED_CONFIRMED, registry.lease_state(first))
        self.assertEqual(0, fixture["coordinator"].count())
        fixture["now"][0] = 1.0
        second = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        drive_to(fixture, second, "accepted")
        later = registry.dispatch_worker(second)
        fixture["now"][0] = 10.0
        with self.assertRaises(ContractRefusal):
            registry.dequeue_worker(second, later)
        self.assertEqual(LeaseState.REFUSED, registry.lease_state(second))
        self.assertEqual(0, fixture["coordinator"].count())

    def test_queue_removal_returns_a_cancel_receipt_for_every_kind(self) -> None:
        for removal in ("cancel", "task_loss"):
            with self.subTest(kind="execute-serial-1", removal=removal):
                fixture = build_fixture()
                registry = fixture["registry"]
                lease = registry.acquire(
                    fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                    resource=fixture["connection"], owner=fixture["task"][0],
                )
                registry.dispatch_worker(lease)
                if removal == "cancel":
                    receipt = registry.request_worker_cancel(lease)
                    self.assertIsNone(registry.request_worker_cancel(lease))
                else:
                    observation = registry.setup_reference_receiving_task_done(lease)
                    receipt = registry.observe_receiving_task_done(observation)
                    self.assertIs(receipt, registry.observe_receiving_task_done(observation))
                self.assertIsInstance(receipt, WorkerExitReceipt)
                self.assertEqual(LeaseState.CANCELLED_CONFIRMED, registry.lease_state(lease))
                self.assertEqual(0, fixture["coordinator"].count())
            with self.subTest(kind="execute-serial-2", removal=removal):
                fixture = build_fixture(command_schedule_provider=two_slot_schedule)
                registry = fixture["registry"]
                lease = registry.acquire(
                    fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                    resource=fixture["connection"], owner=fixture["task"][0],
                )
                drive_to(fixture, lease, "accepted")
                registry.dispatch_worker(lease)
                if removal == "cancel":
                    receipt = registry.request_worker_cancel(lease)
                else:
                    receipt = registry.observe_receiving_task_done(registry.setup_reference_receiving_task_done(lease))
                self.assertIsInstance(receipt, WorkerExitReceipt)
                self.assertEqual(LeaseState.REFUSED, registry.lease_state(lease))
                self.assertEqual(0, fixture["coordinator"].count())
            for serial in (1, 2):
                with self.subTest(kind="delivery", serial=serial, removal=removal):
                    schedule = (lambda k: two_slot_schedule(k) if k is OperationKind.ITERATOR_HANDOFF
                                else (WorkerCommandSpec(f"{k.value}-command", (1,)),))
                    fixture = make_lifetime_fixture(command_schedule_provider=schedule)
                    registry = fixture["registry"]
                    coordinator = fixture["coordinator"]
                    lease, registration, successor = two_range_handoff(fixture)
                    if serial == 2:
                        drive_to(fixture, lease, "accepted")
                    authorization = registry.dispatch_worker(lease)
                    self.assertEqual(2, coordinator.count())
                    if removal == "cancel":
                        receipt = registry.request_worker_cancel(lease)
                    else:
                        observation = registry.setup_reference_receiving_task_done(lease)
                        receipt = registry.observe_receiving_task_done(observation)
                        self.assertIs(receipt, registry.observe_receiving_task_done(observation))
                    self.assertIsInstance(receipt, WorkerExitReceipt)
                    self.assertIs(WorkerCommandState.QUEUE_REMOVED, registry.worker_command_state(authorization))
                    self.assertEqual((WorkerExitKind.CANCEL, receipt, 0, False), registry.worker_exit_facts(authorization))
                    self.assertIs(EffectKnowledge.NOT_BEGUN, registry.worker_effect_knowledge(authorization))
                    self.assertEqual(LeaseState.RETIRING_HANDOFF, registry.lease_state(lease))
                    self.assertEqual(1, coordinator.count(), "the successor permit was released exactly once")
                    retirement = registry.delivery_retirement(lease)
                    cause = receipt if removal == "cancel" else observation
                    self.assertIs(retirement, registry.begin_delivery_non_success(lease, cause))
                    with self.assertRaises(ContractRefusal):
                        registry.dequeue_buffer(
                            fixture["queue"], successor, fixture["handle"], registration,
                            fixture["context"], fixture["task"][0],
                        )
                    self.assertIsInstance(settle_retirement(fixture, lease), RefetchRequired)
                    self.assertEqual(0, coordinator.count())
                    self.assertEqual(RevisionCursor(fixture["scope"], 1, 0), registry.delivery_cursors(registration)[1])
                    self.assertEqual(LeaseState.REFUSED, registry.lease_state(lease))

    def test_registry_detected_delivery_non_success_enters_phase_one(self) -> None:
        for cause in ("expiry", "invalidation", "epoch"):
            for at in ("publication_ready", "settle"):
                if cause == "epoch" and at == "settle":
                    continue
                with self.subTest(cause=cause, at=at):
                    fixture = make_lifetime_fixture()
                    registry = fixture["registry"]
                    coordinator = fixture["coordinator"]
                    lease, registration, successor = two_range_handoff(fixture)
                    authorization = drive_to(fixture, lease, "accepted")
                    candidate = registry.prepare_delivery_publication(lease)
                    success_receipt = registry.worker_exit_facts(authorization)[1]
                    before = vector(registry, lease, authorization, coordinator=coordinator, registration=registration)
                    with self.assertRaises(ContractRefusal):
                        registry.begin_delivery_non_success(lease, success_receipt)
                    self.assertEqual(before, vector(registry, lease, authorization, coordinator=coordinator, registration=registration))
                    self.inject(fixture, cause, fixture["subscription"])
                    if at == "settle" or cause in self.LAZY:
                        with self.assertRaises(ContractRefusal):
                            registry.settle_delivery_success(lease, candidate)
                    self.assertEqual(LeaseState.RETIRING_HANDOFF, registry.lease_state(lease))
                    self.assertEqual(1, coordinator.count())
                    with self.assertRaises(ContractRefusal):
                        registry.dequeue_buffer(
                            fixture["queue"], successor, fixture["handle"], registration,
                            fixture["context"], fixture["task"][0],
                        )
                    self.assertIsInstance(settle_retirement(fixture, lease), RefetchRequired)
                    self.assertEqual(0, coordinator.count())
                    self.assertEqual(0, registry.delivery_cursors(registration)[1].revision)

    def test_hard_fence_contains_accepted_unpublished_leases(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        step(fixture, lease, PlanStep.LOWER)
        drive_to(fixture, lease, "accepted")
        self.assertEqual("continuation", registry.lease_facts(lease)[2])
        registry.start_close(fixture["connection"], hard=True)
        self.assertEqual((LeaseState.CONTAINED, "containment"), (registry.lease_state(lease), registry.lease_facts(lease)[2]))
        self.assertEqual("nonquiescent", registry.close_outcome(fixture["connection"]).knowledge.value)
        fixture["task"][0] = object()
        registry.complete_contained(lease)
        self.assertEqual(0, fixture["coordinator"].count())
        self.assertEqual("closed", registry.close_outcome(fixture["connection"]).knowledge.value)


def full_command(fixture, lease, value="value"):
    """Run the default slot to RESULT_ACCEPTED and return its artifacts."""

    registry = fixture["registry"]
    authorization = registry.dispatch_worker(lease)
    registry.dequeue_worker(lease, authorization)
    registry.worker_issuer.run_effect(authorization, 1)
    failure = registry.setup_reference_worker_failure(authorization)
    result = registry.setup_reference_worker_result(authorization, value)
    receipt = registry.worker_exit_success(authorization, result)
    stop = registry.setup_reference_worker_stop(authorization)
    registry.observe_worker_stopped(stop)
    registry.accept_worker_result(receipt)
    return {"authorization": authorization, "result": result, "failure": failure, "receipt": receipt, "stop": stop}


class TerminalAbsorptionTests(unittest.TestCase):
    """IR6: terminal leases are absorbing and a retiring handoff keeps phase two reachable."""

    def terminal_fixture(self, outcome):
        if outcome == "retired":
            fixture = make_lifetime_fixture()
            registry = fixture["registry"]
            lease, registration, _ = two_range_handoff(fixture)
            artifacts = {"authorization": registry.dispatch_worker(lease)}
            registry.dequeue_worker(lease, artifacts["authorization"])
            artifacts["failure"] = registry.setup_reference_worker_failure(artifacts["authorization"])
            artifacts["receipt"] = registry.worker_exit_failure(artifacts["authorization"], artifacts["failure"])
            artifacts["retirement"] = registry.delivery_retirement(lease)
            artifacts["stop"] = registry.setup_reference_worker_stop(artifacts["authorization"])
            registry.observe_worker_stopped(artifacts["stop"])
            delivery_stop = registry.setup_reference_delivery_stop(artifacts["retirement"])
            registry.observe_delivery_stopped(artifacts["retirement"], delivery_stop)
            registry.settle_delivery_non_success(lease, artifacts["retirement"])
            artifacts["result"] = None
            return fixture, lease, artifacts
        fixture = build_fixture()
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        if outcome == "cancelled":
            artifacts = {"authorization": registry.dispatch_worker(lease), "result": None, "stop": None}
            artifacts["failure"] = registry.setup_reference_worker_failure(artifacts["authorization"])
            artifacts["receipt"] = registry.request_worker_cancel(lease)
            return fixture, lease, artifacts
        step(fixture, lease, PlanStep.LOWER)
        artifacts = full_command(fixture, lease)
        if outcome == "succeeded":
            registry.run_plan_step(lease, PlanStep.PUBLICATION, fixture["task"][0], registry.issue_consumer("publish"))
        else:
            registry.request_worker_cancel(lease)
            registry.complete_contained(lease)
        return fixture, lease, artifacts

    def test_every_entry_leaves_a_terminal_lease_unchanged_from_every_task(self) -> None:
        expected = {
            "succeeded": LeaseState.SUCCEEDED, "refused": LeaseState.REFUSED,
            "cancelled": LeaseState.CANCELLED_CONFIRMED, "retired": LeaseState.REFUSED,
        }
        for outcome, state in expected.items():
            for caller in ("receiver", "third"):
                with self.subTest(outcome=outcome, caller=caller):
                    fixture, lease, artifacts = self.terminal_fixture(outcome)
                    registry = fixture["registry"]
                    coordinator = fixture["coordinator"]
                    receiver = fixture["task"][0]
                    self.assertEqual(state, registry.lease_state(lease))
                    settled = vector(registry, lease, coordinator=coordinator)
                    observation = registry.setup_reference_receiving_task_done(lease)
                    if caller == "third":
                        fixture["task"][0] = object()
                    authorization = artifacts["authorization"]
                    entries = [
                        lambda: registry.dequeue_worker(lease, authorization),
                        lambda: registry.worker_issuer.run_effect(authorization, 1),
                        lambda: registry.worker_exit_success(authorization, artifacts["result"]),
                        lambda: registry.worker_exit_failure(authorization, artifacts["failure"]),
                        lambda: registry.run_worker_cleanup(authorization, 1),
                        lambda: registry.worker_issuer.revoke(authorization),
                        lambda: registry.request_worker_cancel(lease),
                        lambda: registry.observe_receiving_task_done(observation),
                        lambda: registry.observe_worker_stopped(artifacts["stop"]),
                        lambda: registry.accept_worker_result(artifacts["receipt"]),
                        lambda: registry.dispatch_worker(lease),
                        lambda: registry.run_plan_step(lease, PlanStep.PUBLICATION, fixture["task"][0], registry.issue_consumer("late")),
                        lambda: registry.complete(lease, fixture["task"][0], LeaseState.REFUSED),
                        lambda: registry.complete(lease, fixture["task"][0], LeaseState.CANCELLED_CONFIRMED),
                        lambda: registry.complete_contained(lease),
                        lambda: registry.settle_delivery_success(lease, object.__new__(DeliveryPublicationCandidate)),
                        lambda: registry.begin_delivery_non_success(lease, artifacts["receipt"]),
                        lambda: registry.commit_refresh(object()),
                        lambda: registry.revoke_generation(),
                        lambda: registry.start_close(fixture["runtime"], hard=True),
                    ]
                    if outcome == "retired":
                        entries.append(lambda: registry.settle_delivery_non_success(lease, artifacts["retirement"]))
                    for index, entry in enumerate(entries):
                        try:
                            entry()
                        except ContractRefusal:
                            pass
                        self.assertEqual(settled, vector(registry, lease, coordinator=coordinator), f"entry {index}")
                    fixture["task"][0] = receiver
                    self.assertEqual(settled, vector(registry, lease, coordinator=coordinator))
                    self.assertEqual("closed", registry.close_outcome(fixture["runtime"]).knowledge.value)

    def test_retiring_handoff_survives_revocation_and_fence_until_settlement(self) -> None:
        for cause in ("failure", "receiver_loss"):
            with self.subTest(cause=cause):
                fixture = make_lifetime_fixture()
                registry = fixture["registry"]
                coordinator = fixture["coordinator"]
                lease, registration, successor = two_range_handoff(fixture)
                if cause == "failure":
                    authorization = registry.dispatch_worker(lease)
                    registry.dequeue_worker(lease, authorization)
                    registry.worker_exit_failure(authorization, registry.setup_reference_worker_failure(authorization))
                else:
                    authorization = drive_to(fixture, lease, "accepted")
                    registry.prepare_delivery_publication(lease)
                    registry.observe_receiving_task_done(registry.setup_reference_receiving_task_done(lease))
                self.assertEqual(LeaseState.RETIRING_HANDOFF, registry.lease_state(lease))
                retirement = registry.delivery_retirement(lease)
                registry.revoke_generation()
                self.assertEqual(LeaseState.RETIRING_HANDOFF, registry.lease_state(lease))
                registry.start_close(fixture["subscription"], hard=True)
                self.assertEqual(LeaseState.RETIRING_HANDOFF, registry.lease_state(lease))
                self.assertEqual("nonquiescent", registry.close_outcome(fixture["subscription"]).knowledge.value)
                self.assertEqual(1, coordinator.count())
                self.assertIsInstance(settle_retirement(fixture, lease, authorization), RefetchRequired)
                self.assertEqual(0, coordinator.count())
                self.assertEqual(0, registry.delivery_cursors(registration)[1].revision)
                self.assertEqual("closed", registry.close_outcome(fixture["subscription"]).knowledge.value)
                self.assertIsInstance(registry.settle_delivery_non_success(lease, retirement), RefetchRequired)
                self.assertEqual(0, coordinator.count())
                attempt = coordinator.begin_drain(fixture["binding"])
                registry.migration_queue_barrier(attempt)
                coordinator.begin_migration(attempt, BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2))
                self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)


class WorkerEntryValidationTests(unittest.TestCase):
    """IR7 and IR8: cleanup and later-slot dispatch validate before any mutation."""

    def cleanup_fixture(self, *, raising=False, effect_provider=None):
        worker = object()

        def cleanup(label, step_number):
            def fixed():
                if raising:
                    raise EffectFault()
            return fixed

        fixture = build_fixture(
            command_schedule_provider=lambda kind: (WorkerCommandSpec("cleanup", (1,), cleanup_steps=1),),
            assigned_worker_provider=lambda serial: worker,
            cleanup_provider=cleanup,
            effect_provider=effect_provider,
        )
        fixture["worker"] = worker
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        return fixture, lease

    def test_cleanup_refuses_before_its_containment_scope(self) -> None:
        stages = ("queued", "running_idle", "contained", "quiescent_contained", "accepted")
        for stage in stages:
            for caller in ("third", "receiver", "worker"):
                with self.subTest(stage=stage, caller=caller):
                    fixture, lease = self.cleanup_fixture()
                    registry = fixture["registry"]
                    receiver, worker = fixture["task"][0], fixture["worker"]
                    authorization = registry.dispatch_worker(lease)
                    if stage != "queued":
                        fixture["task"][0] = worker
                        registry.dequeue_worker(lease, authorization)
                        registry.worker_issuer.run_effect(authorization, 1)
                    if stage in {"contained", "quiescent_contained"}:
                        fixture["task"][0] = receiver
                        registry.request_worker_cancel(lease)
                    if stage == "quiescent_contained":
                        registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization))
                    if stage == "accepted":
                        registry.run_worker_cleanup(authorization, 1)
                        result = registry.setup_reference_worker_result(authorization, "value")
                        receipt = registry.worker_exit_success(authorization, result)
                        registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization))
                        fixture["task"][0] = receiver
                        registry.accept_worker_result(receipt)
                    fixture["task"][0] = {"third": object(), "receiver": receiver, "worker": worker}[caller]
                    legal = caller == "worker" and stage in {"running_idle", "contained"}
                    before = vector(registry, lease, authorization, coordinator=fixture["coordinator"])
                    if legal:
                        registry.run_worker_cleanup(authorization, 1)
                        self.assertEqual(2, registry.worker_cleanup_step(authorization))
                        continue
                    with self.assertRaises(ContractRefusal):
                        registry.run_worker_cleanup(authorization, 1)
                    self.assertEqual(before, vector(registry, lease, authorization, coordinator=fixture["coordinator"]))
                    if stage == "running_idle":
                        fixture["task"][0] = worker
                        registry.run_worker_cleanup(authorization, 1)
                        result = registry.setup_reference_worker_result(authorization, "value")
                        receipt = registry.worker_exit_success(authorization, result)
                        registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization))
                        fixture["task"][0] = receiver
                        self.assertEqual("value", registry.accept_worker_result(receipt))

    def test_cleanup_refuses_on_queue_removed_and_terminal_commands(self) -> None:
        schedule = (lambda k: (WorkerCommandSpec("delivery", (1,), cleanup_steps=1),)
                    if k is OperationKind.ITERATOR_HANDOFF else (WorkerCommandSpec(f"{k.value}-command", (1,)),))
        fixture = make_lifetime_fixture(command_schedule_provider=schedule)
        registry = fixture["registry"]
        lease, registration, _ = two_range_handoff(fixture)
        authorization = registry.dispatch_worker(lease)
        registry.request_worker_cancel(lease)
        self.assertIs(WorkerCommandState.QUEUE_REMOVED, registry.worker_command_state(authorization))
        before = vector(registry, lease, authorization, coordinator=fixture["coordinator"], registration=registration)
        with self.assertRaises(ContractRefusal):
            registry.run_worker_cleanup(authorization, 1)
        self.assertEqual(before, vector(registry, lease, authorization, coordinator=fixture["coordinator"], registration=registration))
        fixture, lease = self.cleanup_fixture()
        registry = fixture["registry"]
        receiver, worker = fixture["task"][0], fixture["worker"]
        authorization = registry.dispatch_worker(lease)
        fixture["task"][0] = worker
        registry.dequeue_worker(lease, authorization)
        registry.worker_issuer.run_effect(authorization, 1)
        registry.run_worker_cleanup(authorization, 1)
        receipt = registry.worker_exit_success(authorization, registry.setup_reference_worker_result(authorization, "v"))
        registry.observe_worker_stopped(registry.setup_reference_worker_stop(authorization))
        fixture["task"][0] = receiver
        registry.accept_worker_result(receipt)
        step(fixture, lease, PlanStep.LOWER)
        registry.run_plan_step(lease, PlanStep.PUBLICATION, receiver, registry.issue_consumer("publish"))
        settled = vector(registry, lease, coordinator=fixture["coordinator"])
        fixture["task"][0] = worker
        with self.assertRaises(ContractRefusal):
            registry.run_worker_cleanup(authorization, 1)
        self.assertEqual(settled, vector(registry, lease, coordinator=fixture["coordinator"]))

    def test_reentrant_cleanup_inside_an_effect_refuses_and_the_effect_returns(self) -> None:
        holder = {}

        def effects(label, ordinal):
            def fixed():
                with self.assertRaises(ContractRefusal):
                    holder["registry"].run_worker_cleanup(holder["authorization"], 1)
                return ordinal
            return fixed

        fixture, lease = self.cleanup_fixture(effect_provider=effects)
        registry = fixture["registry"]
        holder["registry"] = registry
        holder["authorization"] = registry.dispatch_worker(lease)
        fixture["task"][0] = fixture["worker"]
        registry.dequeue_worker(lease, holder["authorization"])
        self.assertEqual(1, registry.worker_issuer.run_effect(holder["authorization"], 1))
        self.assertIs(EffectKnowledge.RETURNED, registry.worker_effect_knowledge(holder["authorization"]))
        self.assertEqual((frozenset(), frozenset({1})), registry.worker_ordinals(holder["authorization"]))
        self.assertEqual(1, registry.worker_cleanup_step(holder["authorization"]))
        self.assertIs(WorkerCommandState.RUNNING_IDLE, registry.worker_command_state(holder["authorization"]))

    def test_cleanup_primary_derives_effect_knowledge_from_reservation_history(self) -> None:
        for history in ("none", "returned", "effect_raised"):
            with self.subTest(history=history):
                def effects(label, ordinal):
                    def fixed():
                        if history == "effect_raised":
                            raise EffectFault()
                        return ordinal
                    return fixed

                fixture, lease = self.cleanup_fixture(raising=True, effect_provider=effects)
                registry = fixture["registry"]
                authorization = registry.dispatch_worker(lease)
                fixture["task"][0] = fixture["worker"]
                registry.dequeue_worker(lease, authorization)
                if history == "returned":
                    registry.worker_issuer.run_effect(authorization, 1)
                elif history == "effect_raised":
                    with self.assertRaises(EffectFault):
                        registry.worker_issuer.run_effect(authorization, 1)
                    primary = registry.worker_exit_facts(authorization)[1]
                with self.assertRaises(EffectFault):
                    registry.run_worker_cleanup(authorization, 1)
                kind, receipt, diagnostics, _ = registry.worker_exit_facts(authorization)
                self.assertIs(WorkerExitKind.FAILURE, kind)
                if history == "effect_raised":
                    self.assertIs(primary, receipt)
                    self.assertEqual(1, diagnostics)
                    self.assertIs(EffectKnowledge.BEGUN_UNCERTAIN, registry.worker_effect_knowledge(authorization))
                else:
                    self.assertEqual(0, diagnostics)
                    self.assertIs(
                        EffectKnowledge.RETURNED if history == "returned" else EffectKnowledge.NOT_BEGUN,
                        registry.worker_effect_knowledge(authorization),
                    )
                self.assertEqual(2, registry.worker_cleanup_step(authorization))

    def test_later_slot_dispatch_validates_the_outer_lease(self) -> None:
        fixture = build_fixture(command_schedule_provider=two_slot_schedule)
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        first = drive_to(fixture, lease, "accepted")
        registry.request_worker_cancel(lease)
        self.assertEqual((LeaseState.CONTAINED, "containment"), (registry.lease_state(lease), registry.lease_facts(lease)[2]))
        before = vector(registry, lease, first, coordinator=fixture["coordinator"])
        with self.assertRaises(ContractRefusal):
            registry.dispatch_worker(lease)
        self.assertEqual(before, vector(registry, lease, first, coordinator=fixture["coordinator"]))
        registry.complete_contained(lease)
        self.assertEqual((LeaseState.REFUSED, 0, 0), (registry.lease_state(lease), fixture["coordinator"].count(), registry.publications))

        fixture = build_fixture(command_schedule_provider=two_slot_schedule)
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        step(fixture, lease, PlanStep.LOWER)
        drive_to(fixture, lease, "accepted")
        second = registry.dispatch_worker(lease)
        self.assertEqual(LeaseState.RUNNING, registry.lease_state(lease))
        self.assertIs(WorkerCommandState.QUEUED, registry.worker_command_state(second))
        self.assertEqual("command", registry.lease_facts(lease)[2])

    def test_retired_delivery_never_dispatches_a_later_slot(self) -> None:
        for retire_by in ("migration", "close", "fence", "overflow", "receiver_loss"):
            with self.subTest(retire_by=retire_by):
                schedule = (lambda k: two_slot_schedule(k) if k is OperationKind.ITERATOR_HANDOFF
                            else (WorkerCommandSpec(f"{k.value}-command", (1,)),))
                fixture = make_lifetime_fixture(command_schedule_provider=schedule)
                registry = fixture["registry"]
                coordinator = fixture["coordinator"]
                lease, registration, _ = two_range_handoff(fixture)
                first = drive_to(fixture, lease, "accepted")
                attempt = None
                if retire_by == "migration":
                    attempt = coordinator.begin_drain(fixture["binding"])
                    registry.migration_queue_barrier(attempt)
                elif retire_by == "close":
                    registry.start_close(fixture["subscription"], hard=True)
                elif retire_by == "fence":
                    registry.start_close(fixture["queue"], hard=True)
                elif retire_by == "overflow":
                    for revision in range(3, 10):
                        publish(fixture, registration, revision=revision)
                    _, overflow = prepare_refresh(fixture, registration, 10, ({"overflow": True},))
                    self.assertIsInstance(registry.commit_refresh(overflow), RefetchRequired)
                else:
                    registry.observe_receiving_task_done(registry.setup_reference_receiving_task_done(lease))
                self.assertEqual(LeaseState.RETIRING_HANDOFF, registry.lease_state(lease))
                before = vector(registry, lease, first, coordinator=coordinator, registration=registration)
                with self.assertRaises(ContractRefusal):
                    registry.dispatch_worker(lease)
                self.assertEqual(before, vector(registry, lease, first, coordinator=coordinator, registration=registration))
                self.assertIsInstance(settle_retirement(fixture, lease), RefetchRequired)
                self.assertEqual(0, coordinator.count())
                if attempt is None:
                    attempt = coordinator.begin_drain(fixture["binding"])
                    registry.migration_queue_barrier(attempt)
                coordinator.begin_migration(attempt, BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2))
                self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)


def join_peer(fixture, name="peer"):
    """A second participant on the fixture's coordinator with its own runtime."""

    registry = ReferenceLifetimeRegistry(fixture["authority"], object(), fixture["coordinator"])
    registry.open_lifetime()
    registry.add_resource(ResourceIdentity(f"{name}-runtime", ResourceKind.RUNTIME))
    return registry


class MembershipLeaveTests(unittest.TestCase):
    """IR9: leave is one registry-witnessed transition bound to every retained
    obligation; IR14: the first join performs the activation edge."""

    def test_unresolved_runtime_stays_leave_pending_across_reopen_recovery_and_cutover(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        coordinator = fixture["coordinator"]
        membership = registry.membership
        lease = registry.acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection_a"], owner=fixture["task"][0],
        )
        registry.start_close(fixture["runtime"])
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))
        transaction = TransactionIdentity(fixture["scope"], "pending")
        self.assertEqual("nonquiescent", registry.close_outcome(fixture["runtime"], (transaction,)).knowledge.value)
        registry.complete(lease, fixture["task"][0], LeaseState.REFUSED)
        self.assertEqual("unresolved", registry.close_outcome(fixture["runtime"], (transaction,)).knowledge.value)
        requested = BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2)

        attempt = coordinator.begin_drain(fixture["binding"])
        registry.migration_queue_barrier(attempt)
        coordinator.reopen_no_effect(coordinator.observe_request_released(attempt, coordinator.attempt_product(attempt)[3]))
        registry.reopen_queues_no_effect(attempt)
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))

        attempt = coordinator.begin_drain(fixture["binding"])
        registry.migration_queue_barrier(attempt)
        coordinator.begin_migration(attempt, requested)
        coordinator.begin_migration_effect()
        coordinator.mark_indeterminate()
        coordinator.recover_migration(MigrationRecoveryProof(
            MigrationRecoveryKind.FULL_ROLLBACK_NO_EFFECT, fixture["scope"], fixture["binding"], requested, 5, attempt,
            "outcome", "binding", "accounting",
        ))
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))

        attempt = coordinator.begin_drain(fixture["binding"])
        registry.migration_queue_barrier(attempt)
        coordinator.begin_migration(attempt, requested)
        coordinator.begin_migration_effect()
        coordinator.publish_generation(requested)
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))

        self.assertEqual("unresolved", registry.close_outcome(fixture["runtime"], (transaction,)).knowledge.value)
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))
        self.assertEqual("closed", registry.close_outcome(fixture["runtime"]).knowledge.value)
        self.assertIs(ParticipantState.LEFT, coordinator.membership_state(membership))
        later = coordinator.begin_drain(coordinator.binding)
        with self.assertRaises(ContractRefusal):
            registry.migration_queue_barrier(later)
        self.assertEqual(0, coordinator.count())

    def test_direct_leave_and_finalize_refuse_until_the_registry_witnesses_close(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        coordinator = fixture["coordinator"]
        membership = registry.membership
        registration = register(fixture)
        publish(fixture, registration)
        self.assertEqual(1, coordinator.count())
        for attempt in (lambda: coordinator.request_leave(membership), lambda: coordinator.finalize_leave(membership)):
            with self.assertRaises(ContractRefusal):
                attempt()
            self.assertIs(ParticipantState.JOINED, coordinator.membership_state(membership))
            self.assertEqual(1, coordinator.count())
            self.assertEqual((1, 0, 0, 9), registry.neutral_lineage_sizes(registration))
        registry.start_close(fixture["runtime"])
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))
        with self.assertRaises(ContractRefusal):
            coordinator.finalize_leave(membership)
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))
        self.assertEqual("closed", registry.close_outcome(fixture["runtime"]).knowledge.value)
        self.assertIs(ParticipantState.LEFT, coordinator.membership_state(membership))
        self.assertEqual(0, coordinator.count())
        with self.assertRaises(ContractRefusal):
            registry.setup_reference_admission(fixture["live_plan"], fixture["binding"])
        with self.assertRaises(ContractRefusal):
            registry.acquire(
                fixture["handle"], OperationKind.REFRESH, ParameterValues({"tenant": "a"}),
                fixture["context"], resource=fixture["subscription"], owner=fixture["task"][0],
            )
        with self.assertRaises(ContractRefusal):
            coordinator.acquire_shared(OperationIdentity(object(), 99, fixture["scope"], 1), object(), membership)
        envelope = BufferedDelivery(
            fixture["scope"], 1, fixture["handle"], "digest", RevisionCursor(fixture["scope"], 1, 0),
            RevisionCursor(fixture["scope"], 1, 1), RevisionCursor(fixture["scope"], 1, 1), (), "advance",
        )
        with self.assertRaises(ContractRefusal):
            coordinator.add_buffer(envelope, object(), membership)
        self.assertEqual(0, coordinator.count())
        registry.start_close(fixture["runtime"])
        registry.start_close(fixture["runtime"], hard=True)
        self.assertEqual("closed", registry.close_outcome(fixture["runtime"]).knowledge.value)

    def test_close_during_attempt_reports_closed_and_the_member_leaves_after_the_attempt(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        coordinator = fixture["coordinator"]
        membership = registry.membership
        peer = join_peer(fixture)
        attempt = coordinator.begin_drain(fixture["binding"])
        registry.start_close(fixture["runtime"])
        registry.migration_queue_barrier(attempt)
        peer.migration_queue_barrier(attempt)
        self.assertEqual("closed", registry.close_outcome(fixture["runtime"]).knowledge.value)
        self.assertIs(ParticipantState.LEAVE_PENDING, coordinator.membership_state(membership))
        registry.start_close(fixture["runtime"])
        self.assertEqual("closed", registry.close_outcome(fixture["runtime"]).knowledge.value)
        coordinator.reopen_no_effect(coordinator.observe_request_released(attempt, coordinator.attempt_product(attempt)[3]))
        self.assertIs(ParticipantState.LEFT, coordinator.membership_state(membership))
        later = coordinator.begin_drain(fixture["binding"])
        with self.assertRaises(ContractRefusal):
            registry.migration_queue_barrier(later)
        peer.migration_queue_barrier(later)
        coordinator.begin_migration(later, BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2))
        self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)

    def test_first_join_activates_and_withdrawal_stays_available_until_then(self) -> None:
        def unused_coordinator():
            scope = QualifiedDeployment("SALES", "FIRST")
            binding = BindingIdentity(scope, "ir", "storage", 1)
            coordinator = ReferenceGenerationCoordinator(scope, binding)
            coordinator.begin_activation(5)
            coordinator.finish_activation(ActivationEvidence(
                scope, binding, 5, "inventory", "physical", "record", "plan_admission_lifetime_v1",
            ))
            return scope, binding, coordinator

        scope, binding, coordinator = unused_coordinator()
        coordinator.first_lifetime_open("plan_admission_lifetime_v1", 5)
        self.assertIs(ActivationState.ACTIVE_UNUSED, coordinator.activation)
        coordinator.withdraw_unused(ActivationUnusedWithdrawalProof(
            scope, binding, 5, "physical", "never-open", "withdrawn", "legacy-restored",
        ))
        self.assertIs(ActivationState.UNACTIVATED, coordinator.activation)

        scope, binding, coordinator = unused_coordinator()
        authority = RuntimeAuthority(lambda: 1.0, lambda: 1, lambda: object())
        unhandshaken = ReferenceLifetimeRegistry(authority, object(), coordinator)
        with self.assertRaises(ContractRefusal):
            unhandshaken.open_lifetime()
        self.assertIs(ActivationState.ACTIVE_UNUSED, coordinator.activation)
        coordinator.first_lifetime_open("plan_admission_lifetime_v1", 5)
        first = ReferenceLifetimeRegistry(authority, object(), coordinator)
        first.open_lifetime()
        self.assertIs(ActivationState.ACTIVE, coordinator.activation)
        self.assertIs(ParticipantState.JOINED, coordinator.membership_state(first.membership))
        with self.assertRaises(ContractRefusal):
            coordinator.withdraw_unused(ActivationUnusedWithdrawalProof(
                scope, binding, 5, "physical", "never-open", "withdrawn", "legacy-restored",
            ))
        second = ReferenceLifetimeRegistry(authority, object(), coordinator)
        second.open_lifetime()
        self.assertIs(ParticipantState.JOINED, coordinator.membership_state(second.membership))


class CoordinatorProtocolTests(unittest.TestCase):
    """IR10: the formal seam declares the membership and proof members."""

    def test_reference_coordinator_conforms_and_partial_stubs_do_not(self) -> None:
        fixture = make_lifetime_fixture()
        self.assertIsInstance(fixture["coordinator"], SharedGenerationCoordinator)
        namespace = {name: None for name in COORDINATOR_ATTRIBUTES}
        namespace.update({name: (lambda self, *args, **kwargs: None) for name in COORDINATOR_METHODS})
        complete = type("CompleteStub", (), dict(namespace))
        self.assertIsInstance(complete(), SharedGenerationCoordinator)
        for missing in MEMBERSHIP_AND_PROOF_METHODS:
            with self.subTest(missing=missing):
                partial = type("PartialStub", (), {name: value for name, value in namespace.items() if name != missing})
                self.assertNotIsInstance(partial(), SharedGenerationCoordinator)
                with self.assertRaises(TypeError):
                    ReferenceLifetimeRegistry(fixture["authority"], object(), partial())


class RefreshDispositionTests(unittest.TestCase):
    """IR11: every unusable known candidate receives the §10 disposition."""

    def test_cursor_divergence_disposes_each_later_commit(self) -> None:
        for order in (("neutral", "changed", "neutral"), ("changed", "neutral")):
            with self.subTest(order=order):
                fixture = make_lifetime_fixture()
                registry = fixture["registry"]
                coordinator = fixture["coordinator"]
                registration = register(fixture)
                prepared = [
                    prepare_refresh(fixture, registration, 1, () if kind == "neutral" else ({"changed": True},))
                    for kind in order
                ]
                self.assertEqual(len(order), coordinator.count())
                first = registry.commit_refresh(prepared[0][1])
                self.assertIsInstance(first, NeutralRefreshReceipt if order[0] == "neutral" else BufferedDelivery)
                count = coordinator.count()
                for lease, candidate in prepared[1:]:
                    self.assertIsInstance(registry.commit_refresh(candidate), RefetchRequired)
                    self.assertEqual(LeaseState.REFUSED, registry.lease_state(lease))
                    count -= 1
                    self.assertEqual(count, coordinator.count())
                    self.assertIsInstance(registry.commit_refresh(candidate), RefreshRecordUnavailable)
                self.assertEqual(0, registry.current_refresh_candidates())
                attempt = coordinator.begin_drain(fixture["binding"])
                registry.migration_queue_barrier(attempt)
                coordinator.begin_migration(attempt, BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2))
                self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)

    def test_worker_backed_divergence_contains_until_the_exact_stop(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        coordinator = fixture["coordinator"]
        registration = register(fixture)
        _, first = prepare_refresh(fixture, registration, 1, ())
        stale, candidate = prepare_refresh(fixture, registration, 1, (), worker=False)
        authorization = registry.dispatch_worker(stale)
        registry.dequeue_worker(stale, authorization)
        self.assertIsInstance(registry.commit_refresh(first), NeutralRefreshReceipt)
        self.assertIsInstance(registry.commit_refresh(candidate), RefreshContainmentPending)
        self.assertEqual((LeaseState.CONTAINED, WorkerCommandState.CONTAINED), (
            registry.lease_state(stale), registry.worker_command_state(authorization),
        ))
        self.assertEqual((1, 0), (coordinator.count(), registry.current_refresh_candidates()))
        self.assertIsInstance(registry.commit_refresh(candidate), RefreshRecordUnavailable)
        stop = registry.setup_reference_worker_stop(authorization)
        registry.observe_worker_stopped(stop)
        result = registry.settle_contained_refresh(stale, stop)
        self.assertIsInstance(result, RefetchRequired)
        self.assertIs(result, registry.settle_contained_refresh(stale, stop))
        self.assertEqual((0, LeaseState.REFUSED), (coordinator.count(), registry.lease_state(stale)))

    def test_enqueue_during_draining_old_disposes_without_orphan_records(self) -> None:
        for when in ("before_barrier", "after_barrier"):
            with self.subTest(when=when):
                fixture = make_lifetime_fixture()
                registry = fixture["registry"]
                coordinator = fixture["coordinator"]
                registration = register(fixture)
                lease, candidate = prepare_refresh(fixture, registration, 1, ({"changed": True},))
                attempt = coordinator.begin_drain(fixture["binding"])
                if when == "after_barrier":
                    registry.migration_queue_barrier(attempt)
                sizes = registry.neutral_lineage_sizes(registration)
                publications = registry.publications
                self.assertIsInstance(registry.commit_refresh(candidate), RefetchRequired)
                self.assertEqual(LeaseState.REFUSED, registry.lease_state(lease))
                self.assertEqual(0, coordinator.count())
                self.assertEqual(sizes, registry.neutral_lineage_sizes(registration))
                self.assertEqual(publications, registry.publications)
                self.assertEqual(0, registry.current_refresh_candidates())
                self.assertIsInstance(registry.commit_refresh(candidate), RefreshRecordUnavailable)
                if when == "before_barrier":
                    registry.migration_queue_barrier(attempt)
                coordinator.begin_migration(attempt, BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2))
                self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)


def counted(action):
    """Run `action` and return (python call events, result): a deterministic
    operation counter, not wall-clock time."""

    calls = {"n": 0}

    def profiler(frame, event, arg):
        if event == "call":
            calls["n"] += 1

    sys.setprofile(profiler)
    try:
        result = action()
    finally:
        sys.setprofile(None)
    return calls["n"], result


class RetentionBoundTests(unittest.TestCase):
    """IR13: no ledger or per-command record outlives its operation, no
    receipt identity survives outside the replay ring, and per-commit lookup
    work does not grow with lifetime history."""

    def test_history_is_discarded_and_lookups_do_constant_work(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        coordinator = fixture["coordinator"]
        registration = register(fixture)
        rounds = 95
        receipt_refs, candidate_refs = [], []
        neutral_calls, changed_calls = {}, {}

        def neutral_round(revision):
            _, candidate = prepare_refresh(fixture, registration, revision, ())
            candidate_refs.append(weakref.ref(candidate))
            calls, receipt = counted(lambda: registry.commit_refresh(candidate))
            self.assertIsInstance(receipt, NeutralRefreshReceipt)
            receipt_refs.append(weakref.ref(receipt))
            if revision in (12, rounds):
                neutral_calls[revision] = calls

        def changed_round(revision):
            _, candidate = prepare_refresh(fixture, registration, revision, ({"changed": True},))
            calls, envelope = counted(lambda: registry.commit_refresh(candidate))
            self.assertIsInstance(envelope, BufferedDelivery)
            if revision in (2, rounds + 1):
                changed_calls[revision] = calls
            lease = registry.dequeue_buffer(
                fixture["queue"], envelope, fixture["handle"], registration, fixture["context"], fixture["task"][0],
            )
            settle_handoff(fixture, lease)

        for revision in range(1, rounds + 1):
            neutral_round(revision)
        self.assertEqual(neutral_calls[12], neutral_calls[rounds], "neutral commit work grew with history")
        changed_round(rounds + 1)
        for revision in range(rounds + 2, rounds + 2 + 2 * 9):
            neutral_round(revision)
        changed_round(rounds + 2 + 2 * 9)
        self.assertEqual(1, len(changed_calls) or 1)
        gc.collect()
        live_receipts = sum(1 for ref in receipt_refs if ref() is not None)
        live_candidates = sum(1 for ref in candidate_refs if ref() is not None)
        _, _, ring, capacity = registry.neutral_lineage_sizes(registration)
        self.assertEqual((9, 9), (ring, capacity))
        self.assertEqual(ring, live_receipts, "receipt identities survive only inside the replay ring")
        self.assertEqual(ring, live_candidates, "candidate identities survive only inside the replay ring")
        self.assertIsInstance(registry.commit_refresh(candidate_refs[0]() or object()), RefreshRecordUnavailable)
        self.assertEqual(0, registry.current_refresh_candidates())
        self.assertEqual(0, coordinator.count())

    def test_changed_commit_work_is_constant_and_worker_records_die_with_the_operation(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        registration = register(fixture)
        work = {}
        for round_number in range(1, 41):
            _, candidate = prepare_refresh(fixture, registration, round_number, ({"changed": True},))
            calls, envelope = counted(lambda: registry.commit_refresh(candidate))
            if round_number in (3, 40):
                work[round_number] = calls
            lease = registry.dequeue_buffer(
                fixture["queue"], envelope, fixture["handle"], registration, fixture["context"], fixture["task"][0],
            )
            settle_handoff(fixture, lease)
        self.assertEqual(work[3], work[40], "changed commit work grew with history")
        refs = []
        for _ in range(20):
            lease = registry.acquire(
                fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                resource=fixture["connection_a"], owner=fixture["task"][0],
            )
            step(fixture, lease, PlanStep.LOWER)
            artifacts = full_command(fixture, lease)
            registry.run_plan_step(lease, PlanStep.PUBLICATION, fixture["task"][0], registry.issue_consumer("publish"))
            refs.extend(weakref.ref(value) for value in artifacts.values())
            self.assertEqual(0, registry.lease_facts(lease)[4], "the ledger is discarded at terminalization")
            del artifacts
        del lease
        gc.collect()
        self.assertEqual(0, sum(1 for ref in refs if ref() is not None), "per-command records outlived their operation")
        self.assertEqual(0, fixture["coordinator"].count())


class ReplayExactnessTests(unittest.TestCase):
    """IR15: exact replay is idempotent; a different failure, cause or task is a conflict."""

    def worker_fixture(self):
        worker = object()
        fixture = build_fixture(assigned_worker_provider=lambda serial: worker)
        fixture["worker"] = worker
        registry = fixture["registry"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=fixture["task"][0],
        )
        return fixture, lease

    def test_different_failure_and_late_success_are_conflicts_with_one_bounded_diagnostic(self) -> None:
        fixture, lease = self.worker_fixture()
        registry = fixture["registry"]
        authorization = registry.dispatch_worker(lease)
        fixture["task"][0] = fixture["worker"]
        registry.dequeue_worker(lease, authorization)
        registry.worker_issuer.run_effect(authorization, 1)
        first = registry.setup_reference_worker_failure(authorization)
        second = registry.setup_reference_worker_failure(authorization)
        receipt = registry.worker_exit_failure(authorization, first)
        before = vector(registry, lease, authorization, coordinator=fixture["coordinator"])
        with self.assertRaises(ContractRefusal) as conflict:
            registry.worker_exit_failure(authorization, second)
        self.assertEqual(RefusalCode.OPERATION_OUTCOME_CONFLICT, conflict.exception.code)
        self.assertEqual(before, vector(registry, lease, authorization, coordinator=fixture["coordinator"]))
        self.assertIs(receipt, registry.worker_exit_failure(authorization, first))
        result = registry.setup_reference_worker_result(authorization, "late")
        for _ in range(2):
            with self.assertRaises(ContractRefusal) as late:
                registry.worker_exit_success(authorization, result)
            self.assertEqual(RefusalCode.OPERATION_OUTCOME_CONFLICT, late.exception.code)
        kind, recorded, diagnostics, cancel_diagnostic = registry.worker_exit_facts(authorization)
        self.assertEqual((WorkerExitKind.FAILURE, receipt, 1, False), (kind, recorded, diagnostics, cancel_diagnostic))
        self.assertEqual(before[0], registry.lease_facts(lease))
        self.assertEqual((WorkerCommandState.CONTAINED, EffectKnowledge.RETURNED), (
            registry.worker_command_state(authorization), registry.worker_effect_knowledge(authorization),
        ))

    def test_delivery_retirement_replay_requires_the_exact_cause(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        lease, registration, _ = two_range_handoff(fixture)
        authorization = registry.dispatch_worker(lease)
        registry.dequeue_worker(lease, authorization)
        failure = registry.setup_reference_worker_failure(authorization)
        receipt = registry.worker_exit_failure(authorization, failure)
        retirement = registry.delivery_retirement(lease)
        self.assertIs(retirement, registry.begin_delivery_non_success(lease, receipt))
        other = registry.setup_reference_worker_failure(authorization)
        observation = registry.setup_reference_receiving_task_done(lease)
        before = vector(registry, lease, authorization, coordinator=fixture["coordinator"], registration=registration)
        for cause in (other, observation, object.__new__(WorkerExitReceipt)):
            with self.assertRaises(ContractRefusal):
                registry.begin_delivery_non_success(lease, cause)
            self.assertEqual(before, vector(registry, lease, authorization, coordinator=fixture["coordinator"], registration=registration))

    def test_result_acceptance_replay_requires_the_receiving_task(self) -> None:
        fixture, lease = self.worker_fixture()
        registry = fixture["registry"]
        receiver = fixture["task"][0]
        authorization = drive_to(fixture, lease, "accepted", worker=fixture["worker"])
        receipt = registry.worker_exit_facts(authorization)[1]
        self.assertEqual("value", registry.accept_worker_result(receipt))
        before = vector(registry, lease, authorization, coordinator=fixture["coordinator"])
        for task in (fixture["worker"], object()):
            fixture["task"][0] = task
            with self.assertRaises(ContractRefusal) as caught:
                registry.accept_worker_result(receipt)
            self.assertEqual(RefusalCode.CONTEXT_OWNER_MISMATCH, caught.exception.code)
            self.assertEqual(before, vector(registry, lease, authorization, coordinator=fixture["coordinator"]))
        fixture["task"][0] = receiver
        self.assertEqual("value", registry.accept_worker_result(receipt))


class MigrationProductTests(unittest.TestCase):
    """IR16/IR17: the deployment-state x attempt-phase product is closed;
    every other pair or edge refuses with the product unchanged."""

    STATES = ("current", "draining", "pre_effect", "effect_begun", "indeterminate", "retired")
    OPERATIONS = (
        "begin_drain", "begin_migration", "begin_migration_effect", "reopen_no_effect",
        "publish_generation", "mark_indeterminate", "recover_success", "recover_rollback",
        "recover_non_reuse", "retire_binding", "join_runtime",
    )
    LEGAL = {
        "current": {"begin_drain": (DeploymentGenerationState.DRAINING_OLD, AttemptPhase.DRAINING_OLD, 1),
                    "join_runtime": (DeploymentGenerationState.CURRENT, None, None)},
        "draining": {"begin_migration": (DeploymentGenerationState.MIGRATING, AttemptPhase.MIGRATING_PRE_EFFECT, 2),
                     "reopen_no_effect": (DeploymentGenerationState.CURRENT, None, None)},
        "pre_effect": {"begin_migration_effect": (DeploymentGenerationState.MIGRATING, AttemptPhase.EFFECT_BEGUN, 3),
                       "reopen_no_effect": (DeploymentGenerationState.CURRENT, None, None)},
        "effect_begun": {"publish_generation": (DeploymentGenerationState.CURRENT, None, None),
                         "mark_indeterminate": (DeploymentGenerationState.MIGRATION_INDETERMINATE, AttemptPhase.EFFECT_BEGUN, 3)},
        "indeterminate": {"recover_success": (DeploymentGenerationState.CURRENT, None, None),
                          "recover_rollback": (DeploymentGenerationState.CURRENT, None, None),
                          "recover_non_reuse": (DeploymentGenerationState.RETIRED, None, None)},
        "retired": {},
    }

    def build(self, state):
        fixture = make_lifetime_fixture()
        coordinator = fixture["coordinator"]
        requested = BindingIdentity(fixture["scope"], "ir-next", "storage-next", 2)
        attempt = None
        if state != "current":
            attempt = coordinator.begin_drain(fixture["binding"])
            fixture["registry"].migration_queue_barrier(attempt)
        if state in {"pre_effect", "effect_begun", "indeterminate", "retired"}:
            coordinator.begin_migration(attempt, requested)
        if state in {"effect_begun", "indeterminate", "retired"}:
            coordinator.begin_migration_effect()
        if state in {"indeterminate", "retired"}:
            coordinator.mark_indeterminate()
        if state == "retired":
            coordinator.recover_migration(self.proof(fixture, attempt, requested, MigrationRecoveryKind.BINDING_NON_REUSE))
        return fixture, attempt, requested

    @staticmethod
    def proof(fixture, attempt, requested, kind):
        return MigrationRecoveryProof(
            kind, fixture["scope"], fixture["binding"], requested, 5,
            attempt if attempt is not None else object.__new__(MigrationAttempt),
            "outcome", "binding", "accounting",
        )

    @staticmethod
    def product(coordinator, attempt):
        phase = serial = None
        if attempt is not None:
            try:
                _, phase, serial, _ = coordinator.attempt_product(attempt)
            except ContractRefusal:
                phase = serial = None
        return (coordinator.state, phase, serial, coordinator.binding.generation, coordinator.admission_epoch, coordinator.count())

    def apply(self, operation, fixture, attempt, requested):
        """Apply the operation; return the attempt whose product to observe afterwards."""

        coordinator = fixture["coordinator"]
        live_attempt = attempt if attempt is not None else object.__new__(MigrationAttempt)
        if operation == "begin_drain":
            return coordinator.begin_drain(coordinator.binding)
        elif operation == "begin_migration":
            coordinator.begin_migration(live_attempt, requested)
        elif operation == "begin_migration_effect":
            coordinator.begin_migration_effect()
        elif operation == "reopen_no_effect":
            if attempt is None:
                coordinator.reopen_no_effect(object.__new__(MigrationNoEffectProof))
            else:
                coordinator.reopen_no_effect(coordinator.observe_request_released(attempt, coordinator.attempt_product(attempt)[3]))
        elif operation == "publish_generation":
            coordinator.publish_generation(requested)
        elif operation == "mark_indeterminate":
            coordinator.mark_indeterminate()
        elif operation == "recover_success":
            coordinator.recover_migration(self.proof(fixture, attempt, requested, MigrationRecoveryKind.REQUESTED_NEXT_SUCCEEDED))
        elif operation == "recover_rollback":
            coordinator.recover_migration(self.proof(fixture, attempt, requested, MigrationRecoveryKind.FULL_ROLLBACK_NO_EFFECT))
        elif operation == "recover_non_reuse":
            coordinator.recover_migration(self.proof(fixture, attempt, requested, MigrationRecoveryKind.BINDING_NON_REUSE))
        elif operation == "retire_binding":
            coordinator.retire_binding()
        else:
            join_peer(fixture)
        return attempt

    def test_every_product_edge_is_enumerated_and_every_other_pair_refuses(self) -> None:
        for state in self.STATES:
            for operation in self.OPERATIONS:
                with self.subTest(state=state, operation=operation):
                    fixture, attempt, requested = self.build(state)
                    coordinator = fixture["coordinator"]
                    before = self.product(coordinator, attempt)
                    expected = self.LEGAL[state].get(operation)
                    if expected is None:
                        with self.assertRaises((ContractRefusal, ValueError, TypeError)):
                            self.apply(operation, fixture, attempt, requested)
                        self.assertEqual(before, self.product(coordinator, attempt))
                        continue
                    observed = self.apply(operation, fixture, attempt, requested)
                    after = self.product(coordinator, observed)
                    self.assertEqual(expected[0], after[0])
                    if expected[1] is not None:
                        self.assertEqual((expected[1], expected[2]), (after[1], after[2]))
                    else:
                        self.assertIsNone(after[1], "the attempt is closed after this edge")

    def test_second_migration_effect_and_current_retirement_refuse_without_change(self) -> None:
        fixture, attempt, requested = self.build("effect_begun")
        coordinator = fixture["coordinator"]
        before = self.product(coordinator, attempt)
        with self.assertRaises(ContractRefusal):
            coordinator.begin_migration_effect()
        self.assertEqual(before, self.product(coordinator, attempt))
        fixture, attempt, _ = self.build("current")
        coordinator = fixture["coordinator"]
        before = self.product(coordinator, attempt)
        with self.assertRaises(ContractRefusal):
            coordinator.retire_binding()
        self.assertEqual(before, self.product(coordinator, attempt))


class DequeueAndRemovalLabelTests(unittest.TestCase):
    """IR18: dequeue validates every trusted input before the permit exchange;
    IR19: the serial-1 removal label depends on prior operation work."""

    def test_invalid_handoff_schedule_leaves_count_permits_head_and_registration_unchanged(self) -> None:
        schedule = (lambda k: () if k is OperationKind.ITERATOR_HANDOFF else (WorkerCommandSpec(f"{k.value}-command", (1,)),))
        fixture = make_lifetime_fixture(command_schedule_provider=schedule)
        registry = fixture["registry"]
        coordinator = fixture["coordinator"]
        registration = register(fixture)
        envelope = publish(fixture, registration)
        before = (coordinator.count(), registry.neutral_lineage_sizes(registration), registry.delivery_cursors(registration), registry.publications)
        with self.assertRaises(ValueError):
            registry.dequeue_buffer(fixture["queue"], envelope, fixture["handle"], registration, fixture["context"], fixture["task"][0])
        self.assertEqual(before, (coordinator.count(), registry.neutral_lineage_sizes(registration), registry.delivery_cursors(registration), registry.publications))
        self.assertEqual(1, coordinator.count())
        registry.start_close(fixture["subscription"], hard=True)
        self.assertEqual(0, coordinator.count())
        self.assertEqual("closed", registry.close_outcome(fixture["subscription"]).knowledge.value)

    def test_serial_one_removal_label_depends_on_prior_plan_work(self) -> None:
        for prior_work in (False, True):
            with self.subTest(prior_work=prior_work):
                fixture = build_fixture()
                registry = fixture["registry"]
                lease = registry.acquire(
                    fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                    resource=fixture["connection"], owner=fixture["task"][0],
                )
                if prior_work:
                    step(fixture, lease, PlanStep.LOWER)
                registry.dispatch_worker(lease)
                self.assertIsInstance(registry.request_worker_cancel(lease), WorkerExitReceipt)
                self.assertEqual(
                    LeaseState.REFUSED if prior_work else LeaseState.CANCELLED_CONFIRMED,
                    registry.lease_state(lease),
                )
                self.assertEqual(0, fixture["coordinator"].count())


class CommandGrammarEnumerationTests(unittest.TestCase):
    """IR16: every legal command edge of design §4.1 is driven and every other
    (state, operation) pair refuses with the state vector unchanged."""

    STATES = (
        WorkerCommandState.QUEUED, WorkerCommandState.RUNNING_IDLE, WorkerCommandState.SUCCESS_PENDING,
        WorkerCommandState.CONTAINED, WorkerCommandState.QUIESCENT_SUCCESS,
        WorkerCommandState.QUIESCENT_CONTAINED, WorkerCommandState.RESULT_ACCEPTED,
    )
    OPERATIONS = ("dequeue", "effect", "exit_success", "exit_failure", "cancel", "task_done", "stop", "accept")
    LEGAL = {
        WorkerCommandState.QUEUED: {
            "dequeue": WorkerCommandState.RUNNING_IDLE, "cancel": "terminal", "task_done": "terminal",
        },
        WorkerCommandState.RUNNING_IDLE: {
            "effect": WorkerCommandState.RUNNING_IDLE, "exit_success": WorkerCommandState.SUCCESS_PENDING,
            "exit_failure": WorkerCommandState.CONTAINED, "cancel": WorkerCommandState.CONTAINED,
            "task_done": WorkerCommandState.CONTAINED,
        },
        WorkerCommandState.SUCCESS_PENDING: {
            "stop": WorkerCommandState.QUIESCENT_SUCCESS, "cancel": WorkerCommandState.CONTAINED,
            "task_done": WorkerCommandState.CONTAINED, "exit_success": WorkerCommandState.SUCCESS_PENDING,
        },
        WorkerCommandState.CONTAINED: {
            "stop": WorkerCommandState.QUIESCENT_CONTAINED, "cancel": WorkerCommandState.CONTAINED,
            "task_done": WorkerCommandState.CONTAINED,
        },
        WorkerCommandState.QUIESCENT_SUCCESS: {
            "accept": WorkerCommandState.RESULT_ACCEPTED, "cancel": WorkerCommandState.QUIESCENT_CONTAINED,
            "task_done": WorkerCommandState.QUIESCENT_CONTAINED, "stop": WorkerCommandState.QUIESCENT_SUCCESS,
            "exit_success": WorkerCommandState.QUIESCENT_SUCCESS,
        },
        WorkerCommandState.QUIESCENT_CONTAINED: {
            "cancel": WorkerCommandState.QUIESCENT_CONTAINED, "task_done": WorkerCommandState.QUIESCENT_CONTAINED,
            "stop": WorkerCommandState.QUIESCENT_CONTAINED,
        },
        WorkerCommandState.RESULT_ACCEPTED: {
            "accept": WorkerCommandState.RESULT_ACCEPTED, "cancel": WorkerCommandState.RESULT_ACCEPTED,
            "task_done": WorkerCommandState.RESULT_ACCEPTED, "stop": WorkerCommandState.RESULT_ACCEPTED,
            "exit_success": WorkerCommandState.RESULT_ACCEPTED,
        },
    }
    # Design §4.1/§6: a late success after containment is refused and fills
    # only its bounded diagnostic slot; the diagnostic counter is the one
    # vector element allowed to move on that refusal.
    LATE_RETURN = {
        (WorkerCommandState.CONTAINED, "exit_success"),
        (WorkerCommandState.QUIESCENT_CONTAINED, "exit_success"),
    }

    @staticmethod
    def masked(facts):
        facts = list(facts)
        kind, receipt, _, cancel_diagnostic = facts[5]
        facts[5] = (kind, receipt, None, cancel_diagnostic)
        return tuple(facts)

    def build(self, state):
        worker = object()
        fixture = build_fixture(
            command_schedule_provider=lambda kind: (WorkerCommandSpec("grammar", (1,), (2,)),),
            assigned_worker_provider=lambda serial: worker,
        )
        registry = fixture["registry"]
        receiver = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=receiver,
        )
        authorization = registry.dispatch_worker(lease)
        artifacts = {"stop": None, "receipt": None}
        artifacts["failure"] = registry.setup_reference_worker_failure(authorization)
        artifacts["result"] = registry.setup_reference_worker_result(authorization, "value")
        if state is not WorkerCommandState.QUEUED:
            fixture["task"][0] = worker
            registry.dequeue_worker(lease, authorization)
            registry.worker_issuer.run_effect(authorization, 1)
        if state in {WorkerCommandState.SUCCESS_PENDING, WorkerCommandState.QUIESCENT_SUCCESS, WorkerCommandState.RESULT_ACCEPTED}:
            artifacts["receipt"] = registry.worker_exit_success(authorization, artifacts["result"])
        if state in {WorkerCommandState.CONTAINED, WorkerCommandState.QUIESCENT_CONTAINED}:
            fixture["task"][0] = receiver
            artifacts["receipt"] = registry.request_worker_cancel(lease)
        if state in {WorkerCommandState.QUIESCENT_SUCCESS, WorkerCommandState.QUIESCENT_CONTAINED, WorkerCommandState.RESULT_ACCEPTED}:
            artifacts["stop"] = registry.setup_reference_worker_stop(authorization)
            registry.observe_worker_stopped(artifacts["stop"])
        fixture["task"][0] = receiver
        if state is WorkerCommandState.RESULT_ACCEPTED:
            registry.accept_worker_result(artifacts["receipt"])
        self.assertIs(state, registry.worker_command_state(authorization))
        fixture["worker"] = worker
        return fixture, lease, authorization, artifacts

    def apply(self, operation, fixture, lease, authorization, artifacts):
        registry = fixture["registry"]
        receiver = fixture["task"][0]
        if operation == "dequeue":
            fixture["task"][0] = fixture["worker"]
            registry.dequeue_worker(lease, authorization)
        elif operation == "effect":
            fixture["task"][0] = fixture["worker"]
            registry.worker_issuer.run_effect(authorization, 2)
        elif operation == "exit_success":
            fixture["task"][0] = fixture["worker"]
            registry.worker_exit_success(authorization, artifacts["result"])
        elif operation == "exit_failure":
            fixture["task"][0] = fixture["worker"]
            registry.worker_exit_failure(authorization, artifacts["failure"])
        elif operation == "cancel":
            registry.request_worker_cancel(lease)
        elif operation == "task_done":
            registry.observe_receiving_task_done(registry.setup_reference_receiving_task_done(lease))
        elif operation == "stop":
            stop = artifacts["stop"] or registry.setup_reference_worker_stop(authorization)
            registry.observe_worker_stopped(stop)
        else:
            registry.accept_worker_result(artifacts["receipt"] or object.__new__(WorkerExitReceipt))
        fixture["task"][0] = receiver

    def test_every_legal_edge_is_driven_and_every_other_pair_refuses(self) -> None:
        for state in self.STATES:
            for operation in self.OPERATIONS:
                with self.subTest(state=state.value, operation=operation):
                    fixture, lease, authorization, artifacts = self.build(state)
                    registry = fixture["registry"]
                    coordinator = fixture["coordinator"]
                    expected = self.LEGAL[state].get(operation)
                    if expected is None:
                        before = vector(registry, lease, authorization, coordinator=coordinator)
                        try:
                            self.apply(operation, fixture, lease, authorization, artifacts)
                        except ContractRefusal:
                            pass
                        else:
                            self.fail("an edge outside the closed grammar was accepted")
                        after = vector(registry, lease, authorization, coordinator=coordinator)
                        if (state, operation) in self.LATE_RETURN:
                            self.assertEqual(self.masked(before), self.masked(after))
                            self.assertEqual(before[5][2] + 1, after[5][2], "one bounded late-return diagnostic")
                        else:
                            self.assertEqual(before, after)
                        continue
                    self.apply(operation, fixture, lease, authorization, artifacts)
                    if expected == "terminal":
                        self.assertEqual(LeaseState.CANCELLED_CONFIRMED, registry.lease_state(lease))
                        self.assertEqual(0, coordinator.count())
                        continue
                    self.assertIs(expected, registry.worker_command_state(authorization))
                    self.assertEqual(1, coordinator.count())
                    if state is WorkerCommandState.RESULT_ACCEPTED and operation in {"cancel", "task_done"}:
                        self.assertEqual(LeaseState.CONTAINED, registry.lease_state(lease))


if __name__ == "__main__":
    unittest.main()
