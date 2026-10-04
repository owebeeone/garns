from __future__ import annotations

import unittest

from garns.backends.contracts.admission import AdmittedReadHandle, LeaseState, OperationIdentity, OperationKind
from garns.backends.contracts.authority import RuntimeAuthority, TrustedClaims
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import (
    ActivationEvidence, ActivationState, BufferedDelivery, DeploymentGenerationState,
    GenerationPermit, ResourceIdentity, ResourceKind,
)
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.recovery import (
    ActivationNoEffectRecoveryProof, ActivationUnusedWithdrawalProof,
    MigrationRecoveryKind, MigrationRecoveryProof,
)
from garns.backends.contracts.migration_reference import MigrationAttempt, MigrationNoEffectProof
from garns.backends.contracts.semantic import BindingIdentity, FrozenPlanRoot, Plan, PlanOrigin, ResultShape
from garns.backends.contracts.values import (
    Capability, ContractRefusal, ParameterValues, QualifiedDeployment,
    RefusalCode, RevisionCursor,
)


def activated():
    scope = QualifiedDeployment("SALES", "PROD")
    binding = BindingIdentity(scope, "ir", "storage", 1)
    coordinator = ReferenceGenerationCoordinator(scope, binding)
    coordinator.begin_activation(12)
    coordinator.finish_activation(ActivationEvidence(
        scope, binding, 12, "operator-inventory", "physical-access-fence",
        "durable-record", "plan_admission_lifetime_v1",
    ))
    coordinator.first_lifetime_open("plan_admission_lifetime_v1", 12)
    return scope, binding, coordinator


def participant(scope, binding, coordinator, name):
    task = object()
    authority = RuntimeAuthority(lambda: 1.0, lambda: 1, lambda: task)
    context = authority.issue(TrustedClaims(
        name, name, scope, {Capability.QUERY}, name, 10.0, 1,
    ))
    registry = ReferenceLifetimeRegistry(authority, object(), coordinator)
    runtime = ResourceIdentity(f"{name}-runtime", ResourceKind.RUNTIME)
    pool = ResourceIdentity(f"{name}-pool", ResourceKind.POOL, (runtime.name,))
    connection = ResourceIdentity(
        f"{name}-connection", ResourceKind.CONNECTION, (runtime.name, pool.name),
    )
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
    def test_two_participant_drain_counts_exact_permits(self) -> None:
        scope, binding, coordinator = activated()
        next_binding = BindingIdentity(scope, "ir-next", "storage-next", 2)
        parts = [participant(scope, binding, coordinator, name) for name in ("first", "second")]
        leases = [
            item["registry"].acquire(
                item["handle"], OperationKind.EXECUTE, ParameterValues({}), item["context"],
                resource=item["connection"], owner=item["task"],
            )
            for item in parts
        ]
        attempt = coordinator.begin_drain(binding)
        with self.assertRaises(ContractRefusal):
            coordinator.begin_migration(attempt, next_binding)
        for item, lease in zip(parts, leases):
            item["registry"].transfer_owner(lease, item["task"], item["task"])
            item["registry"].complete(lease, item["task"], LeaseState.SUCCEEDED)
        for item in parts:
            item["registry"].migration_queue_barrier(attempt)
        coordinator.begin_migration(attempt, next_binding)
        self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)

    def test_generation_permits_are_exact_owned_and_replay_safe(self) -> None:
        scope, binding, coordinator = activated()
        owner = object()
        operation = OperationIdentity(object(), 1, scope, 1)
        permit = coordinator.acquire_shared(operation, owner)
        forged = object.__new__(GenerationPermit)
        other = ReferenceGenerationCoordinator(scope, binding)
        with self.assertRaises(ValueError):
            coordinator.release_shared(forged, owner)
        with self.assertRaises(ValueError):
            coordinator.release_shared(permit, object())
        with self.assertRaises(ValueError):
            other.release_shared(permit, owner)
        self.assertEqual(1, coordinator.count())
        coordinator.release_shared(permit, owner)
        with self.assertRaises(ValueError):
            coordinator.release_shared(permit, owner)
        self.assertEqual(0, coordinator.count())

    def test_buffer_envelope_alone_cannot_release_private_permit(self) -> None:
        scope, _, coordinator = activated()
        owner = object()
        envelope = BufferedDelivery(
            scope, 1, object.__new__(AdmittedReadHandle), "digest", RevisionCursor(scope, 1, 0),
            RevisionCursor(scope, 1, 1), RevisionCursor(scope, 1, 1), (), "advance",
        )
        permit = coordinator.add_buffer(envelope, owner)
        other = ReferenceGenerationCoordinator(scope, coordinator.binding)
        with self.assertRaises(ValueError):
            coordinator.release_buffer(envelope, owner)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            coordinator.release_buffer(permit, object())
        with self.assertRaises(ValueError):
            other.release_buffer(permit, owner)
        self.assertEqual(1, coordinator.count())
        coordinator.release_buffer(permit, owner)
        with self.assertRaises(ValueError):
            coordinator.release_buffer(permit, owner)

    def test_activation_negative_recovery_and_withdrawal_require_exact_proofs(self) -> None:
        scope = QualifiedDeployment("SALES", "NEW")
        binding = BindingIdentity(scope, "ir", "storage", 1)
        coordinator = ReferenceGenerationCoordinator(scope, binding)
        coordinator.begin_activation(2)
        coordinator.mark_activation_indeterminate()
        before = (coordinator.activation, coordinator.protocol_epoch)
        for proof in (None, object(), ActivationNoEffectRecoveryProof(
            scope, binding, 1, "inventory-absent", "record-absent", "legacy-restored",
        )):
            with self.assertRaises((TypeError, ContractRefusal)):
                coordinator.recover_activation(proof)
            self.assertEqual(before, (coordinator.activation, coordinator.protocol_epoch))
        coordinator.recover_activation(ActivationNoEffectRecoveryProof(
            scope, binding, 2, "inventory-absent", "record-absent", "legacy-restored",
        ))
        self.assertEqual(ActivationState.UNACTIVATED, coordinator.activation)
        with self.assertRaises(ValueError):
            coordinator.begin_activation(2)

        coordinator.begin_activation(3)
        coordinator.finish_activation(ActivationEvidence(
            scope, binding, 3, "inventory", "physical", "record",
            "plan_admission_lifetime_v1",
        ))
        stale = ActivationUnusedWithdrawalProof(
            scope, binding, 2, "physical", "never-open", "withdrawn", "legacy-restored",
        )
        with self.assertRaises(ContractRefusal):
            coordinator.withdraw_unused(stale)
        self.assertEqual(ActivationState.ACTIVE_UNUSED, coordinator.activation)
        wrong_fence = ActivationUnusedWithdrawalProof(
            scope, binding, 3, "different-physical-fence", "never-open", "withdrawn",
            "legacy-restored",
        )
        with self.assertRaises(ContractRefusal):
            coordinator.withdraw_unused(wrong_fence)
        self.assertEqual(ActivationState.ACTIVE_UNUSED, coordinator.activation)
        coordinator.withdraw_unused(ActivationUnusedWithdrawalProof(
            scope, binding, 3, "physical", "never-open", "withdrawn", "legacy-restored",
        ))
        with self.assertRaises(ValueError):
            coordinator.begin_activation(3)

    def test_active_activation_has_no_outgoing_reset_edge(self) -> None:
        _, _, coordinator = activated()
        with self.assertRaises(ContractRefusal):
            coordinator.refuse_retirement_or_reset()
        self.assertEqual(ActivationState.ACTIVE, coordinator.activation)

    def test_migration_recovery_has_three_exact_proof_bearing_outcomes(self) -> None:
        for kind, expected_state, expected_generation in (
            (MigrationRecoveryKind.REQUESTED_NEXT_SUCCEEDED, DeploymentGenerationState.CURRENT, 2),
            (MigrationRecoveryKind.FULL_ROLLBACK_NO_EFFECT, DeploymentGenerationState.CURRENT, 1),
            (MigrationRecoveryKind.BINDING_NON_REUSE, DeploymentGenerationState.RETIRED, 1),
        ):
            with self.subTest(kind=kind):
                scope, old, coordinator = activated()
                requested = BindingIdentity(scope, "ir-next", "storage-next", 2)
                attempt = coordinator.begin_drain(old)
                coordinator.begin_migration(attempt, requested)
                coordinator.begin_migration_effect()
                coordinator.mark_indeterminate()
                before = (coordinator.state, coordinator.binding, coordinator.admission_epoch)
                wrong = MigrationRecoveryProof(
                    kind, scope, old, requested, 13, attempt,
                    "outcome", "binding", "accounting",
                )
                with self.assertRaises(ContractRefusal):
                    coordinator.recover_migration(wrong)
                self.assertEqual(before, (coordinator.state, coordinator.binding, coordinator.admission_epoch))
                coordinator.recover_migration(MigrationRecoveryProof(
                    kind, scope, old, requested, 12, attempt,
                    "outcome", "binding", "accounting",
                ))
                self.assertEqual(expected_state, coordinator.state)
                self.assertEqual(expected_generation, coordinator.binding.generation)
                self.assertEqual(12, coordinator.protocol_epoch)

    def test_published_generation_never_relabels_old_admission(self) -> None:
        scope, binding, coordinator = activated()
        old = participant(scope, binding, coordinator, "old")
        next_binding = BindingIdentity(scope, "ir-next", "storage-next", 2)
        attempt = coordinator.begin_drain(binding)
        old["registry"].migration_queue_barrier(attempt)
        coordinator.begin_migration(attempt, next_binding)
        coordinator.begin_migration_effect()
        coordinator.publish_generation(next_binding)
        with self.assertRaises(ContractRefusal) as caught:
            old["registry"].acquire(
                old["handle"], OperationKind.EXECUTE, ParameterValues({}), old["context"],
                resource=old["connection"], owner=old["task"],
            )
        self.assertIn(caught.exception.code, {RefusalCode.ADMISSION_REVOKED, RefusalCode.GENERATION_MISMATCH})

    def test_attempt_requires_every_exact_participant_barrier(self) -> None:
        scope, binding, coordinator = activated()
        parts = [participant(scope, binding, coordinator, name) for name in ("first", "second")]
        attempt = coordinator.begin_drain(binding)
        next_binding = BindingIdentity(scope, "ir-next", "storage-next", 2)
        with self.assertRaises(ContractRefusal):
            coordinator.begin_migration(attempt, next_binding)
        parts[0]["registry"].migration_queue_barrier(attempt)
        with self.assertRaises(ContractRefusal):
            coordinator.begin_migration(attempt, next_binding)
        with self.assertRaises(ContractRefusal):
            parts[0]["registry"].migration_queue_barrier(attempt)
        parts[1]["registry"].migration_queue_barrier(attempt)
        coordinator.begin_migration(attempt, next_binding)
        self.assertEqual(DeploymentGenerationState.MIGRATING, coordinator.state)
        with self.assertRaises(ContractRefusal):
            parts[1]["registry"].migration_queue_barrier(attempt)

    def test_no_effect_reopen_requires_current_exact_proof_and_barriers(self) -> None:
        scope, binding, coordinator = activated()
        item = participant(scope, binding, coordinator, "participant")
        attempt = coordinator.begin_drain(binding)
        before = (coordinator.state, coordinator.admission_epoch, coordinator.binding)
        for proof in (None, object(), object.__new__(MigrationNoEffectProof)):
            with self.assertRaises((TypeError, ContractRefusal)):
                coordinator.reopen_no_effect(proof)
            self.assertEqual(before, (coordinator.state, coordinator.admission_epoch, coordinator.binding))
        proof = coordinator.setup_reference_no_effect_proof(
            attempt, exclusive_request_released_digest="released",
            no_effect_outcome_digest="no-effect",
        )
        other = ReferenceGenerationCoordinator(scope, binding)
        other.begin_activation(12)
        other.finish_activation(ActivationEvidence(
            scope, binding, 12, "inventory", "physical", "record",
            "plan_admission_lifetime_v1",
        ))
        other.first_lifetime_open("plan_admission_lifetime_v1", 12)
        other_attempt = other.begin_drain(binding)
        cross_proof = other.setup_reference_no_effect_proof(
            other_attempt, exclusive_request_released_digest="released",
            no_effect_outcome_digest="no-effect",
        )
        with self.assertRaises(ContractRefusal):
            coordinator.reopen_no_effect(cross_proof)
        with self.assertRaises(ContractRefusal):
            coordinator.reopen_no_effect(proof)
        item["registry"].migration_queue_barrier(attempt)
        coordinator.reopen_no_effect(proof)
        item["registry"].reopen_queues_no_effect(attempt)
        self.assertEqual(DeploymentGenerationState.CURRENT, coordinator.state)
        self.assertEqual(before[1] + 1, coordinator.admission_epoch)
        with self.assertRaises(ContractRefusal):
            coordinator.reopen_no_effect(proof)
        second = coordinator.begin_drain(binding)
        item["registry"].migration_queue_barrier(second)
        with self.assertRaises(ContractRefusal):
            coordinator.reopen_no_effect(proof)

    def test_pre_effect_migrating_reopen_and_exact_successor_only(self) -> None:
        scope, binding, coordinator = activated()
        attempt = coordinator.begin_drain(binding)
        for generation in (1, 3):
            with self.assertRaises(ContractRefusal):
                coordinator.begin_migration(
                    attempt, BindingIdentity(scope, f"ir-{generation}", f"storage-{generation}", generation),
                )
            self.assertEqual(DeploymentGenerationState.DRAINING_OLD, coordinator.state)
        requested = BindingIdentity(scope, "ir-next", "storage-next", 2)
        coordinator.begin_migration(attempt, requested)
        proof = coordinator.setup_reference_no_effect_proof(
            attempt, exclusive_request_released_digest="released",
            no_effect_outcome_digest="no-effect",
        )
        coordinator.reopen_no_effect(proof)
        self.assertEqual(binding, coordinator.binding)
        self.assertEqual(DeploymentGenerationState.CURRENT, coordinator.state)

    def test_unknown_activation_protocol_fails_closed(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        binding = BindingIdentity(scope, "ir", "storage", 1)
        coordinator = ReferenceGenerationCoordinator(scope, binding)
        coordinator.begin_activation(1)
        with self.assertRaises(ContractRefusal):
            coordinator.finish_activation(ActivationEvidence(
                scope, binding, 1, "inventory", "physical", "record", "unknown",
            ))
        self.assertEqual(ActivationState.ACTIVATING, coordinator.activation)


if __name__ == "__main__":
    unittest.main()
