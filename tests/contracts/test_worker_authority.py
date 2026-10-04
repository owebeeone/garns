from __future__ import annotations

import copy
import inspect
import pickle
import unittest

from garns.backends.contracts.admission import LeaseState, OperationKind
from garns.backends.contracts.values import ContractRefusal, ParameterValues, RefusalCode
from garns.backends.contracts.worker_authority import (
    EffectKnowledge, WorkerCommandAuthorization, WorkerCommandSpec,
    WorkerCommandState, WorkerEffectReservation, WorkerExitReceipt,
    WorkerStopReceipt,
)
from tests.contracts.test_admission_contracts import build_fixture


class Boom(BaseException):
    pass


class WorkerAuthorityTests(unittest.TestCase):
    def fixture(self, *, schedules=None, effect_provider=None):
        worker = object()
        fixture = build_fixture(
            command_schedule_provider=(
                (lambda kind: tuple(schedules))
                if schedules is not None
                else (lambda kind: (WorkerCommandSpec("command", (1, 2)),))
            ),
            assigned_worker_provider=lambda serial: worker,
            effect_provider=effect_provider,
        )
        fixture["worker"] = worker
        return fixture

    def issue(self, fixture):
        registry = fixture["registry"]
        caller = fixture["task"][0]
        lease = registry.acquire(
            fixture["handle"], OperationKind.EXECUTE, ParameterValues({}),
            fixture["context"], resource=fixture["connection"], owner=caller,
        )
        authorization = registry.dispatch_worker(lease)
        fixture["task"][0] = fixture["worker"]
        registry.dequeue_worker(lease, authorization)
        return lease, authorization, caller

    def finish_success(self, fixture, lease, authorization, caller, value="result"):
        registry = fixture["registry"]
        result = registry.setup_reference_worker_result(authorization, value)
        receipt = registry.worker_exit_success(authorization, result)
        stop = registry.setup_reference_worker_stop(authorization)
        registry.observe_worker_stopped(stop)
        fixture["task"][0] = caller
        self.assertEqual(value, registry.accept_worker_result(receipt))
        return receipt

    def test_private_handles_are_empty_exact_and_nontransferable(self) -> None:
        fixture = self.fixture()
        _, authorization, _ = self.issue(fixture)
        for identity_type in (
            WorkerCommandAuthorization, WorkerEffectReservation,
            WorkerExitReceipt, WorkerStopReceipt,
        ):
            self.assertEqual((), identity_type.__slots__)
            with self.assertRaises(TypeError):
                identity_type()
        for action in (
            lambda: copy.copy(authorization),
            lambda: copy.deepcopy(authorization),
            lambda: pickle.dumps(authorization),
        ):
            with self.assertRaises(TypeError):
                action()
        for name in ("context", "claims", "operation", "lease", "worker", "binding"):
            self.assertFalse(hasattr(authorization, name), name)

    def test_effect_api_has_no_callback_or_caller_identity_and_reserves_once(self) -> None:
        effects = []
        fixture = self.fixture(
            effect_provider=lambda label, ordinal: lambda: effects.append(ordinal) or ordinal,
        )
        lease, authorization, _ = self.issue(fixture)
        signature = inspect.signature(fixture["registry"].worker_issuer.run_effect)
        self.assertEqual(("authorization", "ordinal"), tuple(signature.parameters))
        self.assertEqual(1, fixture["registry"].worker_issuer.run_effect(authorization, 1))
        with self.assertRaises(ContractRefusal) as caught:
            fixture["registry"].worker_issuer.run_effect(authorization, 1)
        self.assertEqual(RefusalCode.EFFECT_ORDINAL_REUSED, caught.exception.code)
        self.assertEqual([1], effects)
        self.assertEqual(LeaseState.RUNNING, fixture["registry"].lease_state(lease))

    def test_baseexception_contains_before_escape_and_revokes_unused_effect(self) -> None:
        def provider(label, ordinal):
            def fixed():
                if ordinal == 1:
                    raise Boom()
                return ordinal
            return fixed

        fixture = self.fixture(effect_provider=provider)
        lease, authorization, _ = self.issue(fixture)
        with self.assertRaises(Boom):
            fixture["registry"].worker_issuer.run_effect(authorization, 1)
        self.assertEqual(LeaseState.CONTAINED, fixture["registry"].lease_state(lease))
        self.assertEqual(WorkerCommandState.CONTAINED, fixture["registry"].worker_command_state(authorization))
        self.assertEqual(EffectKnowledge.BEGUN_UNCERTAIN, fixture["registry"].worker_effect_knowledge(authorization))
        remaining, completed = fixture["registry"].worker_ordinals(authorization)
        self.assertEqual(frozenset(), remaining)
        self.assertEqual(frozenset(), completed)
        with self.assertRaises(ContractRefusal):
            fixture["registry"].worker_issuer.run_effect(authorization, 2)
        self.assertEqual(1, fixture["coordinator"].count())

    def test_nested_reservation_refuses_without_consuming_second_ordinal(self) -> None:
        holder = {}

        def provider(label, ordinal):
            def fixed():
                with self.assertRaises(ContractRefusal):
                    holder["registry"].worker_issuer.run_effect(holder["authorization"], 2)
                return "outer"
            return fixed

        fixture = self.fixture(effect_provider=provider)
        lease, authorization, _ = self.issue(fixture)
        holder.update(registry=fixture["registry"], authorization=authorization)
        self.assertEqual("outer", fixture["registry"].worker_issuer.run_effect(authorization, 1))
        remaining, completed = fixture["registry"].worker_ordinals(authorization)
        self.assertEqual(frozenset({2}), remaining)
        self.assertEqual(frozenset({1}), completed)
        self.assertEqual(LeaseState.RUNNING, fixture["registry"].lease_state(lease))

    def test_two_commands_have_distinct_tombstones_under_one_outer_permit(self) -> None:
        fixture = self.fixture(schedules=(
            WorkerCommandSpec("first", (1,)),
            WorkerCommandSpec("second", (1,)),
        ))
        lease, first, caller = self.issue(fixture)
        fixture["registry"].worker_issuer.run_effect(first, 1)
        first_exit = self.finish_success(fixture, lease, first, caller, "first")
        self.assertEqual(1, fixture["coordinator"].count())
        second = fixture["registry"].dispatch_worker(lease)
        self.assertIsNot(first, second)
        fixture["task"][0] = fixture["worker"]
        fixture["registry"].dequeue_worker(lease, second)
        with self.assertRaises(ContractRefusal):
            fixture["registry"].worker_issuer.run_effect(first, 1)
        fixture["registry"].worker_issuer.run_effect(second, 1)
        self.finish_success(fixture, lease, second, caller, "second")
        self.assertIs(first_exit, first_exit)
        self.assertEqual(1, fixture["coordinator"].count())

    def test_receiver_loss_contains_without_receiver_resumption(self) -> None:
        fixture = self.fixture(schedules=(WorkerCommandSpec("only", (1,)),))
        lease, authorization, _ = self.issue(fixture)
        fixture["registry"].worker_issuer.run_effect(authorization, 1)
        result = fixture["registry"].setup_reference_worker_result(authorization, "private")
        fixture["registry"].worker_exit_success(authorization, result)
        observation = fixture["registry"].setup_reference_receiving_task_done(lease)
        observed_exit = fixture["registry"].observe_receiving_task_done(observation)
        self.assertEqual(LeaseState.CONTAINED, fixture["registry"].lease_state(lease))
        stop = fixture["registry"].setup_reference_worker_stop(authorization)
        fixture["registry"].observe_worker_stopped(stop)
        fixture["registry"].complete_contained(lease)
        self.assertEqual(0, fixture["coordinator"].count())
        self.assertIs(observed_exit, fixture["registry"].observe_receiving_task_done(observation))


if __name__ == "__main__":
    unittest.main()
