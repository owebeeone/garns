from __future__ import annotations

import copy
import inspect
import pickle
import unittest

from garns.backends.contracts.admission import (
    AdmittedReadHandle,
    LeaseState,
    OperationKind,
    PlanStep,
    ReadOperationLease,
)
from garns.backends.contracts.authority import RuntimeAuthority, TrustedClaims
from garns.backends.contracts.consumers import ClosedPlanConsumer
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import ActivationEvidence, ResourceIdentity, ResourceKind
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.protocols import AsyncBackend, AsyncConnection
from garns.backends.contracts.semantic import (
    BindingIdentity,
    FrozenPlanRoot,
    Plan,
    PlanOrigin,
    ResultField,
    ResultShape,
    SemanticType,
)
from garns.backends.contracts.values import (
    Capability,
    ContractRefusal,
    ParameterValues,
    QualifiedDeployment,
    RefusalCode,
)


def build_fixture(capabilities=frozenset({Capability.QUERY})):
    scope = QualifiedDeployment("SALES", "PROD")
    binding = BindingIdentity(scope, "ir", "storage", 1)
    plan = Plan(
        "sales.open",
        "query",
        (),
        ResultShape((ResultField("sales.Order.status", SemanticType("Text", "text")),)),
        FrozenPlanRoot("garns.plan/1", "digest", b"payload"),
        PlanOrigin("SALES", "ir", "storage", 1),
    )
    task = [object()]
    now = [1.0]
    epoch = [3]
    authority = RuntimeAuthority(lambda: now[0], lambda: epoch[0], lambda: task[0])
    context = authority.issue(TrustedClaims(
        "principal", "writer", scope, capabilities, "context", 10.0, 3,
    ))
    coordinator = ReferenceGenerationCoordinator(scope, binding)
    coordinator.begin_activation(7)
    coordinator.finish_activation(ActivationEvidence(
        scope, binding, 7, "inventory", "physical", "record",
        "plan_admission_lifetime_v1",
    ))
    coordinator.first_lifetime_open("plan_admission_lifetime_v1", 7)
    registry = ReferenceLifetimeRegistry(authority, object(), coordinator)
    runtime = ResourceIdentity("runtime", ResourceKind.RUNTIME)
    pool = ResourceIdentity("pool", ResourceKind.POOL, ("runtime",))
    connection = ResourceIdentity("connection", ResourceKind.CONNECTION, ("runtime", "pool"))
    for resource in (runtime, pool, connection):
        registry.add_resource(resource)
    handle = registry.setup_reference_admission(plan, binding)
    return locals()


class AdmissionContractTests(unittest.TestCase):
    def test_handles_are_empty_sealed_and_not_copyable_or_serializable(self) -> None:
        fixture = build_fixture()
        handle = fixture["handle"]
        lease = fixture["registry"].acquire(
            handle,
            OperationKind.EXECUTE,
            ParameterValues({}),
            fixture["context"],
            resource=fixture["connection"],
            owner=fixture["task"][0],
        )
        self.assertEqual(("__weakref__",), AdmittedReadHandle.__slots__)
        self.assertEqual(("__weakref__",), ReadOperationLease.__slots__)
        for value in (handle, lease):
            for operation in (
                lambda value=value: copy.copy(value),
                lambda value=value: copy.deepcopy(value),
                lambda value=value: pickle.dumps(value),
            ):
                with self.assertRaises(TypeError):
                    operation()
            for name in ("plan", "root", "claims", "registry", "issuer", "binding", "generation"):
                self.assertFalse(hasattr(value, name), name)
                with self.assertRaises(AttributeError):
                    setattr(value, name, object())
        with self.assertRaises(TypeError):
            AdmittedReadHandle()
        with self.assertRaises(TypeError):
            ReadOperationLease()

    def test_production_rebuild_compare_is_distinct_from_fixture_setup(self) -> None:
        fixture = build_fixture()
        plan = fixture["plan"]
        registry = fixture["registry"]
        binding = fixture["binding"]
        registry.admit_rebuilt(plan, plan, binding)
        mutant = Plan(
            plan.read_qid,
            plan.noun,
            plan.parameters,
            plan.result,
            FrozenPlanRoot("garns.plan/1", "other", b"other"),
            plan.origin,
        )
        with self.assertRaises(ContractRefusal) as caught:
            registry.admit_rebuilt(mutant, plan, binding)
        self.assertEqual(RefusalCode.PLAN_PROVENANCE_MISMATCH, caught.exception.code)

    def test_counterfeit_cross_registry_and_revoked_handles_refuse_without_lease(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        before = fixture["coordinator"].count()
        with self.assertRaises(ContractRefusal):
            registry.acquire(
                object.__new__(AdmittedReadHandle),
                OperationKind.EXECUTE,
                ParameterValues({}),
                fixture["context"],
                resource=fixture["connection"],
                owner=fixture["task"][0],
            )
        other = build_fixture()
        with self.assertRaises(ContractRefusal):
            registry.acquire(
                other["handle"],
                OperationKind.EXECUTE,
                ParameterValues({}),
                fixture["context"],
                resource=fixture["connection"],
                owner=fixture["task"][0],
            )
        registry.revoke_generation()
        with self.assertRaises(ContractRefusal):
            registry.acquire(
                fixture["handle"],
                OperationKind.EXECUTE,
                ParameterValues({}),
                fixture["context"],
                resource=fixture["connection"],
                owner=fixture["task"][0],
            )
        self.assertEqual(before, fixture["coordinator"].count())

    def test_guard_drives_effect_and_rejects_plan_escape_through_wrappers(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]

        def acquire():
            return registry.acquire(
                fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                resource=fixture["connection"], owner=owner,
            )

        lease = acquire()
        with self.assertRaises(TypeError):
            registry.issue_consumer("lower", lambda product: None)
        consumer = registry.issue_consumer("lower")
        result = registry.run_plan_step(
            lease, PlanStep.LOWER, owner, consumer,
        )
        self.assertEqual("sales.open", result.read_qid)

        for escape in (
            lambda plan: plan,
            lambda plan: plan.root,
            lambda plan: {"wrapped": plan},
            lambda plan: (lambda: plan),
        ):
            candidate = acquire()
            with self.assertRaises(ContractRefusal):
                registry.run_plan_step(candidate, PlanStep.LOWER, owner, escape)
            self.assertEqual(LeaseState.ACQUIRED, registry.lease_state(candidate))

        forged = object.__new__(ClosedPlanConsumer)
        candidate = acquire()
        with self.assertRaises(ContractRefusal):
            registry.run_plan_step(candidate, PlanStep.LOWER, owner, forged)
        other = build_fixture()
        with self.assertRaises(ContractRefusal):
            registry.run_plan_step(
                candidate, PlanStep.LOWER, owner, other["registry"].issue_consumer("cross"),
            )

    def test_parent_owned_derived_commands_share_one_permit_and_order(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        before = fixture["coordinator"].count()
        self.assertNotIn("nested_fetch", {kind.value for kind in OperationKind})
        self.assertNotIn("total_fetch", {kind.value for kind in OperationKind})
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        registry.run_plan_step(lease, PlanStep.LOWER, owner, registry.issue_consumer("lower"))
        with self.assertRaises(ValueError):
            registry.run_plan_step(
                lease, PlanStep.CHILD_FETCH, owner, registry.issue_consumer("unowned-child"),
            )
        child = registry.issue_derived_command(lease, owner, PlanStep.CHILD_FETCH, 1, "child")
        total = registry.issue_derived_command(lease, owner, PlanStep.TOTAL_FETCH, 2, "total")
        self.assertEqual(before + 1, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.run_derived_command(lease, owner, total, 2)
        self.assertEqual(PlanStep.CHILD_FETCH, registry.run_derived_command(lease, owner, child, 1).step)
        with self.assertRaises(ContractRefusal):
            registry.run_derived_command(lease, owner, child, 1)
        self.assertEqual(PlanStep.TOTAL_FETCH, registry.run_derived_command(lease, owner, total, 2).step)
        registry.complete(lease, owner, LeaseState.REFUSED)
        with self.assertRaises(ContractRefusal):
            registry.run_derived_command(lease, owner, total, 2)
        self.assertEqual(before, fixture["coordinator"].count())

    def test_publication_is_committed_before_return_and_cannot_be_relabeled(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        registry.run_plan_step(lease, PlanStep.LOWER, owner, registry.issue_consumer("lower"))
        product = registry.run_plan_step(
            lease, PlanStep.PUBLICATION, owner, registry.issue_consumer("publication"),
        )
        self.assertEqual(PlanStep.PUBLICATION, product.step)
        self.assertEqual(1, registry.publications)
        with self.assertRaises(ContractRefusal):
            registry.complete(lease, owner, LeaseState.REFUSED)
        registry.complete(lease, owner, LeaseState.SUCCEEDED)

    def test_authority_is_revalidated_between_steps_and_before_publication(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        registry.run_plan_step(lease, PlanStep.LOWER, owner, registry.issue_consumer("lower"))
        fixture["now"][0] = 10.0
        with self.assertRaises(ContractRefusal):
            registry.run_plan_step(
                lease, PlanStep.PUBLICATION, owner, registry.issue_consumer("publish"),
            )
        self.assertEqual(0, registry.publications)

    def test_owner_transfer_and_terminal_completion_are_compare_and_idempotent(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        worker = object()
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        registry.transfer_owner(lease, owner, worker)
        self.assertEqual(LeaseState.RUNNING, registry.lease_state(lease))
        with self.assertRaises(ContractRefusal):
            registry.transfer_owner(lease, owner, object())
        registry.complete(lease, worker, LeaseState.SUCCEEDED)
        registry.complete(lease, worker, LeaseState.SUCCEEDED)
        self.assertEqual(0, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal) as caught:
            registry.complete(lease, worker, LeaseState.REFUSED)
        self.assertEqual(RefusalCode.OPERATION_OUTCOME_CONFLICT, caught.exception.code)

    def test_rejected_transfer_is_atomic_and_old_owner_remains_usable(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        proposed = object()
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        registry.run_plan_step(
            lease, PlanStep.LOWER, owner, registry.issue_consumer("lower"),
        )
        before = (registry.lease_state(lease), fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.transfer_owner(lease, owner, proposed, queued=True)
        self.assertEqual(before, (registry.lease_state(lease), fixture["coordinator"].count()))
        with self.assertRaises(ContractRefusal):
            registry.contain(lease, proposed)
        registry.complete(lease, owner, LeaseState.REFUSED)

    def test_static_and_live_operation_grammars_are_disjoint(self) -> None:
        fixture = build_fixture({Capability.QUERY, Capability.LIVE})
        registry = fixture["registry"]
        owner = fixture["task"][0]
        for kind in (
            OperationKind.SNAPSHOT_REGISTRATION,
            OperationKind.REFRESH,
            OperationKind.ITERATOR_HANDOFF,
        ):
            with self.subTest(kind=kind):
                with self.assertRaises(ContractRefusal):
                    registry.acquire(
                        fixture["handle"], kind, ParameterValues({}), fixture["context"],
                        resource=fixture["connection"], owner=owner,
                    )
        live_plan = Plan(
            "sales.live", "question", (), ResultShape(()),
            FrozenPlanRoot("garns.plan/1", "live", b"live"),
            PlanOrigin("SALES", "ir", "storage", 1), 2,
        )
        live_handle = registry.setup_reference_admission(live_plan, fixture["binding"])
        with self.assertRaises(ContractRefusal):
            registry.acquire(
                live_handle, OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                resource=fixture["connection"], owner=owner,
            )
        self.assertNotIn("governed_mutation", {kind.value for kind in OperationKind})
        self.assertNotIn("migration", {kind.value for kind in OperationKind})

    def test_queued_cancellation_requires_authoritative_owner_and_loses_dequeue_race(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        caller = fixture["task"][0]
        command = object()
        first = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=caller,
        )
        worker = object()
        registry.dispatch_to_worker(first, caller, command, worker, (1,))
        registry.cancel_queued(first, command)
        self.assertEqual(LeaseState.CANCELLED_CONFIRMED, registry.lease_state(first))

        second = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=caller,
        )
        authorization = registry.dispatch_to_worker(second, caller, command, worker, (1,))
        fixture["task"][0] = worker
        registry.dequeue_worker(second, command, worker, authorization)
        with self.assertRaises(ContractRefusal):
            registry.cancel_queued(second, command)
        registry.contain(second, worker)
        registry.complete(second, worker, LeaseState.REFUSED)
        self.assertEqual(0, fixture["coordinator"].count())

    def test_protocols_have_no_raw_plan_executable_signature(self) -> None:
        for protocol, method_names in (
            (AsyncConnection, ("execute", "consistent_snapshot")),
            (AsyncBackend, ("subscribe",)),
        ):
            for method_name in method_names:
                signature = inspect.signature(getattr(protocol, method_name))
                annotations = tuple(parameter.annotation for parameter in signature.parameters.values())
                self.assertNotIn(Plan, annotations)
                self.assertNotIn("Plan", repr(signature))
                self.assertNotIn("parameters", signature.parameters)


if __name__ == "__main__":
    unittest.main()
