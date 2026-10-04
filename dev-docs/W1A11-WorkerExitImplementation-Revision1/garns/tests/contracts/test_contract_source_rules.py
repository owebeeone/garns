from __future__ import annotations

import ast
import inspect
from pathlib import Path
import unittest

from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.worker_authority import WorkerAuthorizationIssuer


ROOT = Path(__file__).resolve().parents[2]
CONTRACTS = ROOT / "src" / "garns" / "backends" / "contracts"
OWNED_SOURCE = (
    "admission.py",
    "authority.py",
    "consumers.py",
    "worker_authority.py",
    "lifetime_reference.py",
    "buffer_reference.py",
    "snapshot_reference.py",
    "generation_reference.py",
    "migration_reference.py",
    "lifetime.py",
    "protocols.py",
    "values.py",
    "__init__.py",
)


def parsed(name: str) -> ast.Module:
    return ast.parse((CONTRACTS / name).read_text(encoding="utf-8"), filename=name)


def class_node(tree: ast.Module, name: str) -> ast.ClassDef:
    return next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == name)


def function_node(owner: ast.ClassDef, name: str) -> ast.FunctionDef | ast.AsyncFunctionDef:
    return next(
        node for node in owner.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    )


class ContractSourceRules(unittest.TestCase):
    def test_every_owned_contract_source_parses_and_has_no_conditional_branch_directives(self) -> None:
        for name in OWNED_SOURCE:
            with self.subTest(name=name):
                source = (CONTRACTS / name).read_text(encoding="utf-8")
                ast.parse(source, filename=name)
                self.assertNotIn("#[cfg", source)
                self.assertNotIn("#if", source)

    def test_execution_protocols_never_accept_or_return_raw_plan(self) -> None:
        tree = parsed("protocols.py")
        annotation_nodes = tuple(
            node.annotation
            for node in ast.walk(tree)
            if isinstance(node, (ast.arg, ast.AnnAssign)) and node.annotation is not None
        ) + tuple(
            node.returns
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns is not None
        )
        raw_plan_names = tuple(
            node for annotation in annotation_nodes for node in ast.walk(annotation)
            if isinstance(node, ast.Name) and node.id == "Plan"
        )
        self.assertFalse(raw_plan_names)
        source = (CONTRACTS / "protocols.py").read_text(encoding="utf-8")
        self.assertNotIn("unwrap", source.lower())

    def test_worker_entries_have_no_callback_or_caller_identity_override(self) -> None:
        expected = {
            "dispatch_worker": ("self", "lease"),
            "dequeue_worker": ("self", "lease", "authorization"),
            "run_worker_effect": ("self", "authorization", "ordinal"),
            "worker_exit_success": ("self", "authorization", "result"),
            "worker_exit_failure": ("self", "authorization", "failure"),
            "request_worker_cancel": ("self", "lease"),
            "observe_worker_stopped": ("self", "receipt"),
            "accept_worker_result": ("self", "receipt"),
        }
        tree = parsed("lifetime_reference.py")
        owner = class_node(tree, "ReferenceLifetimeRegistry")
        for name, parameters in expected.items():
            with self.subTest(name=name):
                node = function_node(owner, name)
                actual = tuple(argument.arg for argument in node.args.args)
                self.assertEqual(parameters, actual)
                self.assertFalse({"callback", "worker", "task", "stop", "proof"} & set(actual))
        self.assertEqual(
            ("authorization", "ordinal"),
            tuple(inspect.signature(WorkerAuthorizationIssuer.run_effect).parameters)[1:],
        )

    def test_worker_facade_has_no_secondary_mutable_ledger(self) -> None:
        tree = parsed("worker_authority.py")
        owner = class_node(tree, "WorkerAuthorizationIssuer")
        forbidden = (ast.Dict, ast.List, ast.Set, ast.DictComp, ast.ListComp, ast.SetComp)
        assigned_values = tuple(
            node.value for node in ast.walk(owner)
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None
        )
        self.assertFalse(any(isinstance(value, forbidden) for value in assigned_values))
        source = ast.unparse(owner)
        for token in ("command_ledger", "active_command_serial", "active_reservation", "LeaseState"):
            self.assertNotIn(token, source)
        lifetime = class_node(parsed("lifetime_reference.py"), "_LeaseRecord")
        fields = {
            node.target.id
            for node in lifetime.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        }
        self.assertTrue({"command_ledger", "active_command_serial", "containment_owner"} <= fields)

    def test_shared_permit_release_is_centralized_in_terminalizer(self) -> None:
        tree = parsed("lifetime_reference.py")
        owner = class_node(tree, "ReferenceLifetimeRegistry")
        release_sites = []
        for method in (
            node for node in owner.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            for node in ast.walk(method):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "release_shared"
                ):
                    release_sites.append(method.name)
        self.assertEqual(["_acquire", "_terminalize"], release_sites)

    def test_cursor_membership_and_phase_proof_mutations_have_one_owner_each(self) -> None:
        cursor_stores = set()
        participant_stores = set()
        proof_issuers = set()
        for name in OWNED_SOURCE:
            tree = parsed(name)
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                    if node.attr in {"produced_through", "delivered_through"}:
                        cursor_stores.add(name)
                    if node.attr == "_participants":
                        participant_stores.add(name)
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "issue_no_effect_proof"
                ):
                    proof_issuers.add(name)
        self.assertEqual({"buffer_reference.py"}, cursor_stores)
        self.assertEqual({"generation_reference.py"}, participant_stores)
        self.assertEqual({"generation_reference.py"}, proof_issuers)
        generation = (CONTRACTS / "generation_reference.py").read_text(encoding="utf-8")
        self.assertIn("def observe_request_released(", generation)
        self.assertNotIn("setup_reference_no_effect_proof", generation)
        self.assertNotIn("released_digest", generation)

    def test_delivery_terminalization_has_only_specialized_success_and_retirement_calls(self) -> None:
        tree = parsed("lifetime_reference.py")
        owner = class_node(tree, "ReferenceLifetimeRegistry")
        specialized = {
            "settle_delivery_success",
            "settle_delivery_non_success",
        }
        terminalizers = set()
        for method in (
            node for node in owner.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            if any(
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "_terminalize"
                for node in ast.walk(method)
            ):
                terminalizers.add(method.name)
        self.assertTrue(specialized <= terminalizers)
        complete = ast.unparse(function_node(owner, "complete"))
        self.assertIn("OperationKind.ITERATOR_HANDOFF", complete)
        self.assertIn("specialized delivery settlement", complete)


if __name__ == "__main__":
    unittest.main()
