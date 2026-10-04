from __future__ import annotations

import unittest

from garns.backends.contracts.admission import LeaseState, OperationKind
from garns.backends.contracts.authority import RuntimeAuthority, TrustedClaims
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import ActivationEvidence, ActivationState, DeploymentGenerationState, ResourceIdentity, ResourceKind
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.semantic import BindingIdentity, FrozenPlanRoot, Plan, PlanOrigin, ResultShape
from garns.backends.contracts.values import Capability, ContractRefusal, ParameterValues, QualifiedDeployment, RefusalCode


def participant(scope, binding, coordinator, name):
    task = object()
    authority = RuntimeAuthority(lambda: 1.0, lambda: 1, lambda: task)
    context = authority.issue(TrustedClaims(
        name, name, scope, {Capability.QUERY}, name, 10.0, 1,
    ))
    registry = ReferenceLifetimeRegistry(authority, object(), coordinator)
    runtime = ResourceIdentity(f"{name}-runtime", ResourceKind.RUNTIME)
    pool = ResourceIdentity(f"{name}-pool", ResourceKind.POOL, (runtime.name,))
    connection = ResourceIdentity(f"{name}-connection", ResourceKind.CONNECTION, (runtime.name, pool.name))
    for resource in (runtime, pool, connection):
        registry.add_resource(resource)
    plan = Plan(
        f"sales.{name}", "query", (), ResultShape(()),
        FrozenPlanRoot("garns.plan/1", name, name.encode()),
        PlanOrigin(scope.world, binding.ir_digest, binding.storage_digest, binding.generation),
    )
    handle = registry.setup_reference_admission(plan, binding)
    return locals()


class GenerationContractTests(unittest.TestCase):
    def activated(self):
        scope = QualifiedDeployment("SALES", "PROD")
        binding = BindingIdentity(scope, "ir", "storage", 1)
        coordinator = ReferenceGenerationCoordinator(scope, binding)
        coordinator.begin_activation()
        evidence = ActivationEvidence(
            scope, binding, 12, "operator-inventory", "physical-access-fence",
            "durable-record", "plan_admission_lifetime_v1",
        )
        coordinator.finish_activation(evidence)
        coordinator.first_lifetime_open("plan_admission_lifetime_v1", 12)
        return scope, binding, coordinator

    def test_two_participant_drain_counts_global_permits(self) -> None:
        scope, binding, coordinator = self.activated()
        first = participant(scope, binding, coordinator, "first")
        second = participant(scope, binding, coordinator, "second")
        leases = []
        for current in (first, second):
            leases.append(current["registry"].acquire(
                current["handle"], OperationKind.EXECUTE, ParameterValues({}), current["context"],
                resource=current["connection"], owner=current["task"],
            ))
        self.assertEqual(2, coordinator.count())
        coordinator.begin_drain(binding)
        with self.assertRaises(ContractRefusal):
            first["registry"].acquire(
                first["handle"], OperationKind.EXECUTE, ParameterValues({}), first["context"],
                resource=first["connection"], owner=first["task"],
            )
        first["registry"].transfer_owner(leases[0], first["task"], first["task"])
        first["registry"].complete(leases[0], first["task"], LeaseState.SUCCEEDED)
        self.assertEqual(1, coordinator.count())
        with self.assertRaises(ContractRefusal):
            coordinator.begin_migration()
        second["registry"].transfer_owner(leases[1], second["task"], second["task"])
        second["registry"].complete(leases[1], second["task"], LeaseState.SUCCEEDED)
        coordinator.begin_migration()
        self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)

    def test_local_close_does_not_retire_deployment_or_peer(self) -> None:
        scope, binding, coordinator = self.activated()
        first = participant(scope, binding, coordinator, "first")
        second = participant(scope, binding, coordinator, "second")
        first["registry"].start_close(first["runtime"])
        first["registry"].close_outcome(first["runtime"])
        lease = second["registry"].acquire(
            second["handle"], OperationKind.EXECUTE, ParameterValues({}), second["context"],
            resource=second["connection"], owner=second["task"],
        )
        self.assertEqual(DeploymentGenerationState.CURRENT, coordinator.state)
        self.assertEqual(ActivationState.ACTIVE, coordinator.activation)
        second["registry"].transfer_owner(lease, second["task"], second["task"])
        second["registry"].complete(lease, second["task"], LeaseState.SUCCEEDED)

    def test_publish_next_generation_never_relabels_old_admission(self) -> None:
        scope, binding, coordinator = self.activated()
        old = participant(scope, binding, coordinator, "old")
        coordinator.begin_drain(binding)
        coordinator.begin_migration()
        coordinator.begin_migration_effect()
        next_binding = BindingIdentity(scope, "ir-next", "storage-next", 2)
        coordinator.publish_generation(next_binding)
        with self.assertRaises(ContractRefusal) as caught:
            old["registry"].acquire(
                old["handle"], OperationKind.EXECUTE, ParameterValues({}), old["context"],
                resource=old["connection"], owner=old["task"],
            )
        self.assertEqual(RefusalCode.GENERATION_MISMATCH, caught.exception.code)

    def test_active_unused_withdrawal_and_active_irreversibility_are_distinct(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        binding = BindingIdentity(scope, "ir", "storage", 1)
        evidence = ActivationEvidence(
            scope, binding, 2, "inventory", "physical", "record", "plan_admission_lifetime_v1",
        )
        unused = ReferenceGenerationCoordinator(scope, binding)
        unused.begin_activation()
        unused.finish_activation(evidence)
        unused.withdraw_unused(2)
        self.assertEqual(ActivationState.UNACTIVATED, unused.activation)

        active = ReferenceGenerationCoordinator(scope, binding)
        active.begin_activation()
        active.finish_activation(evidence)
        active.first_lifetime_open("plan_admission_lifetime_v1", 2)
        with self.assertRaises(ContractRefusal):
            active.withdraw_unused(2)
        with self.assertRaises(ContractRefusal):
            active.refuse_retirement_or_reset()
        self.assertEqual(ActivationState.ACTIVE, active.activation)

    def test_legacy_missing_and_unknown_protocols_fail_closed(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        binding = BindingIdentity(scope, "ir", "storage", 1)
        for protocol in ("plan_admission_v1", "", "future_unknown"):
            coordinator = ReferenceGenerationCoordinator(scope, binding)
            coordinator.begin_activation()
            with self.assertRaises(ContractRefusal) as caught:
                coordinator.finish_activation(ActivationEvidence(
                    scope, binding, 1, "inventory", "physical", "record", protocol,
                ))
            self.assertEqual(RefusalCode.LIFETIME_PROTOCOL_REQUIRED, caught.exception.code)
            self.assertEqual(ActivationState.ACTIVATING, coordinator.activation)


if __name__ == "__main__":
    unittest.main()
