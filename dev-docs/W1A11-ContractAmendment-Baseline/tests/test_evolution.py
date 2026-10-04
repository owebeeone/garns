"""Evolution: classify, migrate and reopen a real store across five generations.

The store is a real in-memory SQLite database that is shipped at g1, seeded,
and then migrated one generation at a time. Physical names are read back out
of the world's storage binding, never spelled here.
"""

from __future__ import annotations

import unittest

from tests.support import CORPUS, GarnsTestCase, program_of, world_ir

from garns.evolution import classify, migrate, open_store
from garns.lower_sqlite import q
from garns.mutants import observe_scenario
from garns.parse import parse_text
from garns.resolve import resolve_files

GENERATIONS = [("PRACTICE", f"corpus/worlds/evolution/g{n}") for n in range(1, 6)]
SCENARIOS = CORPUS / "mutants" / "scenarios"
SHIP_REFUSALS = ("RETIREMENT_POLICY_REQUIRED", "RENAME_TARGET_UNKNOWN", "RETYPE_KEY_EQUALITY",
                 "ACCESSOR_BREAKING_UNACKNOWLEDGED", "RESTORE_DATA_UNAVAILABLE", "MOVE_HOME_INCONSISTENT")


class TestGenerationWalk(GarnsTestCase):
    """g1 -> g5 on one store: classify, migrate, reopen at every step."""

    def setUp(self) -> None:
        self.worlds = [world_ir(name, rel) for name, rel in GENERATIONS]
        self.store, self.engine, _live = self.shipped_at_g1()
        self.seeded_name = "Ann"
        with self.engine.transaction("governed", "seed") as tx:
            owner = tx.mint("people.User", {"people.User.email": "a@x"})
            self.client = tx.mint("clients.Client", {"clients.Client.user_name": self.seeded_name,
                                                     "clients.Client.owner": owner})
        self.steps = self.walk()

    def shipped_at_g1(self):
        from garns.engine import Engine, Store

        store = Store(self.worlds[0], ":memory:")
        self.addCleanup(store.close)
        store.ship(generation=1)
        return store, Engine(store, clock=lambda: 3), None

    def walk(self) -> list[dict]:
        history = [self.worlds[0].program]
        steps = []
        for index in range(1, len(self.worlds)):
            before, after = self.worlds[index - 1], self.worlds[index]
            classification = classify(history[-1], after.program, history, retention=3)
            statements = migrate(self.store.conn, before, after, classification, generation=index + 1)
            opened = open_store(self.store.conn, after, after.program.deployments[0])
            steps.append({
                "generation": index + 1,
                "compat": classification.compat,
                "kinds": sorted({event.kind for event in classification.events}),
                "statements": statements,
                "opened": opened,
            })
            history.append(after.program)
        return steps

    def step(self, generation: int) -> dict:
        return next(s for s in self.steps if s["generation"] == generation)

    def test_the_store_reopens_at_each_migrated_generation(self) -> None:
        self.assertEqual([2, 3, 4, 5], [s["generation"] for s in self.steps])
        self.assertEqual([2, 3, 4, 5], [s["opened"]["generation"] for s in self.steps])

    def test_every_migration_emits_at_least_one_statement(self) -> None:
        for step in self.steps:
            with self.subTest(generation=step["generation"]):
                self.assertTrue(step["statements"])

    def test_an_added_use_is_additive_and_the_later_generations_are_breaking(self) -> None:
        self.assertEqual("additive", self.step(2)["compat"])
        for generation in (3, 4, 5):
            with self.subTest(generation=generation):
                self.assertEqual("breaking", self.step(generation)["compat"])

    def test_generation_three_carries_rename_and_relocation_continuity(self) -> None:
        kinds = self.step(3)["kinds"]
        self.assertIn("intent_renamed", kinds)
        self.assertIn("intent_relocated", kinds)

    def test_retirement_and_restore_are_real_events(self) -> None:
        self.assertIn("retire_intent", self.step(4)["kinds"])
        self.assertIn("restore_intent", self.step(5)["kinds"])

    def test_the_renamed_column_keeps_the_data_that_was_written_before_the_rename(self) -> None:
        final = self.worlds[-1]
        carrier = final.carrier("clients.Client")
        use = carrier.use_named("preferred_name")
        self.assertIsNotNone(use, "the final generation renames the intent")
        relation = final.storage.relation("clients.Client")
        column = final.column_of("clients.Client", use)
        row = self.store.conn.execute(
            f"SELECT {q(column)} FROM {q(relation.table)} WHERE {q(relation.identity)} = ?", (self.client,)
        ).fetchone()
        self.assertEqual((self.seeded_name,), row)

    def test_the_intent_that_was_retired_and_restored_is_readable_again(self) -> None:
        final = self.worlds[-1]
        use = final.carrier("clients.Client").use_named("nickname")
        self.assertIsNotNone(use, "g5 restores the retired intent")
        relation = final.storage.relation("clients.Client")
        column = final.column_of("clients.Client", use)
        columns = {row[1] for row in self.store.conn.execute(f"PRAGMA table_info({q(relation.table)})").fetchall()}
        self.assertIn(column, columns)


class TestShipStageRefusals(GarnsTestCase):
    def test_each_evolution_scenario_refuses_at_ship_with_its_own_code(self) -> None:
        for name in SHIP_REFUSALS:
            with self.subTest(scenario=name):
                observation = observe_scenario(SCENARIOS / name)
                self.assertEqual((name, "ship"), (observation.code, observation.stage))

    def test_move_home_is_a_real_evolution_statement_not_a_refusal_shape(self) -> None:
        text = (SCENARIOS / "MOVE_HOME_INCONSISTENT" / "g2" / "world.garns").read_text(encoding="utf-8")
        program = resolve_files([parse_text(text, "move_home.garns")])
        self.assertEqual(1, len(program.move_homes))
        self.assertEqual("drop", program.move_homes[0].disposition)


class TestGenerationSourcesResolve(GarnsTestCase):
    def test_all_five_generations_resolve_and_bind_independently(self) -> None:
        for name, rel in GENERATIONS:
            with self.subTest(source=rel):
                world = world_ir(name, rel)
                self.assertEqual(name, world.world.name)
                self.assertIs(world.program, program_of(rel))


if __name__ == "__main__":
    unittest.main()
