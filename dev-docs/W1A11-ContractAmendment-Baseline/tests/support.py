"""Shared fixtures and helpers for the Garns baseline test suite.

Nothing here decides an outcome: worlds and reads are selected by their
qualified names (the only selection the public boundaries admit), stores are
built in temporary files or memory, and every expectation is computed by the
test from data it seeded itself.
"""

from __future__ import annotations

import functools
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

BUILD = Path(__file__).resolve().parents[1]

for _entry in (str(BUILD / "src"), str(BUILD)):
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

from garns.engine import Engine, Store  # noqa: E402
from garns.ir import Program  # noqa: E402
from garns.live import LiveEngine  # noqa: E402
from garns.parse import garns_files, parse_paths  # noqa: E402
from garns.resolve import resolve_files  # noqa: E402
from garns.storage import WorldIR, bind_world  # noqa: E402

CORPUS = BUILD / "corpus"
GENERATED = BUILD / "generated"

# Corpus trees whose sources are meant to be admitted by the frozen grammar.
# The refusal and single-file mutant fixtures are deliberately excluded: they
# exist to be refused, and test_parse/test_mutants observe them separately.
PARSEABLE_ROOTS = (
    CORPUS / "worlds",
    CORPUS / "conformance" / "worlds",
    CORPUS / "conformance" / "static",
    CORPUS / "conformance" / "dynamic",
    CORPUS / "metamorphic",
    CORPUS / "mutants" / "scenarios",
)


def discovered_worlds() -> list[tuple[str, str]]:
    """Every ``(world name, build-relative source directory)`` in the corpus.

    Discovered from the storage bindings on disk, so a world added to the
    corpus is covered without editing the suite.
    """
    out: list[tuple[str, str]] = []
    for root in (CORPUS / "worlds", CORPUS / "conformance" / "worlds"):
        for binding in root.rglob("storage-*.json"):
            name = binding.name[len("storage-") : -len(".json")]
            out.append((name, binding.parent.relative_to(BUILD).as_posix()))
    return sorted(out, key=lambda pair: (pair[1], pair[0]))


@functools.lru_cache(maxsize=None)
def program_of(rel: str) -> Program:
    """Parse and resolve every ``*.garns`` of one build-relative directory."""
    return resolve_files(parse_paths(garns_files(BUILD / rel)))


@functools.lru_cache(maxsize=None)
def world_ir(world: str, rel: str) -> WorldIR:
    """Bind ``world`` (by qualified world name) to its explicit storage document."""
    program = program_of(rel)
    return bind_world(program, world, BUILD / rel / f"storage-{world}.json")


class GarnsTestCase(unittest.TestCase):
    """Adds temporary directories and shipped stores that clean themselves up."""

    def tempdir(self) -> Path:
        path = Path(tempfile.mkdtemp(prefix="garns-tests-"))
        self.addCleanup(shutil.rmtree, path, ignore_errors=True)
        return path

    def shipped(self, world: WorldIR, clock: int = 10, path: str = ":memory:") -> tuple[Store, Engine, LiveEngine]:
        store = Store(world, path)
        self.addCleanup(store.close)
        store.ship()
        engine = Engine(store, clock=lambda: clock)
        return store, engine, LiveEngine(engine)


# --------------------------------------------------------------------- seeds
# The seeds below are the tests' own data. Every expectation in the suite is
# derived from these rows, never from a file that records an answer.

PRACTICE_CLIENTS = (("c1", "Ann", "u1"), ("c2", "Bob", "u1"), ("c3", "Cy", "u2"))
SALES_ORDERS = (("cA", "open", 120, 5), ("cA", "open", 30, 7), ("cB", "open", 200, 6),
                ("cB", "closed", 999, 8), ("cA", "closed", 1, 9))


def seed_practice(engine: Engine) -> dict[str, int]:
    ids: dict[str, int] = {}
    with engine.transaction("governed", "seed") as tx:
        ids["u1"] = tx.mint("people.User", {"people.User.email": "one@x"})
        ids["u2"] = tx.mint("people.User", {"people.User.email": "two@x"})
        for key, name, owner in PRACTICE_CLIENTS:
            ids[key] = tx.mint("clients.Client", {"clients.Client.preferred_name": name, "clients.Client.owner": ids[owner]})
        ids["k1"] = tx.mint("clients.Contact", {"clients.Contact.preferred_name": "Kim", "clients.Contact.email": "k@x",
                                                "clients.Contact.relationship": "sister", "clients.Contact.client": ids["c1"]})
        ids["l1"] = tx.mint("labels.Label", {"labels.Label.label_name": "vip"})
        ids["cl1"] = tx.mint("labels.ClientLabel", {"labels.ClientLabel.client": ids["c1"], "labels.ClientLabel.label": ids["l1"]})
        ids["n1"] = tx.mint("notes.Note", {"notes.Note.note_body": "hello", "notes.Note.recorded_at": 5, "notes.Note.client": ids["c1"]})
        ids["f1"] = tx.mint("documents.Form", {"documents.Form.title": "intake", "documents.Form.template_ref": "T1",
                                               "documents.Form.client": ids["c1"], "documents.Form.owner": ids["u1"]})
    return ids


def seed_sales(engine: Engine) -> dict[str, int]:
    ids: dict[str, int] = {}
    with engine.transaction("governed", "seed") as tx:
        ids["cA"] = tx.mint("sales.Customer", {"sales.Customer.customer_id": "A", "sales.Customer.name": "Acme"})
        ids["cB"] = tx.mint("sales.Customer", {"sales.Customer.customer_id": "B", "sales.Customer.name": "Bolt"})
        for n, (customer, status, total, created) in enumerate(SALES_ORDERS):
            ids[f"o{n}"] = tx.mint("sales.Order", {"sales.Order.order_id": f"O{n}", "sales.Order.status": status,
                                                   "sales.Order.total": total, "sales.Order.created_at": created,
                                                   "sales.Order.customer": ids[customer]})
    return ids


SALES_CUSTOMER_NAMES = {"cA": "Acme", "cB": "Bolt"}


def seed_ledgerhouse(store: Store) -> None:
    """Write the captured world's tables the way its external writer would."""
    conn = store.conn
    conn.execute("INSERT INTO house (code_txt) VALUES ('H1')")
    conn.execute("INSERT INTO shelf (label_txt, kept_by) VALUES ('top', 1)")
    conn.execute("INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('rice', 900, 'open', 1)")
    conn.execute("INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('salt', 100, 'sealed', 1)")
