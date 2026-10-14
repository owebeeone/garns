from __future__ import annotations

import ast
import inspect
from pathlib import Path
import unittest

from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry  # noqa: F401
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


# Accepted coordinator call shapes (design §9 membership, §11 proof and
# effect-begun transitions, permits and the frozen-attempt barrier).  The
# formal seam must declare exactly these members, and every coordinator call
# site in the registry must be one of them.
COORDINATOR_ATTRIBUTES = ("deployment", "binding", "state", "admission_epoch")
COORDINATOR_METHODS = (
    "prepare_lifetime_open", "join_runtime", "close_unjoined",
    "witness_local_drain", "witness_local_close", "request_leave",
    "finalize_leave", "membership_state",
    "acquire_shared", "release_shared", "add_buffer", "release_buffer",
    "exchange_buffer_for_shared", "permit_live", "count",
    "begin_drain", "barrier_allowed", "acknowledge_barrier", "begin_migration",
    "begin_migration_effect", "observe_request_released", "reopen_no_effect",
    "no_effect_reopen_complete", "attempt_product", "publish_generation",
    "mark_indeterminate", "recover_migration",
)
MEMBERSHIP_AND_PROOF_METHODS = (
    "join_runtime", "request_leave", "finalize_leave", "close_unjoined",
    "witness_local_drain", "witness_local_close",
    "observe_request_released", "reopen_no_effect", "begin_migration_effect",
    "recover_migration",
)
# Every public registry entry that can reach the containment routine must
# validate one of these before any mutation: the live receiver, the exact
# assigned worker, a trusted registry-owned observation or cause record, or a
# trusted barrier/fence/invalidation event (design §5.2 three trusted sources,
# §7 row 1).  Markers are checked in the method or in the private helpers it
# calls directly.
AUTHORITY_MARKERS = {
    "receiver": (
        "self._lease_for_owner(", "self._owner_matches(", "self._presentation_current(",
        "self._require_publication_ready(", "self._authority.is_current_task(record.receiving_task)",
    ),
    "worker": ("self._validate_worker_barriers(", "self._authority.is_current_task(command.worker)"),
    "observation": ("self._observations.get(", "self._exit_receipts.get(", "self._failures.get("),
    "barrier": ("self._coordinator.barrier_allowed(", "self._descendant_names(", "self._registry_epoch += 1"),
}
CONTAINMENT_ENTRIES = {
    "run_plan_step": "receiver", "issue_derived_command": "receiver", "run_derived_command": "receiver",
    "dispatch_worker": "receiver", "request_worker_cancel": "receiver", "accept_worker_result": "receiver",
    "setup_reference_initial_snapshot": "receiver", "register_subscription": "receiver",
    "setup_reference_refresh_candidate": "receiver", "publish_refresh_buffer": "receiver",
    "commit_refresh": "receiver", "prepare_delivery_publication": "receiver",
    "settle_delivery_success": "receiver",
    "dequeue_worker": "worker", "run_worker_effect": "worker", "worker_exit_success": "worker",
    "worker_exit_failure": "worker", "run_worker_cleanup": "worker",
    "observe_receiving_task_done": "observation", "begin_delivery_non_success": "observation",
    "start_close": "barrier", "migration_queue_barrier": "barrier", "revoke_generation": "barrier",
}


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
            "run_worker_cleanup": ("self", "authorization", "step"),
            "request_worker_cancel": ("self", "lease"),
            "observe_receiving_task_done": ("self", "observation"),
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
        # The exact set of entries that take a worker authorization: nothing
        # outside this enumeration may accept one (design §12 enumeration).
        authorization_entries = {
            node.name for node in owner.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and "authorization" in {argument.arg for argument in node.args.args}
        }
        self.assertEqual({
            "dequeue_worker", "run_worker_effect", "setup_reference_worker_result",
            "setup_reference_worker_failure", "worker_exit_success", "worker_exit_failure",
            "run_worker_cleanup", "setup_reference_worker_stop", "worker_command_state",
            "worker_effect_knowledge", "worker_ordinals", "worker_exit_facts",
            "worker_cleanup_step", "_command_for", "_worker_context_owner",
        }, authorization_entries)
        # IR22: the executor facade offers no cancellation route.
        self.assertFalse(hasattr(WorkerAuthorizationIssuer, "revoke"))
        self.assertEqual(
            ("run_effect", "context_owner"),
            tuple(name for name in vars(WorkerAuthorizationIssuer) if not name.startswith("_")),
        )
        self.assertNotIn("_revoke_worker_authorization", {
            node.name for node in owner.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        })

    def test_public_containment_entries_validate_authority_first(self) -> None:
        tree = parsed("lifetime_reference.py")
        owner = class_node(tree, "ReferenceLifetimeRegistry")
        methods = {
            node.name: node for node in owner.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

        def callees(method):
            return {
                node.func.attr for node in ast.walk(method)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "self"
                and node.func.attr in methods
            }

        graph = {name: callees(method) for name, method in methods.items()}
        reaching = {"_contain_lease"}
        changed = True
        while changed:
            changed = False
            for name, called in graph.items():
                if name not in reaching and called & reaching:
                    reaching.add(name)
                    changed = True
        public = {name for name in reaching if not name.startswith("_")}
        self.assertEqual(set(CONTAINMENT_ENTRIES), public)
        for name, authority in CONTAINMENT_ENTRIES.items():
            with self.subTest(entry=name, authority=authority):
                sources = [ast.unparse(methods[name])]
                sources.extend(ast.unparse(methods[helper]) for helper in graph[name] if helper.startswith("_"))
                text = "\n".join(sources)
                self.assertTrue(
                    any(marker in text for marker in AUTHORITY_MARKERS[authority]),
                    f"{name} must validate a {authority} before reaching containment",
                )
        self.assertEqual(
            ("authorization", "ordinal"),
            tuple(inspect.signature(WorkerAuthorizationIssuer.run_effect).parameters)[1:],
        )

    def test_terminalizers_are_exactly_enumerated_and_gated(self) -> None:
        tree = parsed("lifetime_reference.py")
        owner = class_node(tree, "ReferenceLifetimeRegistry")

        def calls(method, attribute):
            return [
                node for node in ast.walk(method)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == attribute
            ]

        methods = {
            node.name: node for node in owner.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        terminalizers = {name for name, method in methods.items() if calls(method, "_terminalize")}
        self.assertEqual({
            # generic non-delivery success: all three require the one
            # publication precondition (IR1, IR2)
            "run_plan_step", "register_subscription", "_commit_refresh_record",
            # refresh dispositions (IR11)
            "settle_contained_refresh", "_dispose_refresh",
            # specialized delivery settlement (design §8)
            "settle_delivery_success", "settle_delivery_non_success",
            # generic completion by owner or containment owner (design §6)
            "complete", "complete_contained",
            # authoritative queue removal of a non-delivery (design §4.1)
            "_contain_lease",
        }, terminalizers)
        for name in ("run_plan_step", "register_subscription", "_commit_refresh_record"):
            with self.subTest(gated=name):
                source = ast.unparse(methods[name])
                self.assertTrue(
                    "_require_publication_ready(" in source or "_publication_ready(" in source,
                    f"{name} must require the publication precondition",
                )
        self.assertIn("_require_publication_ready(", ast.unparse(methods["prepare_delivery_publication"]))
        for name in ("complete", "complete_contained"):
            with self.subTest(refuses_handoff=name):
                self.assertIn("OperationKind.ITERATOR_HANDOFF", ast.unparse(methods[name]))
        for call in calls(methods["_contain_lease"], "_terminalize"):
            self.assertNotIn("SUCCEEDED", ast.unparse(call))
        self.assertEqual([], calls(methods["_dispose_refresh"], "_cancel_or_remove"))
        self.assertNotIn("_cancel_or_remove", methods)

    def test_containment_writes_live_in_one_routine(self) -> None:
        tree = parsed("lifetime_reference.py")
        owner = class_node(tree, "ReferenceLifetimeRegistry")
        contained_writers, retiring_writers, containment_owner_writers = set(), set(), set()
        for method in (
            node for node in owner.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ):
            for node in ast.walk(method):
                if not isinstance(node, ast.Assign):
                    continue
                value = ast.unparse(node.value)
                for target in node.targets:
                    if not isinstance(target, ast.Attribute):
                        continue
                    if target.attr == "state" and value == "LeaseState.CONTAINED":
                        contained_writers.add(method.name)
                    if target.attr == "state" and value == "LeaseState.RETIRING_HANDOFF":
                        retiring_writers.add(method.name)
                    if target.attr == "owner" and value.endswith(".containment_owner"):
                        containment_owner_writers.add(method.name)
        self.assertEqual({"_contain_lease"}, contained_writers)
        self.assertEqual({"_begin_retirement"}, retiring_writers)
        self.assertEqual({"_contain_lease", "_begin_retirement"}, containment_owner_writers)
        # Terminal leases are absorbing and a retiring handoff keeps its label:
        # the routine's first two statements return before any write.
        routine = function_node(owner, "_contain_lease")
        guards = [node for node in routine.body if isinstance(node, ast.If)][:2]
        self.assertEqual(
            ["record.state.terminal", "record.delivery_retirement is not None"],
            [ast.unparse(node.test) for node in guards],
        )
        for guard in guards:
            self.assertEqual(1, len(guard.body))
            self.assertIsInstance(guard.body[0], ast.Return)

    def test_coordinator_protocol_members_equal_accepted_call_shapes(self) -> None:
        protocol = class_node(parsed("lifetime.py"), "SharedGenerationCoordinator")
        methods = {
            node.name for node in protocol.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        attributes = {
            node.target.id for node in protocol.body
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
        }
        self.assertEqual(set(COORDINATOR_METHODS), methods)
        self.assertEqual(set(COORDINATOR_ATTRIBUTES), attributes)
        self.assertTrue(set(MEMBERSHIP_AND_PROOF_METHODS) <= methods)
        begin_migration = function_node(protocol, "begin_migration")
        self.assertEqual("'MigrationRequestIdentity'", ast.unparse(begin_migration.returns))
        reference = class_node(parsed("generation_reference.py"), "ReferenceGenerationCoordinator")
        self.assertEqual("MigrationRequestIdentity", ast.unparse(function_node(reference, "begin_migration").returns))
        registry_tree = parsed("lifetime_reference.py")
        call_sites = {
            node.attr for node in ast.walk(registry_tree)
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute)
            and isinstance(node.value.value, ast.Name) and node.value.value.id == "self"
            and node.value.attr == "_coordinator"
        }
        self.assertTrue(call_sites, "the registry must call the coordinator through the seam")
        self.assertEqual(set(), call_sites - methods - attributes, "every coordinator call site is a protocol member")
        registry = class_node(registry_tree, "ReferenceLifetimeRegistry")
        init = function_node(registry, "__init__")
        coordinator_argument = next(argument for argument in init.args.args if argument.arg == "coordinator")
        self.assertEqual("SharedGenerationCoordinator", ast.unparse(coordinator_argument.annotation))
        self.assertIn("isinstance(coordinator, SharedGenerationCoordinator)", ast.unparse(init))

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
        self.assertEqual(["_terminalize"], release_sites)

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
