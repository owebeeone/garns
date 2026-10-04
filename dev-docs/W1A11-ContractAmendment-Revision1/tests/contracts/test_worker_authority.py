from __future__ import annotations

import copy
import pickle
import unittest

from garns.backends.contracts.admission import LeaseState, OperationKind
from garns.backends.contracts.semantic import BindingIdentity
from garns.backends.contracts.values import ContractRefusal, ParameterValues, RefusalCode
from garns.backends.contracts.worker_authority import WorkerAuthorizationIssuer, WorkerCommandAuthorization
from tests.contracts.test_admission_contracts import build_fixture


class WorkerAuthorityTests(unittest.TestCase):
    def issue(self, fixture, *, ordinals=(1, 2)):
        registry = fixture["registry"]
        caller = fixture["task"][0]
        worker = object()
        command = object()
        lease = registry.acquire(
            fixture["handle"],
            OperationKind.EXECUTE,
            ParameterValues({}),
            fixture["context"],
            resource=fixture["connection"],
            owner=caller,
        )
        operation = registry.operation(lease)
        issuer = WorkerAuthorizationIssuer(fixture["authority"], registry.worker_operation_live)
        authorization = issuer.issue_for_dispatch(
            fixture["context"],
            fixture["capabilities"].__iter__().__next__(),
            operation.runtime_identity,
            operation,
            lease,
            command,
            worker,
            fixture["binding"],
            ordinals,
        )
        registry.transfer_owner(lease, caller, worker, queued=True)
        registry.transfer_owner(lease, worker, worker)
        return locals()

    def test_private_handle_is_empty_and_public_context_stays_task_bound(self) -> None:
        fixture = build_fixture()
        issued = self.issue(fixture)
        authorization = issued["authorization"]
        self.assertEqual(("__weakref__",), WorkerCommandAuthorization.__slots__)
        for name in (
            "context", "claims", "runtime", "operation", "lease", "command", "worker",
            "binding", "ordinals", "issuer", "registry",
        ):
            self.assertFalse(hasattr(authorization, name), name)
        for operation in (
            lambda: copy.copy(authorization),
            lambda: copy.deepcopy(authorization),
            lambda: pickle.dumps(authorization),
        ):
            with self.assertRaises(TypeError):
                operation()
        fixture["task"][0] = issued["worker"]
        with self.assertRaises(ContractRefusal):
            fixture["authority"].validate(
                fixture["context"],
                scope=fixture["scope"],
                capability=fixture["capabilities"].__iter__().__next__(),
            )

    def test_exact_worker_effect_consumes_ordinal_immediately_once(self) -> None:
        fixture = build_fixture()
        issued = self.issue(fixture)
        fixture["task"][0] = issued["worker"]
        effects = []

        def run(ordinal, effect):
            return issued["issuer"].run_effect(
                issued["authorization"],
                issued["operation"].runtime_identity,
                issued["operation"],
                issued["lease"],
                issued["command"],
                issued["worker"],
                fixture["binding"],
                ordinal,
                effect,
            )

        self.assertEqual("effect", run(1, lambda: effects.append(1) or "effect"))
        self.assertEqual([1], effects)
        with self.assertRaises(ContractRefusal) as caught:
            run(1, lambda: effects.append(2))
        self.assertEqual(RefusalCode.EFFECT_ORDINAL_REUSED, caught.exception.code)
        self.assertEqual([1], effects)

    def test_expiry_invalidation_revocation_and_wrong_bindings_have_zero_effects(self) -> None:
        attacks = ("expiry", "invalidation", "revocation", "worker", "command", "runtime", "generation")
        for attack in attacks:
            with self.subTest(attack=attack):
                fixture = build_fixture()
                issued = self.issue(fixture, ordinals=(1,))
                fixture["task"][0] = issued["worker"]
                worker = issued["worker"]
                command = issued["command"]
                runtime = issued["operation"].runtime_identity
                binding = fixture["binding"]
                if attack == "expiry":
                    fixture["now"][0] = 10.0
                elif attack == "invalidation":
                    fixture["authority"].invalidate(fixture["context"])
                elif attack == "revocation":
                    issued["issuer"].revoke(issued["authorization"])
                elif attack == "worker":
                    worker = object()
                elif attack == "command":
                    command = object()
                elif attack == "runtime":
                    runtime = object()
                elif attack == "generation":
                    binding = BindingIdentity(fixture["scope"], "ir", "storage", 2)
                effects = []
                with self.assertRaises(ContractRefusal):
                    issued["issuer"].run_effect(
                        issued["authorization"], runtime, issued["operation"], issued["lease"],
                        command, worker, binding, 1, lambda: effects.append("called"),
                    )
                self.assertEqual([], effects)

    def test_hard_fence_refuses_new_effect_but_retains_containment(self) -> None:
        fixture = build_fixture()
        issued = self.issue(fixture, ordinals=(1,))
        fixture["registry"].start_close(fixture["connection"], hard=True)
        effects = []
        with self.assertRaises(ContractRefusal):
            issued["issuer"].run_effect(
                issued["authorization"],
                issued["operation"].runtime_identity,
                issued["operation"],
                issued["lease"],
                issued["command"],
                issued["worker"],
                fixture["binding"],
                1,
                lambda: effects.append("called"),
            )
        self.assertEqual([], effects)
        self.assertEqual(LeaseState.CONTAINED, fixture["registry"].lease_state(issued["lease"]))
        self.assertEqual(1, fixture["coordinator"].count())


if __name__ == "__main__":
    unittest.main()
