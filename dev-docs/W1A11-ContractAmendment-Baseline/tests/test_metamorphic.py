"""Schema independence: a full rename must not change the normalized semantics,
and two modules with identical local names must stay apart at runtime.

The compiler is never told that a rename happened; the harness rewrites the
sources through the resolver's own reference map and the world is compiled
again from scratch.
"""

from __future__ import annotations

import difflib
import json
import unittest

from tests.support import BUILD, CORPUS, GarnsTestCase

from garns.engine import Engine, Store
from garns.live import LiveEngine
from garns.metamorphic import normalized_program_json, physical_scheme, transform
from garns.parse import garns_files, parse_paths, parse_text
from garns.resolve import resolve_files
from garns.storage import bind_world, binding_document

PRACTICE_SOURCE = BUILD / "corpus" / "worlds" / "practice"
COLLISION_SOURCE = CORPUS / "metamorphic" / "collision"
SEED = "meta-seed-7"


def resolve_texts(texts: dict[str, str]):
    return resolve_files([parse_text(text, path) for path, text in texts.items()])


class TestFullRename(GarnsTestCase):
    def setUp(self) -> None:
        self.files = parse_paths(garns_files(PRACTICE_SOURCE))
        self.program = resolve_files(self.files)
        self.transformed = transform(self.files, self.program, "PRACTICE", SEED, resolve_texts)
        self.renamed = resolve_texts(self.transformed.sources)

    def test_the_harness_actually_renames_the_world(self) -> None:
        self.assertTrue(self.transformed.mapping, "the rename must touch at least one identity")
        self.assertIn("PRACTICE", self.transformed.mapping)
        original_names = {c.qid for c in self.program.carriers}
        renamed_names = {c.qid for c in self.renamed.carriers}
        self.assertEqual(len(original_names), len(renamed_names))
        self.assertEqual(set(), original_names & renamed_names, "no original qualified name may survive")

    def test_normalized_program_json_is_unchanged_by_a_full_rename(self) -> None:
        before = normalized_program_json(self.program)
        after = normalized_program_json(self.renamed, self.transformed.forward)
        if before != after:
            diff = list(difflib.unified_diff(before.splitlines(), after.splitlines(), "original", "renamed", lineterm="", n=1))
            self.fail(f"{len(self.transformed.mapping)} identities renamed; normalized IR differs:\n" + "\n".join(diff[:60]))

    def test_the_renamed_world_still_binds_and_runs(self) -> None:
        new_world_name = self.transformed.mapping["PRACTICE"]
        binding_path = self.tempdir() / "renamed-binding.json"
        binding_path.write_text(json.dumps(self.transformed.binding, indent=1, sort_keys=True), encoding="utf-8")
        world = bind_world(self.renamed, new_world_name, binding_path)
        store, _engine, _live = self.shipped(world, clock=5)
        tables = {row[0] for row in store.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        self.assertEqual({relation.table for relation in world.storage.relations.values()} - tables, set())

    def test_generated_physical_names_change_where_the_binding_changes(self) -> None:
        original = bind_world(self.program, "PRACTICE", PRACTICE_SOURCE / "storage-PRACTICE.json")
        binding_path = self.tempdir() / "renamed-binding.json"
        binding_path.write_text(json.dumps(self.transformed.binding, indent=1, sort_keys=True), encoding="utf-8")
        renamed = bind_world(self.renamed, self.transformed.mapping["PRACTICE"], binding_path)
        old_tables = {relation.table for relation in original.storage.relations.values()}
        new_tables = {relation.table for relation in renamed.storage.relations.values()}
        self.assertEqual(set(), old_tables & new_tables)


class TestShortNameCollision(GarnsTestCase):
    """Two modules declare the same local names; runtime keys must stay distinct."""

    WORLDS = ("ALPHA", "BETA")

    def setUp(self) -> None:
        self.program = resolve_files(parse_paths(garns_files(COLLISION_SOURCE)))
        self.tmp = self.tempdir()
        self.runtimes = {name: self.build(name) for name in self.WORLDS}

    def build(self, world_name: str):
        binding_path = self.tmp / f"collision-{world_name}.json"
        binding_path.write_text(json.dumps(binding_document(self.program, world_name, physical_scheme(world_name))), encoding="utf-8")
        world = bind_world(self.program, world_name, binding_path)
        store = Store(world, ":memory:")
        self.addCleanup(store.close)
        store.ship()
        engine = Engine(store, clock=lambda: 1)
        live = LiveEngine(engine)
        module = world_name.lower()
        with engine.transaction("governed", "s") as tx:
            root = tx.mint(f"{module}.Root", {f"{module}.Root.code": "R"})
            tx.mint(f"{module}.Item", {f"{module}.Item.code": "X", f"{module}.Item.amount": 10, f"{module}.Item.holder": root})
        instance = live.subscribe(f"{module}.heavy", {"floor": 5}, scope=root)
        return {"world": world, "engine": engine, "live": live, "instance": instance, "root": root, "module": module}

    def test_the_two_modules_really_share_their_local_names(self) -> None:
        locals_by_module = {}
        for carrier in self.program.carriers:
            locals_by_module.setdefault(carrier.module, set()).add(carrier.name)
        modules = [m for m in locals_by_module if m in {w.lower() for w in self.WORLDS}]
        self.assertEqual(2, len(modules))
        self.assertEqual(locals_by_module[modules[0]], locals_by_module[modules[1]])

    def test_index_keys_stay_distinct_under_qualified_identities(self) -> None:
        keys = {name: set(runtime["live"].index) for name, runtime in self.runtimes.items()}
        self.assertTrue(all(keys.values()))
        self.assertTrue(keys["ALPHA"].isdisjoint(keys["BETA"]))
        for name, entries in keys.items():
            with self.subTest(world=name):
                self.assertTrue(all(carrier.startswith(f"{name.lower()}.") for _partition, carrier, _field in entries))

    def test_a_write_in_one_module_routes_only_that_modules_instance(self) -> None:
        alpha, beta = self.runtimes["ALPHA"], self.runtimes["BETA"]
        with alpha["engine"].transaction("governed", "w") as tx:
            tx.change("alpha.Item", 1, {"alpha.Item.amount": 20})
        self.assertEqual({alpha["instance"].id: True}, alpha["live"].last_routing)
        self.assertEqual({}, beta["live"].last_routing)

    def test_same_named_reads_return_results_selected_by_qualified_identity(self) -> None:
        alpha, beta = self.runtimes["ALPHA"], self.runtimes["BETA"]
        with alpha["engine"].transaction("governed", "w") as tx:
            tx.change("alpha.Item", 1, {"alpha.Item.amount": 20})
        self.assertEqual([{"code": "X", "amount": 20}], alpha["instance"].rows())
        self.assertEqual([{"code": "X", "amount": 10}], beta["instance"].rows())


if __name__ == "__main__":
    unittest.main()
