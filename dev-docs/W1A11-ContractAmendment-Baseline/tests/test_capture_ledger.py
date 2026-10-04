"""Ledger typing and external capture.

The typed identities of a write are validated before any effect: the store's
revision and ledger must be unchanged after a refusal. The captured world's
changelog coverage is measured against the real store, so removing a declared
changelog column refuses at load.
"""

from __future__ import annotations

import unittest

from tests.support import CORPUS, GarnsTestCase, seed_ledgerhouse, seed_practice, world_ir

from garns.capture import CaptureAdapter
from garns.mutants import observe_scenario
from garns.refuse import Refusal
from garns.storage import expected_relation_keys

PRACTICE = ("PRACTICE", "corpus/worlds/practice")
LEDGERHOUSE = ("LEDGERHOUSE", "corpus/conformance/worlds/ledgerhouse")
SCENARIOS = CORPUS / "mutants" / "scenarios"


class TestTypedPreEffectRefusals(GarnsTestCase):
    """Every identity a ledger record names is checked before the store changes."""

    def setUp(self) -> None:
        self.world = world_ir(*PRACTICE)
        self.store, self.engine, _live = self.shipped(self.world, clock=10)
        self.ids = seed_practice(self.engine)
        self.revision = self.engine.revision
        self.rows = len(self.engine.ledger_rows())

    def assertNoEffect(self) -> None:
        self.assertEqual(self.revision, self.engine.revision, "a refused write must not advance the revision")
        self.assertEqual(self.rows, len(self.engine.ledger_rows()), "a refused write must not append to the ledger")

    def refused(self, action) -> Refusal:
        with self.assertRaises(Refusal) as caught:
            action()
        self.assertNoEffect()
        return caught.exception

    def test_an_undeclared_writer_refuses(self) -> None:
        def act():
            with self.engine.transaction("stranger", "tx1"):
                pass

        self.assertEqual("LEDGER_WRITER_UNKNOWN", self.refused(act).code)

    def test_a_transaction_identity_that_is_not_typed_refuses(self) -> None:
        def act():
            with self.engine.transaction("governed", "not a typed id!"):
                pass

        self.assertEqual("LEDGER_TRANSACTION_INVALID", self.refused(act).code)

    def test_a_carrier_outside_the_world_refuses(self) -> None:
        def act():
            with self.engine.transaction("governed", "tx1") as tx:
                tx.mint("people.NotACarrier", {})

        self.assertEqual("LEDGER_CARRIER_UNKNOWN", self.refused(act).code)

    def test_a_field_that_is_not_a_use_or_link_refuses(self) -> None:
        def act():
            with self.engine.transaction("governed", "tx1") as tx:
                tx.mint("people.User", {"people.User.nickname": "nope"})

        self.assertEqual("LEDGER_FIELD_UNKNOWN", self.refused(act).code)

    def test_a_value_of_the_wrong_type_refuses(self) -> None:
        def act():
            with self.engine.transaction("governed", "tx1") as tx:
                tx.mint("people.User", {"people.User.email": 42})

        self.assertEqual("LEDGER_VALUE_TYPE", self.refused(act).code)

    def test_a_scope_identity_that_is_not_in_the_store_refuses(self) -> None:
        def act():
            with self.engine.transaction("governed", "tx1") as tx:
                tx.mint("clients.Client", {"clients.Client.preferred_name": "Zed", "clients.Client.owner": 9999})

        self.assertEqual("LEDGER_SCOPE_UNKNOWN", self.refused(act).code)

    def test_the_same_writes_are_admitted_once_their_identities_are_typed(self) -> None:
        with self.engine.transaction("governed", "tx1") as tx:
            identity = tx.mint("clients.Client", {"clients.Client.preferred_name": "Zed",
                                                  "clients.Client.owner": self.ids["u1"]})
        self.assertEqual(self.revision + 1, self.engine.revision)
        self.assertEqual(self.rows + 1, len(self.engine.ledger_rows()))
        self.assertIsInstance(identity, int)


class TestScenarioRefusals(GarnsTestCase):
    """The same refusals, executed against real store states by the scenario runner."""

    NAMES = ("LEDGER_WRITER_UNKNOWN", "LEDGER_FIELD_UNKNOWN", "LEDGER_SCOPE_UNKNOWN", "LEDGER_VALUE_TYPE",
             "LEDGER_TRANSACTION_INVALID", "LEDGER_CARRIER_UNKNOWN")

    def test_each_scenario_refuses_with_its_own_code_at_runtime(self) -> None:
        for name in self.NAMES:
            with self.subTest(scenario=name):
                observation = observe_scenario(SCENARIOS / name)
                self.assertEqual((name, "runtime"), (observation.code, observation.stage))

    def test_the_control_scenario_is_accepted(self) -> None:
        observation = observe_scenario(SCENARIOS / "ACCEPTED_CONTROL")
        self.assertEqual(("ACCEPTED", "accepted"), (observation.code, observation.stage))


class TestExternalCapture(GarnsTestCase):
    def setUp(self) -> None:
        self.world = world_ir(*LEDGERHOUSE)
        self.store, self.engine, self.live = self.shipped(self.world, clock=1)
        self.capture = CaptureAdapter(self.engine)
        seed_ledgerhouse(self.store)

    def test_external_writes_become_typed_deltas_carrying_scope_keys(self) -> None:
        revision, deltas = self.capture.acquire("ext-1")
        self.assertEqual(1, revision)
        by_carrier = {}
        for delta in deltas:
            by_carrier.setdefault(delta.carrier, []).append(delta)
        self.assertIn("pantry.Jar", by_carrier)
        for delta in by_carrier["pantry.Jar"]:
            self.assertEqual("insert", delta.operation)
            self.assertEqual(1, delta.scope_after, "a jar is scoped through its shelf to the household")
        self.assertEqual({"pantry_daemon"}, {d.writer for d in deltas})
        self.assertEqual({"ext-1"}, {d.transaction for d in deltas})

    def test_coverage_denominators_are_measured_against_the_declared_fields(self) -> None:
        observed = self.capture.check_coverage()
        expected = {}
        for carrier in self.world.relations:
            uses, links = expected_relation_keys(self.world.program, carrier)
            expected[carrier.qid] = 4 + len(uses) + len(links)  # seq, op, revision, identity + mapped fields
        self.assertEqual(expected, observed)

    def test_ledger_records_carry_typed_carrier_identity_writer_and_transaction(self) -> None:
        self.capture.acquire("ext-1")
        rows = self.engine.ledger_rows()
        self.assertTrue(rows)
        qids = {c.qid for c in self.world.relations}
        for row in rows:
            self.assertIn(row["carrier"], qids)
            self.assertIsInstance(row["identity"], int)
            self.assertEqual("pantry_daemon", row["writer"])
            self.assertEqual("ext-1", row["transaction_id"])

    def test_dropping_a_declared_changelog_column_refuses_at_load_before_any_effect(self) -> None:
        self.capture.acquire("ext-1")
        revision = self.engine.revision
        self.store.conn.execute("INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('tea', 20, 'open', 1)")
        self.store.conn.execute("ALTER TABLE jar_trail DROP COLUMN cond_v")
        with self.assertRaises(Refusal) as caught:
            self.capture.acquire("ext-2")
        self.assertEqual(("WRITER_CAPTURE_INCOMPLETE", "load"), (caught.exception.code, caught.exception.stage))
        self.assertEqual(revision, self.engine.revision, "the refusal precedes any recorded revision")

    def test_a_missing_changelog_table_refuses_at_load(self) -> None:
        self.store.conn.execute("DROP TABLE jar_trail")
        with self.assertRaises(Refusal) as caught:
            self.capture.check_coverage()
        self.assertEqual(("WRITER_CAPTURE_INCOMPLETE", "load"), (caught.exception.code, caught.exception.stage))


class TestCaptureRequiresDeclaration(GarnsTestCase):
    def test_a_governed_world_admits_no_capture_adapter(self) -> None:
        _store, engine, _live = self.shipped(world_ir(*PRACTICE))
        with self.assertRaises(Refusal) as caught:
            CaptureAdapter(engine)
        self.assertEqual("CAPTURE_NOT_DECLARED", caught.exception.code)


if __name__ == "__main__":
    unittest.main()
