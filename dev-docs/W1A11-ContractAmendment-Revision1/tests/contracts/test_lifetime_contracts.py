from __future__ import annotations

import unittest

from garns.backends.contracts.admission import LeaseState, OperationKind, PlanStep
from garns.backends.contracts.authority import RuntimeAuthority, TrustedClaims
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import (
    ActivationEvidence,
    ActivationState,
    BufferedDelivery,
    DeploymentGenerationState,
    LocalResourceState,
    QueueState,
    ResourceIdentity,
    ResourceKind,
)
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.semantic import (
    BindingIdentity,
    FrozenPlanRoot,
    Plan,
    PlanOrigin,
    ResultField,
    ResultShape,
    SemanticType,
)
from garns.backends.contracts.state import CloseKnowledge
from garns.backends.contracts.values import (
    Capability,
    ContractRefusal,
    ParameterValues,
    QualifiedDeployment,
    RefusalCode,
    RevisionCursor,
    TransactionIdentity,
)


def make_lifetime_fixture():
    scope = QualifiedDeployment("SALES", "PROD")
    binding = BindingIdentity(scope, "ir", "storage", 1)
    plan = Plan(
        "sales.live",
        "question",
        (),
        ResultShape((ResultField("sales.Order.status", SemanticType("Text", "text")),)),
        FrozenPlanRoot("garns.plan/1", "digest", b"payload"),
        PlanOrigin("SALES", "ir", "storage", 1),
        8,
    )
    task = object()
    authority = RuntimeAuthority(lambda: 1.0, lambda: 1, lambda: task)
    context = authority.issue(TrustedClaims(
        "p", "w", scope, {Capability.QUERY, Capability.LIVE}, "c", 10.0, 1,
    ))
    coordinator = ReferenceGenerationCoordinator(scope, binding)
    coordinator.begin_activation()
    evidence = ActivationEvidence(
        scope, binding, 5, "inventory", "physical", "record", "plan_admission_lifetime_v1",
    )
    coordinator.finish_activation(evidence)
    coordinator.first_lifetime_open("plan_admission_lifetime_v1", 5)
    registry = ReferenceLifetimeRegistry(authority, object(), coordinator)
    runtime = ResourceIdentity("runtime", ResourceKind.RUNTIME)
    pool_a = ResourceIdentity("pool-a", ResourceKind.POOL, ("runtime",))
    pool_b = ResourceIdentity("pool-b", ResourceKind.POOL, ("runtime",))
    connection_a = ResourceIdentity("connection-a", ResourceKind.CONNECTION, ("runtime", "pool-a"))
    connection_b = ResourceIdentity("connection-b", ResourceKind.CONNECTION, ("runtime", "pool-b"))
    subscription = ResourceIdentity("subscription", ResourceKind.SUBSCRIPTION, ("runtime",))
    queue = ResourceIdentity("queue", ResourceKind.DELIVERY_QUEUE, ("runtime", "subscription"))
    for resource in (runtime, pool_a, pool_b, connection_a, connection_b, subscription, queue):
        registry.add_resource(resource)
    handle = registry.setup_reference_admission(plan, binding)
    return locals()


def envelope(fixture, revision=1):
    scope = fixture["scope"]
    return BufferedDelivery(
        scope,
        1,
        fixture["handle"],
        "digest",
        RevisionCursor(scope, 1, revision - 1),
        RevisionCursor(scope, 1, revision),
        RevisionCursor(scope, 1, revision),
        ({"status": "open"},),
        f"advance-{revision}",
    )


class LifetimeContractTests(unittest.TestCase):
    def test_acquisition_charges_ancestry_and_local_close_isolated_from_peer(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection_a"], owner=owner,
        )
        registry.start_close(fixture["pool_a"])
        with self.assertRaises(ContractRefusal) as caught:
            registry.acquire(
                fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                resource=fixture["connection_a"], owner=owner,
            )
        self.assertEqual(RefusalCode.LOCAL_RESOURCE_DRAINING, caught.exception.code)
        peer = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection_b"], owner=owner,
        )
        self.assertEqual(DeploymentGenerationState.CURRENT, fixture["coordinator"].state)
        registry.transfer_owner(peer, owner, owner)
        registry.complete(peer, owner, LeaseState.SUCCEEDED)
        self.assertEqual(CloseKnowledge.NONQUIESCENT, registry.close_outcome(fixture["pool_a"]).knowledge)
        registry.transfer_owner(lease, owner, owner)
        registry.complete(lease, owner, LeaseState.SUCCEEDED)
        self.assertEqual(CloseKnowledge.CLOSED, registry.close_outcome(fixture["pool_a"]).knowledge)

    def test_nontransaction_read_and_hard_fence_remain_owned_until_terminal(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection_a"], owner=owner,
        )
        operation = registry.operation(lease)
        registry.start_close(fixture["runtime"], hard=True)
        outcome = registry.close_outcome(fixture["runtime"])
        self.assertEqual(CloseKnowledge.NONQUIESCENT, outcome.knowledge)
        self.assertEqual((operation,), outcome.operations)
        self.assertEqual((), outcome.unresolved)
        self.assertEqual(1, fixture["coordinator"].count())
        registry.complete(lease, owner, LeaseState.REFUSED)
        self.assertEqual(CloseKnowledge.CLOSED, registry.close_outcome(fixture["runtime"]).knowledge)
        self.assertEqual(0, fixture["coordinator"].count())

    def test_hard_fence_after_private_work_suppresses_publication(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection_a"], owner=owner,
        )
        registry.run_plan_step(lease, PlanStep.FETCH, owner, lambda plan: ("private-row",))
        registry.start_close(fixture["connection_a"], hard=True)
        with self.assertRaises(ContractRefusal):
            registry.run_plan_step(lease, PlanStep.PUBLICATION, owner, lambda plan: "public-row")
        self.assertEqual(0, registry.publications)
        registry.complete(lease, owner, LeaseState.REFUSED)

    def test_transaction_knowledge_and_operation_quiescence_are_independent(self) -> None:
        fixture = make_lifetime_fixture()
        tx = TransactionIdentity(fixture["scope"], "tx")
        registry = fixture["registry"]
        registry.start_close(fixture["pool_a"])
        outcome = registry.close_outcome(fixture["pool_a"], (tx,))
        self.assertEqual(CloseKnowledge.UNRESOLVED, outcome.knowledge)
        self.assertEqual((tx,), outcome.unresolved)
        self.assertEqual((), outcome.operations)

    def test_refresh_buffer_barrier_discards_once_and_blocks_late_enqueue(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"]
        first = registry.acquire(
            fixture["handle"], OperationKind.REFRESH, ParameterValues({}), fixture["context"],
            resource=fixture["subscription"], owner=owner,
        )
        first_envelope = envelope(fixture, 1)
        registry.transfer_owner(first, owner, owner)
        registry.publish_refresh_buffer(first, owner, fixture["queue"], first_envelope)
        late = registry.acquire(
            fixture["handle"], OperationKind.REFRESH, ParameterValues({}), fixture["context"],
            resource=fixture["subscription"], owner=owner,
        )
        self.assertEqual(2, fixture["coordinator"].count())
        fixture["coordinator"].begin_drain(fixture["binding"])
        self.assertEqual(1, registry.migration_queue_barrier())
        self.assertEqual(1, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.publish_refresh_buffer(late, owner, fixture["queue"], envelope(fixture, 2))
        registry.complete(late, owner, LeaseState.REFUSED)
        self.assertEqual(0, fixture["coordinator"].count())
        with self.assertRaises(ValueError):
            registry.discard_buffer(first_envelope)
        fixture["coordinator"].begin_migration()

    def test_dequeue_winner_becomes_active_handoff_and_delays_migration(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        owner = fixture["task"]
        item = envelope(fixture)
        registry.enqueue_buffer(fixture["queue"], item)
        handoff = registry.dequeue_buffer(
            fixture["queue"], item, fixture["handle"], ParameterValues({}), fixture["context"], owner,
        )
        self.assertEqual(1, fixture["coordinator"].count())
        fixture["coordinator"].begin_drain(fixture["binding"])
        self.assertEqual(0, registry.migration_queue_barrier())
        with self.assertRaises(ContractRefusal):
            fixture["coordinator"].begin_migration()
        registry.transfer_owner(handoff, owner, owner)
        registry.complete(handoff, owner, LeaseState.SUCCEEDED)
        fixture["coordinator"].begin_migration()
        self.assertEqual(DeploymentGenerationState.MIGRATING, fixture["coordinator"].state)

    def test_no_effect_reopen_uses_new_epoch_and_never_resurrects_buffers(self) -> None:
        fixture = make_lifetime_fixture()
        registry = fixture["registry"]
        item = envelope(fixture)
        registry.enqueue_buffer(fixture["queue"], item)
        fixture["coordinator"].begin_drain(fixture["binding"])
        registry.migration_queue_barrier()
        fixture["coordinator"].reopen_no_effect()
        registry.reopen_queues_no_effect()
        self.assertEqual(DeploymentGenerationState.CURRENT, fixture["coordinator"].state)
        with self.assertRaises(ValueError):
            registry.discard_buffer(item)
        new_item = envelope(fixture, 2)
        registry.enqueue_buffer(fixture["queue"], new_item)
        self.assertEqual(1, fixture["coordinator"].count())

    def test_effectful_unknown_migration_outcome_is_indeterminate(self) -> None:
        fixture = make_lifetime_fixture()
        coordinator = fixture["coordinator"]
        coordinator.begin_drain(fixture["binding"])
        fixture["registry"].migration_queue_barrier()
        coordinator.begin_migration()
        coordinator.begin_migration_effect()
        coordinator.mark_indeterminate()
        self.assertEqual(DeploymentGenerationState.MIGRATION_INDETERMINATE, coordinator.state)
        with self.assertRaises(ContractRefusal):
            coordinator.reopen_no_effect()

    def test_activation_edges_are_one_time_and_missing_legacy_fence_refuses(self) -> None:
        scope = QualifiedDeployment("SALES", "NEW")
        binding = BindingIdentity(scope, "ir", "storage", 1)
        coordinator = ReferenceGenerationCoordinator(scope, binding)
        with self.assertRaises(ContractRefusal):
            coordinator.acquire_shared(object())  # type: ignore[arg-type]
        coordinator.begin_activation()
        with self.assertRaises(ContractRefusal):
            coordinator.finish_activation(ActivationEvidence(
                scope, binding, 1, "inventory", "physical", "record", "plan_admission_v1",
            ))
        self.assertEqual(ActivationState.ACTIVATING, coordinator.activation)
        coordinator.mark_activation_indeterminate()
        coordinator.recover_activation(None)
        self.assertEqual(ActivationState.UNACTIVATED, coordinator.activation)

        coordinator.begin_activation()
        evidence = ActivationEvidence(
            scope, binding, 2, "inventory", "physical", "record", "plan_admission_lifetime_v1",
        )
        coordinator.finish_activation(evidence)
        coordinator.first_lifetime_open("plan_admission_lifetime_v1", 2)
        self.assertEqual(ActivationState.ACTIVE, coordinator.activation)
        before = (coordinator.activation, coordinator.protocol_epoch, coordinator.count())
        with self.assertRaises(ContractRefusal):
            coordinator.refuse_retirement_or_reset()
        self.assertEqual(before, (coordinator.activation, coordinator.protocol_epoch, coordinator.count()))

    def test_resource_and_state_enums_require_exact_members(self) -> None:
        for malformed in ("runtime", 0, False, object()):
            with self.assertRaises((TypeError, ValueError)):
                ResourceIdentity("x", malformed)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            ResourceIdentity("connection", ResourceKind.CONNECTION, ("runtime",))
        fixture = make_lifetime_fixture()
        malformed = ResourceIdentity(
            "bad-connection", ResourceKind.CONNECTION, ("runtime", "subscription"),
        )
        with self.assertRaises(ValueError):
            fixture["registry"].add_resource(malformed)
        self.assertEqual(QueueState.OPEN.value, "open")
        self.assertEqual(LocalResourceState.LOCAL_FENCED.value, "local_fenced")


if __name__ == "__main__":
    unittest.main()
