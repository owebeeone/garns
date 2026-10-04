from __future__ import annotations

import copy
import unittest

from garns.backends.contracts.admission import LeaseState, OperationKind, PlanStep
from garns.backends.contracts.authority import RuntimeAuthority, TrustedClaims
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import (
    ActivationEvidence, BufferedDelivery, DeploymentGenerationState,
    LocalResourceState, QueueState, ResourceIdentity, ResourceKind,
)
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.migration_reference import MigrationNoEffectProof
from garns.backends.contracts.snapshot_reference import (
    InitialSnapshotCandidate, RefreshSnapshotCandidate,
)
from garns.backends.contracts.semantic import BindingIdentity, FrozenPlanRoot, Plan, PlanOrigin, ResultShape
from garns.backends.contracts.state import CloseKnowledge
from garns.backends.contracts.values import (
    Capability, ContractRefusal, ParameterValues, QualifiedDeployment,
    RefusalCode, RevisionCursor, TransactionIdentity,
)


def make_plan(scope, binding, noun="question", digest="live"):
    return Plan(
        f"sales.{digest}", noun, (), ResultShape(()),
        FrozenPlanRoot("garns.plan/1", digest, digest.encode()),
        PlanOrigin(scope.world, binding.ir_digest, binding.storage_digest, binding.generation),
        8 if noun == "question" else None,
    )


def make_lifetime_fixture():
    scope = QualifiedDeployment("SALES", "PROD")
    binding = BindingIdentity(scope, "ir", "storage", 1)
    task = [object()]
    now = [1.0]
    epoch = [1]
    authority = RuntimeAuthority(lambda: now[0], lambda: epoch[0], lambda: task[0])
    context = authority.issue(TrustedClaims(
        "p", "w", scope, {Capability.QUERY, Capability.LIVE}, "c", 10.0, 1,
    ))
    coordinator = ReferenceGenerationCoordinator(scope, binding)
    coordinator.begin_activation(5)
    coordinator.finish_activation(ActivationEvidence(
        scope, binding, 5, "inventory", "physical", "record",
        "plan_admission_lifetime_v1",
    ))
    coordinator.first_lifetime_open("plan_admission_lifetime_v1", 5)
    registry = ReferenceLifetimeRegistry(authority, object(), coordinator)
    runtime = ResourceIdentity("runtime", ResourceKind.RUNTIME)
    pool_a = ResourceIdentity("pool-a", ResourceKind.POOL, ("runtime",))
    pool_b = ResourceIdentity("pool-b", ResourceKind.POOL, ("runtime",))
    connection_a = ResourceIdentity("connection-a", ResourceKind.CONNECTION, ("runtime", "pool-a"))
    connection_b = ResourceIdentity("connection-b", ResourceKind.CONNECTION, ("runtime", "pool-b"))
    subscription = ResourceIdentity("subscription", ResourceKind.SUBSCRIPTION, ("runtime",))
    queue = ResourceIdentity("queue", ResourceKind.DELIVERY_QUEUE, ("runtime", "subscription"))
    peer_subscription = ResourceIdentity("peer-subscription", ResourceKind.SUBSCRIPTION, ("runtime",))
    peer_queue = ResourceIdentity("peer-queue", ResourceKind.DELIVERY_QUEUE, ("runtime", "peer-subscription"))
    for resource in (
        runtime, pool_a, pool_b, connection_a, connection_b,
        subscription, queue, peer_subscription, peer_queue,
    ):
        registry.add_resource(resource)
    live_plan = make_plan(scope, binding)
    query_plan = make_plan(scope, binding, "query", "query")
    handle = registry.setup_reference_admission(live_plan, binding)
    query_handle = registry.setup_reference_admission(query_plan, binding)
    return locals()


def step(fixture, lease, exact_step, label="step"):
    return fixture["registry"].run_plan_step(
        lease, exact_step, fixture["task"][0],
        fixture["registry"].issue_consumer(label),
    )


def register(fixture, *, peer=False):
    registry = fixture["registry"]
    owner = fixture["task"][0]
    subscription = fixture["peer_subscription" if peer else "subscription"]
    queue = fixture["peer_queue" if peer else "queue"]
    lease = registry.acquire(
        fixture["handle"], OperationKind.SNAPSHOT_REGISTRATION,
        ParameterValues({"tenant": "a"}), fixture["context"],
        resource=subscription, owner=owner,
    )
    step(fixture, lease, PlanStep.FETCH, "snapshot-fetch")
    step(fixture, lease, PlanStep.SNAPSHOT_WATERMARK, "snapshot-watermark")
    candidate = registry.setup_reference_initial_snapshot(
        lease, owner, subscription, queue, ({"initial": True},),
        RevisionCursor(fixture["scope"], 1, 0),
    )
    step(fixture, lease, PlanStep.REGISTRATION, "registration")
    step(fixture, lease, PlanStep.ASSEMBLY, "snapshot-assembly")
    result = registry.register_subscription(lease, owner, candidate)
    registry.complete(lease, owner, LeaseState.SUCCEEDED)
    return result.registration


def publish(fixture, registration, *, peer=False, revision=1):
    registry = fixture["registry"]
    owner = fixture["task"][0]
    subscription = fixture["peer_subscription" if peer else "subscription"]
    queue = fixture["peer_queue" if peer else "queue"]
    lease = registry.acquire(
        fixture["handle"], OperationKind.REFRESH,
        ParameterValues({"tenant": "a"}), fixture["context"],
        resource=subscription, owner=owner,
    )
    step(fixture, lease, PlanStep.FETCH, "refresh-fetch")
    step(fixture, lease, PlanStep.ASSEMBLY, "refresh-assembly")
    step(fixture, lease, PlanStep.CURSOR_ADVANCE, "refresh-cursor")
    candidate = registry.setup_reference_refresh_candidate(
        lease, owner, registration,
        RevisionCursor(fixture["scope"], 1, revision - 1),
        RevisionCursor(fixture["scope"], 1, revision),
        RevisionCursor(fixture["scope"], 1, revision),
        ({"status": "open"},), f"advance-{revision}",
    )
    return registry.publish_refresh_buffer(lease, owner, candidate)


class LifetimeContractTests(unittest.TestCase):
    def test_acquisition_charges_ancestry_and_close_is_peer_local(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        lease = registry.acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection_a"], owner=owner,
        )
        registry.start_close(fixture["pool_a"])
        with self.assertRaises(ContractRefusal):
            registry.acquire(
                fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                resource=fixture["connection_a"], owner=owner,
            )
        peer = registry.acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection_b"], owner=owner,
        )
        registry.transfer_owner(peer, owner, owner)
        registry.complete(peer, owner, LeaseState.SUCCEEDED)
        self.assertEqual(CloseKnowledge.NONQUIESCENT, registry.close_outcome(fixture["pool_a"]).knowledge)
        registry.transfer_owner(lease, owner, owner)
        registry.complete(lease, owner, LeaseState.SUCCEEDED)
        self.assertEqual(CloseKnowledge.CLOSED, registry.close_outcome(fixture["pool_a"]).knowledge)
        self.assertEqual(LocalResourceState.LOCAL_OPEN, registry.resource_state(fixture["pool_b"]))

    def test_open_close_finalization_refuses_without_mutation(self) -> None:
        fixture = make_lifetime_fixture()
        before = fixture["registry"].resource_state(fixture["runtime"])
        with self.assertRaises(ContractRefusal):
            fixture["registry"].close_outcome(fixture["runtime"])
        self.assertEqual(before, fixture["registry"].resource_state(fixture["runtime"]))
        lease = fixture["registry"].acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection_a"], owner=fixture["task"][0],
        )
        fixture["registry"].complete(lease, fixture["task"][0], LeaseState.REFUSED)

    def test_steps_are_strict_and_publication_is_exactly_once(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        lease = registry.acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({"x": 1}),
            fixture["context"], resource=fixture["connection_a"], owner=owner,
        )
        consumer = registry.issue_consumer("publish")
        with self.assertRaises(ContractRefusal):
            registry.run_plan_step(lease, PlanStep.PUBLICATION, owner, consumer)
        product = step(fixture, lease, PlanStep.LOWER)
        self.assertEqual({"x": 1}, dict(product.parameters.items()))
        with self.assertRaises(ValueError):
            step(fixture, lease, PlanStep.VALIDATE)
        registry.run_plan_step(lease, PlanStep.PUBLICATION, owner, consumer)
        with self.assertRaises((ContractRefusal, ValueError)):
            registry.run_plan_step(lease, PlanStep.PUBLICATION, owner, consumer)
        self.assertEqual(1, registry.publications)

        illegal = registry.acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection_a"], owner=owner,
        )
        with self.assertRaises(ValueError):
            step(fixture, illegal, PlanStep.REGISTRATION)
        self.assertEqual(LeaseState.ACQUIRED, registry.lease_state(illegal))
        registry.complete(illegal, owner, LeaseState.REFUSED)

        before = fixture["coordinator"].count()
        with self.assertRaises(ContractRefusal):
            registry.acquire(
                fixture["handle"], OperationKind.ITERATOR_HANDOFF, ParameterValues({}),
                fixture["context"], resource=fixture["queue"], owner=owner,
            )
        self.assertEqual(before, fixture["coordinator"].count())

    def test_revocation_expiry_fence_and_graceful_old_generation(self) -> None:
        for attack in ("revoke", "expiry", "fence"):
            with self.subTest(attack=attack):
                fixture = make_lifetime_fixture()
                registry = fixture["registry"]
                owner = fixture["task"][0]
                lease = registry.acquire(
                    fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
                    fixture["context"], resource=fixture["connection_a"], owner=owner,
                )
                step(fixture, lease, PlanStep.LOWER)
                if attack == "revoke":
                    registry.revoke_generation()
                elif attack == "expiry":
                    fixture["now"][0] = 10.0
                else:
                    registry.start_close(fixture["connection_a"], hard=True)
                with self.assertRaises(ContractRefusal):
                    registry.run_plan_step(
                        lease, PlanStep.PUBLICATION, owner,
                        registry.issue_consumer("blocked"),
                    )
                self.assertEqual(0, registry.publications)
                self.assertEqual(LeaseState.CONTAINED, registry.lease_state(lease))
                self.assertEqual(1, fixture["coordinator"].count())

        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        lease = registry.acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection_a"], owner=owner,
        )
        step(fixture, lease, PlanStep.LOWER)
        fixture["coordinator"].begin_drain(fixture["binding"])
        step(fixture, lease, PlanStep.PUBLICATION)
        self.assertEqual(1, registry.publications)

    def test_buffer_provenance_exchange_and_replay_refuse_without_count_change(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        registration = register(fixture)
        premature = registry.acquire(
            fixture["handle"], OperationKind.REFRESH, ParameterValues({"tenant": "a"}),
            fixture["context"], resource=fixture["subscription"], owner=fixture["task"][0],
        )
        with self.assertRaises(ContractRefusal):
            registry.setup_reference_refresh_candidate(
                premature, fixture["task"][0], registration,
                RevisionCursor(fixture["scope"], 1, 0),
                RevisionCursor(fixture["scope"], 1, 1),
                RevisionCursor(fixture["scope"], 1, 1), (), "premature",
            )
        registry.complete(premature, fixture["task"][0], LeaseState.REFUSED)
        bypass = registry.acquire(
            fixture["handle"], OperationKind.REFRESH, ParameterValues({"tenant": "a"}),
            fixture["context"], resource=fixture["subscription"], owner=fixture["task"][0],
        )
        step(fixture, bypass, PlanStep.FETCH)
        with self.assertRaises(ContractRefusal):
            step(fixture, bypass, PlanStep.PUBLICATION)
        self.assertEqual(1, registry.publications)
        registry.complete(bypass, fixture["task"][0], LeaseState.REFUSED)
        envelope = publish(fixture, registration)
        self.assertEqual(1, fixture["coordinator"].count())
        for parameters, previous in (
            (ParameterValues({"tenant": "other"}), RevisionCursor(fixture["scope"], 1, 1)),
            (ParameterValues({"tenant": "a"}), RevisionCursor(fixture["scope"], 1, 0)),
        ):
            refresh = registry.acquire(
                fixture["handle"], OperationKind.REFRESH, parameters, fixture["context"],
                resource=fixture["subscription"], owner=fixture["task"][0],
            )
            step(fixture, refresh, PlanStep.FETCH)
            step(fixture, refresh, PlanStep.ASSEMBLY)
            step(fixture, refresh, PlanStep.CURSOR_ADVANCE)
            before_candidate = fixture["coordinator"].count()
            with self.assertRaises(ContractRefusal):
                registry.setup_reference_refresh_candidate(
                    refresh, fixture["task"][0], registration, previous,
                    RevisionCursor(fixture["scope"], 1, 2),
                    RevisionCursor(fixture["scope"], 1, 2), (), "advance-2",
                )
            self.assertEqual(before_candidate, fixture["coordinator"].count())
            registry.complete(refresh, fixture["task"][0], LeaseState.REFUSED)
        copied = copy.copy(envelope)
        other = registry.setup_reference_admission(
            make_plan(fixture["scope"], fixture["binding"], "question", "other"), fixture["binding"],
        )
        before = fixture["coordinator"].count()
        with self.assertRaises(ContractRefusal):
            registry.dequeue_buffer(
                fixture["queue"], copied, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )
        with self.assertRaises(ContractRefusal):
            registry.dequeue_buffer(
                fixture["queue"], envelope, other, registration,
                fixture["context"], fixture["task"][0],
            )
        self.assertEqual(before, fixture["coordinator"].count())
        handoff = registry.dequeue_buffer(
            fixture["queue"], envelope, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        self.assertEqual(1, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.dequeue_buffer(
                fixture["queue"], envelope, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )
        self.assertEqual(1, fixture["coordinator"].count())
        registry.complete(handoff, fixture["task"][0], LeaseState.REFUSED)

    def test_two_buffer_ranges_are_delivered_fifo_with_one_active_head(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        registration = register(fixture)
        first = publish(fixture, registration, revision=1)
        second = publish(fixture, registration, revision=2)
        self.assertEqual(2, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.dequeue_buffer(
                fixture["queue"], second, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )
        self.assertEqual(2, fixture["coordinator"].count())
        first_handoff = registry.dequeue_buffer(
            fixture["queue"], first, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        self.assertEqual(2, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.dequeue_buffer(
                fixture["queue"], second, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )
        step(fixture, first_handoff, PlanStep.VALIDATE)
        step(fixture, first_handoff, PlanStep.PUBLICATION)
        registry.complete(first_handoff, fixture["task"][0], LeaseState.SUCCEEDED)
        second_handoff = registry.dequeue_buffer(
            fixture["queue"], second, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        step(fixture, second_handoff, PlanStep.VALIDATE)
        step(fixture, second_handoff, PlanStep.PUBLICATION)
        registry.complete(second_handoff, fixture["task"][0], LeaseState.SUCCEEDED)
        registry.complete(second_handoff, fixture["task"][0], LeaseState.SUCCEEDED)
        self.assertEqual(0, fixture["coordinator"].count())

    def test_snapshot_candidates_are_sealed_lease_bound_and_queue_fenced(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.SNAPSHOT_REGISTRATION,
            ParameterValues({"tenant": "a"}), fixture["context"],
            resource=fixture["subscription"], owner=owner,
        )
        with self.assertRaises(ContractRefusal):
            registry.setup_reference_initial_snapshot(
                lease, owner, fixture["subscription"], fixture["queue"], (),
                RevisionCursor(fixture["scope"], 1, 0),
            )
        step(fixture, lease, PlanStep.FETCH)
        step(fixture, lease, PlanStep.SNAPSHOT_WATERMARK)
        candidate = registry.setup_reference_initial_snapshot(
            lease, owner, fixture["subscription"], fixture["queue"],
            ({"row": 1},), RevisionCursor(fixture["scope"], 1, 0),
        )
        self.assertEqual((), InitialSnapshotCandidate.__slots__)
        self.assertFalse(hasattr(candidate, "__dict__"))
        for action in (lambda: copy.copy(candidate), lambda: InitialSnapshotCandidate()):
            with self.assertRaises(TypeError):
                action()
        step(fixture, lease, PlanStep.REGISTRATION)
        step(fixture, lease, PlanStep.ASSEMBLY)
        registry.start_close(fixture["queue"], hard=True)
        before = (registry.publications, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.register_subscription(lease, owner, candidate)
        self.assertEqual(before, (registry.publications, fixture["coordinator"].count()))
        self.assertEqual(LeaseState.CONTAINED, registry.lease_state(lease))
        registry.complete(lease, owner, LeaseState.REFUSED)

    def test_refresh_candidate_is_exact_one_shot_and_not_an_envelope(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        registration = register(fixture)
        lease = registry.acquire(
            fixture["handle"], OperationKind.REFRESH, ParameterValues({"tenant": "a"}),
            fixture["context"], resource=fixture["subscription"], owner=owner,
        )
        for plan_step in (PlanStep.FETCH, PlanStep.ASSEMBLY, PlanStep.CURSOR_ADVANCE):
            step(fixture, lease, plan_step)
        candidate = registry.setup_reference_refresh_candidate(
            lease, owner, registration, RevisionCursor(fixture["scope"], 1, 0),
            RevisionCursor(fixture["scope"], 1, 1),
            RevisionCursor(fixture["scope"], 1, 1), ({"row": 1},), "advance-1",
        )
        self.assertEqual((), RefreshSnapshotCandidate.__slots__)
        self.assertFalse(hasattr(candidate, "__dict__"))
        with self.assertRaises(TypeError):
            copy.copy(candidate)
        envelope = registry.publish_refresh_buffer(lease, owner, candidate)
        self.assertIsInstance(envelope, BufferedDelivery)
        with self.assertRaises(ContractRefusal):
            registry.publish_refresh_buffer(lease, owner, candidate)

    def test_snapshot_candidate_cross_lease_refuses_without_consuming_it(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]

        def prepared():
            lease = registry.acquire(
                fixture["handle"], OperationKind.SNAPSHOT_REGISTRATION,
                ParameterValues({"tenant": "a"}), fixture["context"],
                resource=fixture["subscription"], owner=owner,
            )
            step(fixture, lease, PlanStep.FETCH)
            step(fixture, lease, PlanStep.SNAPSHOT_WATERMARK)
            candidate = registry.setup_reference_initial_snapshot(
                lease, owner, fixture["subscription"], fixture["queue"],
                ({"row": 1},), RevisionCursor(fixture["scope"], 1, 0),
            )
            step(fixture, lease, PlanStep.REGISTRATION)
            step(fixture, lease, PlanStep.ASSEMBLY)
            return lease, candidate

        first, candidate = prepared()
        second, _ = prepared()
        before = (registry.publications, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.register_subscription(second, owner, candidate)
        self.assertEqual(before, (registry.publications, fixture["coordinator"].count()))
        registry.complete(second, owner, LeaseState.REFUSED)
        result = registry.register_subscription(first, owner, candidate)
        self.assertEqual(RevisionCursor(fixture["scope"], 1, 0), result.watermark)
        with self.assertRaises(ContractRefusal):
            registry.register_subscription(first, owner, candidate)
        self.assertEqual(before[0] + 1, registry.publications)
        registry.complete(first, owner, LeaseState.SUCCEEDED)

    def test_invalidation_between_fifo_ranges_releases_queue_not_active_handoff(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        registration = register(fixture)
        first = publish(fixture, registration, revision=1)
        publish(fixture, registration, revision=2)
        handoff = registry.dequeue_buffer(
            fixture["queue"], first, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        self.assertEqual(2, fixture["coordinator"].count())
        registry.start_close(fixture["subscription"], hard=True)
        self.assertEqual(1, fixture["coordinator"].count())
        self.assertEqual(LeaseState.CONTAINED, registry.lease_state(handoff))
        registry.complete(handoff, fixture["task"][0], LeaseState.REFUSED)
        self.assertEqual(0, fixture["coordinator"].count())

    def test_migration_attempt_barrier_releases_multiple_queued_buffers_once(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        registration = register(fixture)
        first = publish(fixture, registration, revision=1)
        publish(fixture, registration, revision=2)
        self.assertEqual(2, fixture["coordinator"].count())
        attempt = fixture["coordinator"].begin_drain(fixture["binding"])
        self.assertEqual(2, registry.migration_queue_barrier(attempt))
        self.assertEqual(0, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.migration_queue_barrier(attempt)
        with self.assertRaises(ContractRefusal):
            registry.dequeue_buffer(
                fixture["queue"], first, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )
        proof = fixture["coordinator"].setup_reference_no_effect_proof(
            attempt, exclusive_request_released_digest="released",
            no_effect_outcome_digest="no-effect",
        )
        fixture["coordinator"].reopen_no_effect(proof)
        registry.reopen_queues_no_effect(attempt)
        with self.assertRaises(ContractRefusal):
            registry.dequeue_buffer(
                fixture["queue"], first, fixture["handle"], registration,
                fixture["context"], fixture["task"][0],
            )

    def test_close_invalidates_selected_buffers_once_and_not_peer(self) -> None:
        fixture = make_lifetime_fixture()
        first_registration = register(fixture)
        peer_registration = register(fixture, peer=True)
        first = publish(fixture, first_registration)
        peer = publish(fixture, peer_registration, peer=True)
        self.assertEqual(2, fixture["coordinator"].count())
        fixture["registry"].start_close(fixture["subscription"], hard=True)
        self.assertEqual(1, fixture["coordinator"].count())
        fixture["registry"].start_close(fixture["subscription"], hard=True)
        self.assertEqual(1, fixture["coordinator"].count())
        self.assertEqual(CloseKnowledge.CLOSED, fixture["registry"].close_outcome(fixture["subscription"]).knowledge)
        with self.assertRaises(ContractRefusal):
            fixture["registry"].dequeue_buffer(
                fixture["queue"], first, fixture["handle"], first_registration,
                fixture["context"], fixture["task"][0],
            )
        handoff = fixture["registry"].dequeue_buffer(
            fixture["peer_queue"], peer, fixture["handle"], peer_registration,
            fixture["context"], fixture["task"][0],
        )
        self.assertIsInstance(peer, BufferedDelivery)
        fixture["registry"].complete(handoff, fixture["task"][0], LeaseState.REFUSED)

        for root_name in ("queue", "runtime"):
            with self.subTest(root=root_name):
                current = make_lifetime_fixture()
                publish(current, register(current))
                self.assertEqual(1, current["coordinator"].count())
                current["registry"].start_close(current[root_name], hard=True)
                self.assertEqual(0, current["coordinator"].count())
                self.assertEqual(
                    CloseKnowledge.CLOSED,
                    current["registry"].close_outcome(current[root_name]).knowledge,
                )

    def test_refresh_publication_revalidates_every_barrier(self) -> None:
        for attack in ("expiry", "revocation", "fence", "drain"):
            with self.subTest(attack=attack):
                fixture = make_lifetime_fixture()
                registry = fixture["registry"]
                owner = fixture["task"][0]
                registration = register(fixture)
                lease = registry.acquire(
                    fixture["handle"], OperationKind.REFRESH,
                    ParameterValues({"tenant": "a"}), fixture["context"],
                    resource=fixture["subscription"], owner=owner,
                )
                step(fixture, lease, PlanStep.FETCH)
                step(fixture, lease, PlanStep.ASSEMBLY)
                step(fixture, lease, PlanStep.CURSOR_ADVANCE)
                candidate = registry.setup_reference_refresh_candidate(
                    lease, owner, registration,
                    RevisionCursor(fixture["scope"], 1, 0),
                    RevisionCursor(fixture["scope"], 1, 1),
                    RevisionCursor(fixture["scope"], 1, 1), (), "advance",
                )
                if attack == "expiry":
                    fixture["now"][0] = 10.0
                elif attack == "revocation":
                    registry.revoke_generation()
                elif attack == "fence":
                    registry.start_close(fixture["subscription"], hard=True)
                else:
                    attempt = fixture["coordinator"].begin_drain(fixture["binding"])
                    registry.migration_queue_barrier(attempt)
                before = (registry.publications, fixture["coordinator"].count())
                with self.assertRaises(ContractRefusal):
                    registry.publish_refresh_buffer(lease, owner, candidate)
                self.assertEqual(before, (registry.publications, fixture["coordinator"].count()))
                self.assertEqual(LeaseState.CONTAINED, registry.lease_state(lease))
                registry.complete(lease, owner, LeaseState.REFUSED)

    def test_closed_waits_for_contained_handoff(self) -> None:
        fixture = make_lifetime_fixture()
        registration = register(fixture)
        envelope = publish(fixture, registration)
        handoff = fixture["registry"].dequeue_buffer(
            fixture["queue"], envelope, fixture["handle"], registration,
            fixture["context"], fixture["task"][0],
        )
        fixture["registry"].start_close(fixture["subscription"], hard=True)
        self.assertEqual(LeaseState.CONTAINED, fixture["registry"].lease_state(handoff))
        self.assertEqual(
            CloseKnowledge.NONQUIESCENT,
            fixture["registry"].close_outcome(fixture["subscription"]).knowledge,
        )
        fixture["registry"].complete(handoff, fixture["task"][0], LeaseState.REFUSED)
        self.assertEqual(
            CloseKnowledge.CLOSED,
            fixture["registry"].close_outcome(fixture["subscription"]).knowledge,
        )

    def test_no_effect_reopen_invalidates_old_admission_and_lease(self) -> None:
        fixture = make_lifetime_fixture()
        coordinator = fixture["coordinator"]
        old_lease = fixture["registry"].acquire(
            fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection_a"], owner=fixture["task"][0],
        )
        attempt = coordinator.begin_drain(fixture["binding"])
        fixture["registry"].migration_queue_barrier(attempt)
        proof = coordinator.setup_reference_no_effect_proof(
            attempt, exclusive_request_released_digest="released",
            no_effect_outcome_digest="no-effect",
        )
        coordinator.reopen_no_effect(proof)
        fixture["registry"].reopen_queues_no_effect(attempt)
        with self.assertRaises(ContractRefusal):
            fixture["registry"].run_plan_step(
                old_lease, PlanStep.LOWER, fixture["task"][0],
                fixture["registry"].issue_consumer("old"),
            )
        self.assertEqual(LeaseState.CONTAINED, fixture["registry"].lease_state(old_lease))
        with self.assertRaises(ContractRefusal):
            fixture["registry"].acquire(
                fixture["query_handle"], OperationKind.EXECUTE, ParameterValues({}),
                fixture["context"], resource=fixture["connection_a"], owner=fixture["task"][0],
            )
        new_handle = fixture["registry"].setup_reference_admission(
            fixture["query_plan"], fixture["binding"],
        )
        lease = fixture["registry"].acquire(
            new_handle, OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection_a"], owner=fixture["task"][0],
        )
        self.assertEqual(2, coordinator.count())
        fixture["registry"].complete(lease, fixture["task"][0], LeaseState.REFUSED)
        fixture["registry"].complete(old_lease, fixture["task"][0], LeaseState.REFUSED)

    def test_transactions_and_operations_remain_independent_close_knowledge(self) -> None:
        fixture = make_lifetime_fixture()
        tx = TransactionIdentity(fixture["scope"], "tx")
        fixture["registry"].start_close(fixture["pool_a"])
        outcome = fixture["registry"].close_outcome(fixture["pool_a"], (tx,))
        self.assertEqual(CloseKnowledge.UNRESOLVED, outcome.knowledge)
        self.assertEqual((tx,), outcome.unresolved)

    def test_resource_and_state_enums_are_closed(self) -> None:
        for malformed in ("runtime", 0, False, object()):
            with self.assertRaises((TypeError, ValueError)):
                ResourceIdentity("x", malformed)
        self.assertEqual(QueueState.OPEN.value, "open")
        self.assertEqual(LocalResourceState.LOCAL_FENCED.value, "local_fenced")


if __name__ == "__main__":
    unittest.main()
