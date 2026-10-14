"""Live questions: routing, scope partitioning, deltas and fold equivalence.

PRACTICE covers recursive composition, scope isolation, neutral writes and
rollback; LEDGERHOUSE (an ``external_captured`` world) covers grouped keys
moving between groups when an outside writer changes a row.
"""

from __future__ import annotations

import unittest

from tests.support import GarnsTestCase, seed_ledgerhouse, seed_practice, world_ir

from garns.capture import CaptureAdapter
from garns.live import canonical_rows, fold

PRACTICE = ("PRACTICE", "corpus/worlds/practice")
LEDGERHOUSE = ("LEDGERHOUSE", "corpus/conformance/worlds/ledgerhouse")
INNER = "labels.vip_clients"
OUTER = "labels.vip_contacts"
DORMANT = "notes.dormant_clients"


class PracticeLiveTestCase(GarnsTestCase):
    def setUp(self) -> None:
        self.world = world_ir(*PRACTICE)
        self.store, self.engine, self.live = self.shipped(self.world, clock=10)
        self.ids = seed_practice(self.engine)
        self.inner = self.live.subscribe(INNER, scope=self.ids["u1"])
        self.outer = self.live.subscribe(OUTER, scope=self.ids["u1"])
        self.other_scope = self.live.subscribe(INNER, scope=self.ids["u2"])
        self.dormant = self.live.subscribe(DORMANT, {"after": 10}, scope=self.ids["u1"])
        self.live.stats.listener_scans = 0

    def label(self, client_key: str, transaction: str) -> None:
        with self.engine.transaction("governed", transaction) as tx:
            tx.mint("labels.ClientLabel", {"labels.ClientLabel.client": self.ids[client_key],
                                           "labels.ClientLabel.label": self.ids["l1"]})


class TestInstrumentationIsReal(PracticeLiveTestCase):
    def test_the_listener_scan_counter_measures_real_registry_iteration(self) -> None:
        before = self.live.stats.listener_scans
        visited = list(self.live.registry)
        self.assertEqual(len(self.live.registry), len(visited))
        self.assertEqual(before + len(visited), self.live.stats.listener_scans)


class TestRouting(PracticeLiveTestCase):
    def test_a_write_inside_the_inner_question_routes_inner_and_outer(self) -> None:
        self.label("c2", "t2")
        self.assertTrue(self.live.last_routing.get(self.inner.id))
        self.assertTrue(self.live.last_routing.get(self.outer.id),
                        "recursive composition must route the composing question too")

    def test_a_result_neutral_routed_write_emits_no_batch(self) -> None:
        self.label("c2", "t2")
        self.assertIsNotNone(self.live.last_batches[self.inner.id])
        self.assertIsNone(self.live.last_batches[self.outer.id],
                          "the outer result did not change, so there is nothing to send")

    def test_a_write_outside_every_footprint_routes_nothing(self) -> None:
        with self.engine.transaction("governed", "t3") as tx:
            tx.change("people.User", self.ids["u1"], {"people.User.email": "one@y"})
        self.assertEqual({}, self.live.last_routing)
        self.assertEqual({}, self.live.last_batches)

    def test_a_write_in_another_scope_routes_only_that_partition(self) -> None:
        with self.engine.transaction("governed", "t4") as tx:
            tx.change("clients.Client", self.ids["c3"], {"clients.Client.preferred_name": "Cyrus"})
        self.assertEqual({self.other_scope.id}, set(self.live.last_routing))
        self.assertNotIn(self.inner.id, self.live.last_routing)
        self.assertNotIn(self.outer.id, self.live.last_routing)

    def test_routing_never_iterates_the_listener_registry(self) -> None:
        self.label("c2", "t2")
        with self.engine.transaction("governed", "t3") as tx:
            tx.change("people.User", self.ids["u1"], {"people.User.email": "one@y"})
        with self.engine.transaction("governed", "t4") as tx:
            tx.change("clients.Client", self.ids["c3"], {"clients.Client.preferred_name": "Cyrus"})
        stats = self.live.stats.as_dict()
        self.assertEqual(0, stats["listener_scans"], stats)
        self.assertGreater(stats["probes"], 0, "routing is done by probing the index")


class TestRollback(PracticeLiveTestCase):
    def test_a_rolled_back_transaction_leaves_no_revision_ledger_row_or_batch(self) -> None:
        revision_before = self.engine.revision
        rows_before = len(self.engine.ledger_rows())
        self.live.last_routing, self.live.last_batches = {}, {}

        class Abort(RuntimeError):
            pass

        with self.assertRaises(Abort):
            with self.engine.transaction("governed", "t5") as tx:
                tx.mint("labels.ClientLabel", {"labels.ClientLabel.client": self.ids["c1"],
                                               "labels.ClientLabel.label": self.ids["l1"]})
                raise Abort()
        self.assertTrue(tx.rolled_back)
        self.assertEqual(revision_before, self.engine.revision)
        self.assertEqual(rows_before, len(self.engine.ledger_rows()))
        self.assertEqual({}, self.live.last_routing)
        self.assertEqual({}, self.live.last_batches)

    def test_a_rolled_back_mint_leaves_no_row_behind(self) -> None:
        before = self.engine.execute(INNER, scope=self.ids["u1"]).rows
        try:
            with self.engine.transaction("governed", "t5") as tx:
                tx.mint("labels.ClientLabel", {"labels.ClientLabel.client": self.ids["c2"],
                                               "labels.ClientLabel.label": self.ids["l1"]})
                raise RuntimeError("abort")
        except RuntimeError:
            pass
        self.assertEqual(before, self.engine.execute(INNER, scope=self.ids["u1"]).rows)


class TestFoldEquivalence(PracticeLiveTestCase):
    def test_folded_deltas_equal_one_shot_recomputation_after_every_commit(self) -> None:
        initial, keys = self.inner.rows(), list(self.inner.order)
        log = []
        steps = [
            lambda: self.label("c2", "t2"),
            lambda: self.change_name("c1", "Annabel", "t3"),
            lambda: self.change_name("c2", "Bobby", "t4"),
            lambda: self.label("c1", "t5"),
        ]
        for n, step in enumerate(steps, start=1):
            with self.subTest(commit=n):
                step()
                batch = self.live.last_batches.get(self.inner.id)
                if batch is not None:
                    log.append(batch)
                folded = fold(initial, keys, log)
                one_shot = self.engine.execute(INNER, scope=self.ids["u1"]).rows
                self.assertEqual(canonical_rows(sorted(folded, key=canonical_key)),
                                 canonical_rows(sorted(one_shot, key=canonical_key)))
        self.assertTrue(log, "at least one commit must have produced a batch")

    def change_name(self, client_key: str, name: str, transaction: str) -> None:
        with self.engine.transaction("governed", transaction) as tx:
            tx.change("clients.Client", self.ids[client_key], {"clients.Client.preferred_name": name})


def canonical_key(row: dict) -> str:
    return canonical_rows([row])


class TestCapturedGroupedQuestion(GarnsTestCase):
    """LEDGERHOUSE: an external writer moves a row between group keys."""

    GROUPED = "pantry.jars_by_state"

    def setUp(self) -> None:
        self.world = world_ir(*LEDGERHOUSE)
        self.store, self.engine, self.live = self.shipped(self.world, clock=1)
        self.capture = CaptureAdapter(self.engine)
        seed_ledgerhouse(self.store)
        self.capture.acquire("e1")
        self.instance = self.live.subscribe(self.GROUPED, scope=1)

    def test_moving_a_row_between_groups_refreshes_the_old_and_the_new_key(self) -> None:
        before = {tuple(key) for key in self.instance.order}
        self.store.conn.execute("UPDATE jar SET cond='sealed' WHERE lbl='rice'")
        self.capture.acquire("e2")
        batch = self.live.last_batches[self.instance.id]
        self.assertIsNotNone(batch, "a group key move must produce a batch")
        changes = {(change.op, change.key) for change in batch.changes}
        self.assertIn(("delete", ("open",)), changes)
        self.assertIn(("upsert", ("sealed",)), changes)
        self.assertIn(("open",), before)

    def test_folded_deltas_equal_one_shot_recomputation_after_every_captured_revision(self) -> None:
        initial, keys = self.instance.rows(), list(self.instance.order)
        log = []
        emitted = []
        steps = (
            "UPDATE jar SET cond='sealed' WHERE lbl='rice'",
            "UPDATE jar SET mass_g=50 WHERE lbl='salt'",
            "INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('tea', 20, 'open', 1)",
            "DELETE FROM jar WHERE lbl='rice'",
        )
        for n, statement in enumerate(steps, start=1):
            with self.subTest(revision=n):
                self.store.conn.execute(statement)
                self.capture.acquire(f"e{n}")
                batch = self.live.last_batches.get(self.instance.id)
                emitted.append(batch is not None)
                if batch is not None:
                    log.append(batch)
                folded = fold(initial, keys, log)
                one_shot = self.engine.execute(self.GROUPED, scope=1).rows
                self.assertEqual(canonical_rows(sorted(folded, key=canonical_key)),
                                 canonical_rows(sorted(one_shot, key=canonical_key)))
        self.assertEqual([True, False, True, True], emitted,
                         "only writes that change the grouped result may emit a batch")

    def test_an_external_write_outside_the_grouped_footprint_routes_nothing(self) -> None:
        atoms = {(a.carrier, a.field) for a in self.instance.footprint.atoms}
        self.assertNotIn(("pantry.Jar", "pantry.Jar.grams"), atoms)
        self.store.conn.execute("UPDATE jar SET mass_g=50 WHERE lbl='salt'")
        self.capture.acquire("e-neutral")
        self.assertNotIn(self.instance.id, self.live.last_routing)
        self.assertIsNone(self.live.last_batches.get(self.instance.id))


if __name__ == "__main__":
    unittest.main()
