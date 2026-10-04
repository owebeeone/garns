from __future__ import annotations

import copy
from dataclasses import dataclass
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
    coordinator.begin_activation()
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
        calls = []

        def acquire():
            return registry.acquire(
                fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
                resource=fixture["connection"], owner=owner,
            )

        lease = acquire()
        result = registry.run_plan_step(
            lease, PlanStep.LOWER, owner, lambda plan: calls.append(plan.read_qid) or ("sql",),
        )
        self.assertEqual(("sql",), result)
        self.assertEqual(["sales.open"], calls)

        @dataclass
        class Wrapper:
            payload: object

        for escape in (
            lambda plan: plan,
            lambda plan: plan.root,
            lambda plan: Wrapper(plan),
            lambda plan: (lambda: plan),
        ):
            candidate = acquire()
            with self.assertRaises(TypeError):
                registry.run_plan_step(candidate, PlanStep.LOWER, owner, escape)

    def test_authority_is_revalidated_between_steps_and_before_publication(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        owner = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=owner,
        )
        registry.run_plan_step(lease, PlanStep.LOWER, owner, lambda plan: "sql")
        fixture["now"][0] = 10.0
        with self.assertRaises(ContractRefusal):
            registry.run_plan_step(lease, PlanStep.PUBLICATION, owner, lambda plan: "rows")
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
        registry.transfer_owner(lease, owner, worker, queued=True)
        self.assertEqual(LeaseState.QUEUED, registry.lease_state(lease))
        with self.assertRaises(ContractRefusal):
            registry.transfer_owner(lease, owner, object())
        registry.transfer_owner(lease, worker, worker)
        registry.complete(lease, worker, LeaseState.SUCCEEDED)
        registry.complete(lease, worker, LeaseState.SUCCEEDED)
        self.assertEqual(0, fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal) as caught:
            registry.complete(lease, worker, LeaseState.REFUSED)
        self.assertEqual(RefusalCode.OPERATION_OUTCOME_CONFLICT, caught.exception.code)

    def test_queued_cancellation_requires_authoritative_owner_and_loses_dequeue_race(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        caller = fixture["task"][0]
        command = object()
        first = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=caller,
        )
        registry.transfer_owner(first, caller, command, queued=True)
        registry.cancel_queued(first, command)
        self.assertEqual(LeaseState.CANCELLED_CONFIRMED, registry.lease_state(first))

        second = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}), fixture["context"],
            resource=fixture["connection"], owner=caller,
        )
        worker = object()
        registry.transfer_owner(second, caller, command, queued=True)
        registry.transfer_owner(second, command, worker)
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


if __name__ == "__main__":
    unittest.main()
