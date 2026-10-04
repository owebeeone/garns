"""Wave-3 repair regression (R1 P2.4): a recognised engine without a lowering refuses pre-effect."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD / "src"))

from garns.engine import Engine, Store  # noqa: E402
from garns.metamorphic import physical_scheme  # noqa: E402
from garns.parse import parse_text  # noqa: E402
from garns.refuse import Refusal  # noqa: E402
from garns.resolve import ENGINES, LOWERED_ENGINES, resolve_files  # noqa: E402
from garns.storage import bind_world, binding_document  # noqa: E402

SOURCE = (BUILD / "corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns").read_text(encoding="utf-8")


class EngineLoweringAbsentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="garns-engine-"))
        self.addCleanup(lambda: __import__("shutil").rmtree(self.tmp, ignore_errors=True))

    def attempt(self, text: str, name: str):
        db = self.tmp / f"{name}.sqlite"
        try:
            program = resolve_files([parse_text(text, f"{name}.garns")])
            binding = self.tmp / f"{name}.json"
            binding.write_text(json.dumps(binding_document(program, "ARCHIVE", physical_scheme(name))))
            world = bind_world(program, "ARCHIVE", binding)
            store = Store(world, str(db)); store.ship(); engine = Engine(store, clock=lambda: 1)
            with engine.transaction("governed", "t1") as tx:
                tx.mint("archive.Entry", {"archive.Entry.key": "k1", "archive.Entry.amount": 5})
            store.close()
            return "shipped", db
        except Refusal as r:
            return (r.stage, r.code, r.line, r.column), db

    def test_postgres_is_recognised_but_not_lowered(self) -> None:
        self.assertIn("postgres", ENGINES)
        self.assertNotIn("postgres", LOWERED_ENGINES)
        self.assertEqual(LOWERED_ENGINES, frozenset({"sqlite"}))

    def test_postgres_deployment_refuses_at_validate_before_any_effect(self) -> None:
        outcome, db = self.attempt(SOURCE, "postgres")
        self.assertEqual(outcome, ("validate", "ENGINE_LOWERING_ABSENT", 24, 10))
        self.assertFalse(db.exists(), "no store file may exist after a pre-effect refusal")

    def test_sqlite_twin_ships_and_writes(self) -> None:
        outcome, db = self.attempt(SOURCE.replace("engine postgres", "engine sqlite"), "sqlite")
        self.assertEqual(outcome, "shipped")
        self.assertTrue(db.exists())

    def test_unknown_engine_is_a_different_refusal(self) -> None:
        outcome, db = self.attempt(SOURCE.replace("engine postgres", "engine oracle"), "oracle")
        self.assertEqual(outcome[:2], ("validate", "ENGINE_UNKNOWN"))
        self.assertFalse(db.exists())

    def test_engine_inherited_through_extends_refuses(self) -> None:
        text = SOURCE.replace("  engine postgres\n", "  engine sqlite\n") + '\ndeployment ARCHIVE_MIRROR "inherits" extends ARCHIVE_STORE {\n  engine postgres\n}\n'
        outcome, db = self.attempt(text, "extends")
        self.assertEqual(outcome[:2], ("validate", "ENGINE_LOWERING_ABSENT"))
        self.assertFalse(db.exists())


if __name__ == "__main__":
    unittest.main()
