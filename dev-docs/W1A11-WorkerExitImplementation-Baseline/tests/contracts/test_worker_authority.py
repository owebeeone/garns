from __future__ import annotations

import copy
import pickle
import unittest

from garns.backends.contracts.admission import LeaseState, OperationKind
from garns.backends.contracts.semantic import BindingIdentity
from garns.backends.contracts.values import ContractRefusal, ParameterValues, RefusalCode
from garns.backends.contracts.worker_authority import WorkerCommandAuthorization
from tests.contracts.test_admission_contracts import build_fixture


class WorkerAuthorityTests(unittest.TestCase):
    def issue(self, fixture, *, ordinals=(1, 2)):
        registry = fixture["registry"]
        caller = fixture["task"][0]
        worker = object()
        command = object()
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection"], owner=caller,
        )
        operation = registry.operation(lease)
        authorization = registry.dispatch_to_worker(
            lease, caller, command, worker, tuple(ordinals),
        )
        fixture["task"][0] = worker
        registry.dequeue_worker(lease, command, worker, authorization)
        issuer = registry.worker_issuer
        return locals()

    def run_effect(self, fixture, issued, ordinal, effect, *, command=None, worker=None,
                   binding=None, authorization=None):
        return issued["issuer"].run_effect(
            issued["authorization"] if authorization is None else authorization,
            issued["operation"].runtime_identity,
            issued["operation"], issued["lease"],
            issued["command"] if command is None else command,
            issued["worker"] if worker is None else worker,
            fixture["binding"] if binding is None else binding,
            ordinal, effect,
        )

    def test_private_handle_is_empty_and_public_context_remains_task_bound(self) -> None:
        fixture = build_fixture()
        issued = self.issue(fixture)
        authorization = issued["authorization"]
        self.assertEqual(("__weakref__",), WorkerCommandAuthorization.__slots__)
        for name in ("context", "claims", "operation", "lease", "command", "worker", "binding"):
            self.assertFalse(hasattr(authorization, name), name)
        for action in (
            lambda: copy.copy(authorization),
            lambda: copy.deepcopy(authorization),
            lambda: pickle.dumps(authorization),
        ):
            with self.assertRaises(TypeError):
                action()
        with self.assertRaises(ContractRefusal):
            fixture["authority"].validate(
                fixture["context"], scope=fixture["scope"],
                capability=next(iter(fixture["capabilities"])),
            )

    def test_exact_record_consumes_each_ordinal_before_effect_once(self) -> None:
        fixture = build_fixture()
        issued = self.issue(fixture)
        effects = []
        self.assertEqual("effect", self.run_effect(
            fixture, issued, 1, lambda: effects.append(1) or "effect",
        ))
        with self.assertRaises(ContractRefusal) as caught:
            self.run_effect(fixture, issued, 1, lambda: effects.append(2))
        self.assertEqual(RefusalCode.EFFECT_ORDINAL_REUSED, caught.exception.code)
        self.assertEqual([1], effects)

    def test_unrecorded_or_wrong_queue_tuple_has_zero_effect(self) -> None:
        for attack in ("worker", "command", "authorization", "generation"):
            with self.subTest(attack=attack):
                fixture = build_fixture()
                issued = self.issue(fixture, ordinals=(1,))
                kwargs = {}
                if attack == "worker":
                    kwargs["worker"] = object()
                elif attack == "command":
                    kwargs["command"] = object()
                elif attack == "authorization":
                    kwargs["authorization"] = object.__new__(WorkerCommandAuthorization)
                else:
                    kwargs["binding"] = BindingIdentity(fixture["scope"], "ir", "storage", 2)
                effects = []
                with self.assertRaises(ContractRefusal):
                    self.run_effect(fixture, issued, 1, lambda: effects.append("called"), **kwargs)
                self.assertEqual([], effects)

    def test_dequeue_compares_atomic_command_worker_authorization_tuple(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        caller = fixture["task"][0]
        command = object()
        worker = object()
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection"], owner=caller,
        )
        authorization = registry.dispatch_to_worker(lease, caller, command, worker, (1,))
        before = (registry.lease_state(lease), fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.dequeue_worker(lease, command, object(), authorization)
        self.assertEqual(before, (registry.lease_state(lease), fixture["coordinator"].count()))
        fixture["task"][0] = worker
        registry.dequeue_worker(lease, command, worker, authorization)
        self.assertEqual(LeaseState.RUNNING, registry.lease_state(lease))

    def test_issuing_task_cannot_impersonate_assigned_worker(self) -> None:
        fixture = build_fixture()
        registry = fixture["registry"]
        caller = fixture["task"][0]
        command = object()
        worker = object()
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection"], owner=caller,
        )
        operation = registry.operation(lease)
        authorization = registry.dispatch_to_worker(lease, caller, command, worker, (1,))
        before = (registry.lease_state(lease), fixture["coordinator"].count())
        with self.assertRaises(ContractRefusal):
            registry.dequeue_worker(lease, command, worker, authorization)
        self.assertEqual(before, (registry.lease_state(lease), fixture["coordinator"].count()))
        fixture["task"][0] = worker
        registry.dequeue_worker(lease, command, worker, authorization)
        fixture["task"][0] = caller
        effects = []
        with self.assertRaises(ContractRefusal):
            registry.worker_issuer.run_effect(
                authorization, operation.runtime_identity, operation, lease,
                command, worker, fixture["binding"], 1,
                lambda: effects.append("called"),
            )
        self.assertEqual([], effects)
        fixture["task"][0] = worker
        registry.worker_issuer.run_effect(
            authorization, operation.runtime_identity, operation, lease,
            command, worker, fixture["binding"], 1,
            lambda: effects.append("called"),
        )
        self.assertEqual(["called"], effects)

    def test_original_authority_expiry_invalidation_and_revocation_refuse(self) -> None:
        for attack in ("expiry", "invalidation", "revocation"):
            with self.subTest(attack=attack):
                fixture = build_fixture()
                issued = self.issue(fixture, ordinals=(1,))
                if attack == "expiry":
                    fixture["now"][0] = 10.0
                elif attack == "invalidation":
                    fixture["authority"].invalidate(fixture["context"])
                else:
                    issued["issuer"].revoke(issued["authorization"])
                effects = []
                with self.assertRaises(ContractRefusal):
                    self.run_effect(fixture, issued, 1, lambda: effects.append("called"))
                self.assertEqual([], effects)

    def test_hard_fence_retains_contained_charge(self) -> None:
        fixture = build_fixture()
        issued = self.issue(fixture, ordinals=(1,))
        fixture["registry"].start_close(fixture["connection"], hard=True)
        effects = []
        with self.assertRaises(ContractRefusal):
            self.run_effect(fixture, issued, 1, lambda: effects.append("called"))
        self.assertEqual([], effects)
        self.assertEqual(LeaseState.CONTAINED, fixture["registry"].lease_state(issued["lease"]))
        self.assertEqual(1, fixture["coordinator"].count())


if __name__ == "__main__":
    unittest.main()
