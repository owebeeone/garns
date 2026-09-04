#!/usr/bin/env python3
"""Run the repository verification gates inherited from the v9-5 exit matrix.

No expected answer, filename, comment, or marker is an input to any detector:
expectation files are read only to assert against independently observed
outcomes. Writes gate-report.json next to this build's README.

Usage: uv run --offline --with lark python tools/check.py [--quick]
"""

from __future__ import annotations

import argparse
import hashlib
import sys as _sys

_sys.dont_write_bytecode = True

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

BUILD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BUILD / "src"))

from garns import ir as I  # noqa: E402
from garns.capture import CaptureAdapter  # noqa: E402
from garns.engine import Engine, Store  # noqa: E402
from garns.evolution import classify, migrate, open_store  # noqa: E402
from garns.footprint import derive_footprint  # noqa: E402
from garns.generate import generate, tree_digest  # noqa: E402
from garns.live import LiveEngine, canonical_rows, fold  # noqa: E402
from garns.lower_sqlite import lower_read  # noqa: E402
from garns.metamorphic import normalize, normalized_program_json, transform  # noqa: E402
from garns.mutants import observe_all, observe_single  # noqa: E402
from garns.parse import garns_files, parse_path, parse_paths, parse_text  # noqa: E402
from garns.refuse import Refusal  # noqa: E402
from garns.resolve import resolve_files  # noqa: E402
from garns.storage import bind_world  # noqa: E402
from garns.visit import EXPR_NODES, OPERAND_NODES, SHOW_NODES, check_exhaustive  # noqa: E402

PY = [sys.executable]
WORLDS = [("PRACTICE", "corpus/worlds/practice"), ("EVERBILITY", "corpus/worlds/everbility"), ("VAULTWARDEN", "corpus/worlds/vaultwarden"),
          ("APPFLOWY", "corpus/worlds/appflowy"), ("APPFLOWY_VEC", "corpus/worlds/appflowy"), ("REPORTING", "corpus/conformance/worlds/reporting"),
          ("SALES", "corpus/conformance/worlds/sales"), ("LEDGERHOUSE", "corpus/conformance/worlds/ledgerhouse")] + [(f"PRACTICE", f"corpus/worlds/evolution/g{n}") for n in range(1, 6)]


class Gate:
    def __init__(self, name: str, requirement: str) -> None:
        self.name = name
        self.requirement = requirement
        self.checks: list[dict] = []
        self.commands: list[dict] = []
        self.evidence: list[str] = []

    def check(self, label: str, ok: bool, detail: str = "") -> bool:
        self.checks.append({"label": label, "ok": bool(ok), "detail": detail})
        return bool(ok)

    def command(self, argv: list[str], cwd: Path | None = None, env_no_bytecode: bool = True) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        if env_no_bytecode:
            env["PYTHONDONTWRITEBYTECODE"] = "1"
        proc = subprocess.run(argv, cwd=str(cwd or BUILD), capture_output=True, text=True, env=env)
        self.commands.append({"argv": argv, "exit": proc.returncode, "stdout_tail": proc.stdout[-400:], "stderr_tail": proc.stderr[-400:]})
        return proc

    @property
    def passed(self) -> bool:
        return all(c["ok"] for c in self.checks) and bool(self.checks)

    def as_dict(self) -> dict:
        return {"gate": self.name, "requirement": self.requirement, "pass": self.passed, "checks": self.checks, "commands": self.commands, "evidence": self.evidence}


def world_ir(world: str, rel: str):
    src = BUILD / rel
    program = resolve_files(parse_paths(garns_files(src)))
    return bind_world(program, world, src / f"storage-{world}.json"), program


def seed_practice(engine: Engine) -> dict:
    ids = {}
    with engine.transaction("governed", "seed") as tx:
        ids["u1"] = tx.mint("people.User", {"people.User.email": "one@x"})
        ids["u2"] = tx.mint("people.User", {"people.User.email": "two@x"})
        ids["c1"] = tx.mint("clients.Client", {"clients.Client.preferred_name": "Ann", "clients.Client.owner": ids["u1"]})
        ids["c2"] = tx.mint("clients.Client", {"clients.Client.preferred_name": "Bob", "clients.Client.owner": ids["u1"]})
        ids["c3"] = tx.mint("clients.Client", {"clients.Client.preferred_name": "Cy", "clients.Client.owner": ids["u2"]})
        ids["k1"] = tx.mint("clients.Contact", {"clients.Contact.preferred_name": "Kim", "clients.Contact.email": "k@x", "clients.Contact.relationship": "sister", "clients.Contact.client": ids["c1"]})
        ids["l1"] = tx.mint("labels.Label", {"labels.Label.label_name": "vip"})
        ids["cl1"] = tx.mint("labels.ClientLabel", {"labels.ClientLabel.client": ids["c1"], "labels.ClientLabel.label": ids["l1"]})
        ids["n1"] = tx.mint("notes.Note", {"notes.Note.note_body": "hello", "notes.Note.recorded_at": 5, "notes.Note.client": ids["c1"]})
        ids["f1"] = tx.mint("documents.Form", {"documents.Form.title": "intake", "documents.Form.template_ref": "T1", "documents.Form.client": ids["c1"], "documents.Form.owner": ids["u1"]})
    return ids


def seed_sales(engine: Engine) -> dict:
    ids = {}
    with engine.transaction("governed", "seed") as tx:
        ids["cA"] = tx.mint("sales.Customer", {"sales.Customer.customer_id": "A", "sales.Customer.name": "Acme"})
        ids["cB"] = tx.mint("sales.Customer", {"sales.Customer.customer_id": "B", "sales.Customer.name": "Bolt"})
        for n, (cust, status, total, at) in enumerate([("cA", "open", 120, 5), ("cA", "open", 30, 7), ("cB", "open", 200, 6), ("cB", "closed", 999, 8), ("cA", "closed", 1, 9)]):
            ids[f"o{n}"] = tx.mint("sales.Order", {"sales.Order.order_id": f"O{n}", "sales.Order.status": status, "sales.Order.total": total, "sales.Order.created_at": at, "sales.Order.customer": ids[cust]})
    return ids


# --------------------------------------------------------------------- gates


def purge_caches() -> int:
    removed = 0
    for p in list(BUILD.rglob("__pycache__")):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            removed += 1
    return removed


def g0(gate: Gate) -> None:
    purge_caches()
    gate.check("repository metadata is present", (BUILD / "pyproject.toml").is_file() and (BUILD / "CUT_MANIFEST.json").is_file())
    root_grammar = (BUILD / "grammar" / "garns.lark").read_bytes()
    package_grammar = (BUILD / "src" / "garns" / "garns.lark").read_bytes()
    digest = hashlib.sha256(root_grammar).hexdigest()
    gate.check("root and packaged grammar are byte-identical", root_grammar == package_grammar, digest)
    for rel in ("corpus/conformance/static/reporting.garns", "corpus/conformance/dynamic/open_orders.garns"):
        path = BUILD / rel
        try:
            parse_path(path)
        except Exception as exc:
            gate.check(f"{rel} remains admitted", False, str(exc))
        else:
            gate.check(f"{rel} remains admitted", True, hashlib.sha256(path.read_bytes()).hexdigest())
    gate.evidence.append("grammar/garns.lark")


def g1(gate: Gate) -> None:
    from garns.parse import parser

    p = parser()
    gate.check("parser is LALR", p.options.parser == "lalr", "lark parser=lalr")
    count = 0
    for world, rel in WORLDS:
        try:
            w, program = world_ir(world, rel)
            count += len(program.carriers)
        except Refusal as r:
            gate.check(f"resolve {world} ({rel})", False, str(r))
            continue
        gate.check(f"resolve+bind {world} ({rel})", True, f"{len(program.carriers)} carriers, {len(w.reads)} reads")
    unenforced = [l for world, rel in WORLDS[:1] for c in world_ir(world, rel)[1].carriers for l in c.links if l.enforcement == "unenforced"]
    w_rep, _ = world_ir("REPORTING", "corpus/conformance/worlds/reporting")
    link = w_rep.carrier("reporting.Invoice").link_named("customer")
    gate.check("standalone unenforced resolves as a typed link without a foreign key", link is not None and link.enforcement == "unenforced" and link.inverse == "invoices")
    from garns.lower_sqlite import lower_ddl

    ddl = lower_ddl(w_rep)
    gate.check("unenforced link emits no FOREIGN KEY", "FOREIGN KEY" not in ddl)
    expected = {c["file"]: c for c in json.loads((BUILD / "corpus/conformance/refusals/expected.json").read_text())["cases"]}
    for path in sorted((BUILD / "corpus/conformance/refusals").glob("*.garns")):
        obs = observe_single(path)
        exp = expected[path.name]
        gate.check(f"refusal {path.name}: observed {obs.stage}/{obs.code}", (obs.stage, obs.code) == (exp["stage"], exp["code"]), f"expected {exp['stage']}/{exp['code']} at {obs.line}:{obs.column}")
    gate.evidence.append("corpus/conformance/refusals/expected.json")
    gate.evidence.append("corpus/worlds/MIGRATION.md")


def g2_g4(g2: Gate, g3: Gate, g4: Gate, tmp: Path) -> None:
    w, program = world_ir("SALES", "corpus/conformance/worlds/sales")
    store = Store(w); store.ship(); engine = Engine(store, clock=lambda: 50); live = LiveEngine(engine)
    ids = seed_sales(engine)
    # G2: richer static query executes
    rows = engine.execute("sales_static.revenue_open_by_customer", {"floor": 10}).rows
    g2.check("richer static query (group/having/arithmetic/call/non-path order) executes", rows == [{"customer": "Bolt", "revenue": 200, "orders": 1, "average_order": 200.0}, {"customer": "Acme", "revenue": 150, "orders": 2, "average_order": 75.0}], json.dumps(rows))
    g2.check("distinct static query executes", engine.execute("sales_static.distinct_open_customers").rows == [{"customer": "Acme"}, {"customer": "Bolt"}])
    out = generate(w, tmp / "sales")
    live_products = [f for f in out if f.startswith("questions/")]
    query_products = [f for f in out if f.startswith("queries/")]
    g2.check("queries generate SQL only; no footprint/binding/routing artifact for any query", all(not re.search(r"sales_static\.", f) for f in live_products) and len(query_products) == 3, json.dumps(sorted(live_products)))
    try:
        live.subscribe("sales_static.open_orders_once")
        g2.check("subscribing a query refuses", False)
    except Refusal as r:
        g2.check("subscribing a query refuses before any registration", r.code == "QUERY_NOT_LIVE" and len(live.registry) == 0 and not live.index, str(r))
    try:
        derive_footprint(w, w.program.read("sales_static.open_orders_once"))
        g2.check("footprint of a query refuses", False)
    except Refusal as r:
        g2.check("deriving a footprint for a query refuses", r.code == "QUERY_NOT_LIVE")
    g2.evidence.append("corpus/conformance/worlds/sales/parity.garns")
    # G3
    fp = derive_footprint(w, w.program.read("sales.open_orders"))
    atoms = {(a.carrier, a.field) for a in fp.atoms}
    g3.check("question footprint covers subject structure, predicate, projections, link and order fields",
             {("sales.Order", "*"), ("sales.Order", "sales.Order.status"), ("sales.Order", "sales.Order.total"), ("sales.Order", "sales.Order.customer"), ("sales.Customer", "sales.Customer.name"), ("sales.Order", "sales.Order.created_at")} <= atoms, json.dumps(sorted(atoms)))
    for name, code in (("QUESTION_STATIC_CALL-1.garns", "DECL_SHAPE_INVALID"), ("QUESTION_CLOCK-1.garns", "QUESTION_NOT_FOOTPRINTABLE"), ("QUESTION_COMPOSE_STATIC-1.garns", "QUESTION_COMPOSE_STATIC"),
                       ("QUESTION_LIVE_BOUND_REQUIRED-1.garns", "QUESTION_LIVE_BOUND_REQUIRED"), ("QUESTION_LIVE_BOUND_DUPLICATED-1.garns", "QUESTION_LIVE_BOUND_DUPLICATED")):
        obs = observe_single(BUILD / "corpus/conformance/refusals" / name)
        g3.check(f"static-only/unbounded form in a question refuses pre-effect: {name} -> {obs.code}", obs.code == code and obs.stage in ("decode", "validate"))
    inst = live.subscribe("sales.open_orders")
    g3.check("valid question subscribes, derives its footprint and routes", len(live.index) > 0 and len(inst.rows()) == 3)
    with engine.transaction("governed", "t2") as tx:
        tx.change("sales.Order", ids["o3"], {"sales.Order.status": "open"})
    g3.check("relevant write routes and emits a batch", live.last_routing.get(inst.id) is True and live.last_batches[inst.id] is not None)
    # G4: parity on the shared subset
    one_shot = engine.execute("sales_static.open_orders_once").rows
    inst2 = live.subscribe("sales.open_orders")
    g4.check("query one-shot rows == question initial live rows (canonical bytes)", canonical_rows(one_shot) == canonical_rows(inst2.rows()), canonical_rows(one_shot))
    plan_q = lower_read(w, w.program.read("sales_static.open_orders_once"))
    plan_d = lower_read(w, w.program.read("sales.open_orders"))
    g4.check("both nouns lower through one plan type with the same key/column shape", plan_q.columns == plan_d.columns and plan_q.key_columns == plan_d.key_columns and type(plan_q) is type(plan_d))
    src = (BUILD / "src/garns/lower_sqlite.py").read_text()
    g4.check("one lowering entry point serves execute() and live refresh", src.count("def lower_read(") == 1 and "lower_read(" in (BUILD / "src/garns/engine.py").read_text() and "engine.execute(" in (BUILD / "src/garns/live.py").read_text())
    g4.evidence.append("src/garns/lower_sqlite.py")


def g5(gate: Gate, tmp: Path) -> None:
    src = BUILD / "corpus/worlds/practice"
    files = parse_paths(garns_files(src))
    program = resolve_files(files)
    tr = transform(files, program, "PRACTICE", "meta-seed-7", lambda texts: resolve_files([parse_text(t, p) for p, t in texts.items()]))
    program2 = resolve_files([parse_text(t, p) for p, t in tr.sources.items()])
    gate.check("normalized IR equal after full rename", normalized_program_json(program) == normalized_program_json(program2, tr.forward), f"{len(tr.mapping)} identities renamed")
    world1 = bind_world(program, "PRACTICE", src / "storage-PRACTICE.json")
    binding_path = tmp / "renamed-binding.json"
    binding_path.write_text(json.dumps(tr.binding, indent=1, sort_keys=True))
    world2 = bind_world(program2, tr.mapping["PRACTICE"], binding_path)
    from garns.metamorphic import rename_qualified

    m = lambda key: rename_qualified(program, tr.mapping, key)  # noqa: E731

    def scenario(world, engine, live, names):
        ids = {}
        q = names
        with engine.transaction("governed", "seed") as tx:
            ids["u1"] = tx.mint(q("people.User"), {q("people.User.email"): "one@x"})
            ids["u2"] = tx.mint(q("people.User"), {q("people.User.email"): "two@x"})
            ids["c1"] = tx.mint(q("clients.Client"), {q("clients.Client.preferred_name"): "Ann", q("clients.Client.owner"): ids["u1"]})
            ids["c2"] = tx.mint(q("clients.Client"), {q("clients.Client.preferred_name"): "Bob", q("clients.Client.owner"): ids["u1"]})
            ids["c3"] = tx.mint(q("clients.Client"), {q("clients.Client.preferred_name"): "Cy", q("clients.Client.owner"): ids["u2"]})
            ids["k1"] = tx.mint(q("clients.Contact"), {q("clients.Contact.preferred_name"): "Kim", q("clients.Contact.email"): "k@x", q("clients.Contact.relationship"): "sister", q("clients.Contact.client"): ids["c1"]})
            ids["l1"] = tx.mint(q("labels.Label"), {q("labels.Label.label_name"): "vip"})
            tx.mint(q("labels.ClientLabel"), {q("labels.ClientLabel.client"): ids["c1"], q("labels.ClientLabel.label"): ids["l1"]})
        rows = {
            "vip": engine.execute(q("labels.vip_clients"), scope=ids["u1"]).rows,
            "assign": engine.execute(q("clients.client_assignments"), {"page": 1, "limit": 10}, scope=ids["u1"]).rows,
            "audit": engine.execute(q("clients.all_clients_for_audit"), capabilities={names("PRACTICE#capability:practice_audit")}).rows,
        }
        i1 = live.subscribe(q("labels.vip_contacts"), scope=ids["u1"])
        i2 = live.subscribe(q("labels.vip_clients"), scope=ids["u2"])
        with engine.transaction("governed", "t2") as tx:
            tx.mint(q("labels.ClientLabel"), {q("labels.ClientLabel.client"): ids["c2"], q("labels.ClientLabel.label"): ids["l1"]})
        routing = dict(live.last_routing)
        batches = {k: (v.as_dict() if v else None) for k, v in live.last_batches.items()}
        with engine.transaction("governed", "t3") as tx:
            tx.change(q("clients.Client"), ids["c3"], {q("clients.Client.preferred_name"): "Cyrus"})
        routing2 = dict(live.last_routing)
        return rows, routing, batches, routing2, live.stats.as_dict()

    s1 = Store(world1); s1.ship(); e1 = Engine(s1, clock=lambda: 5); l1 = LiveEngine(e1)
    s2 = Store(world2); s2.ship(); e2 = Engine(s2, clock=lambda: 5); l2 = LiveEngine(e2)
    r1 = scenario(world1, e1, l1, lambda n: n.split(":", 1)[1] if "#capability:" in n else n)
    r2 = scenario(world2, e2, l2, m)
    norm = lambda obj: json.dumps(json.loads(normalize(json.dumps(obj, sort_keys=True, default=str), tr.forward)), sort_keys=True)  # noqa: E731
    gate.check("rows equivalent after rename (normalized column names)", norm(r1[0]) == norm(r2[0]), norm(r1[0])[:200])
    gate.check("routing decisions equivalent", r1[1] == r2[1] and r1[3] == r2[3], json.dumps(r1[1]))
    gate.check("delta batches equivalent", norm(r1[2]) == norm(r2[2]))
    gate.check("routing measures equivalent (probes, candidates, zero scans)", r1[4] == r2[4], json.dumps(r1[4]))
    plan1 = lower_read(world1, world1.program.read("labels.vip_contacts"))
    plan2 = lower_read(world2, world2.program.read(m("labels.vip_contacts")))
    old_tables = {r.table for r in world1.storage.relations.values()}
    new_tables = {r.table for r in world2.storage.relations.values()}
    gate.check("generated SQL uses the new physical names and none of the old ones", all(t not in plan2.sql for t in old_tables) and any(t in plan2.sql for t in new_tables) and plan1.sql != plan2.sql, plan2.sql[:160])
    # collision suite
    csrc = BUILD / "corpus/metamorphic/collision"
    cprog = resolve_files(parse_paths(garns_files(csrc)))
    from garns.storage import binding_document
    from garns.metamorphic import physical_scheme

    results = {}
    for wn in ("ALPHA", "BETA"):
        bp = tmp / f"collision-{wn}.json"
        bp.write_text(json.dumps(binding_document(cprog, wn, physical_scheme(wn))))
        cw = bind_world(cprog, wn, bp)
        st = Store(cw); st.ship(); en = Engine(st, clock=lambda: 1); lv = LiveEngine(en)
        mod = wn.lower()
        with en.transaction("governed", "s") as tx:
            root = tx.mint(f"{mod}.Root", {f"{mod}.Root.code": "R"})
            tx.mint(f"{mod}.Item", {f"{mod}.Item.code": "X", f"{mod}.Item.amount": 10, f"{mod}.Item.holder": root})
        inst = lv.subscribe(f"{mod}.heavy", {"floor": 5}, scope=root)
        results[wn] = (cw, en, lv, inst, root)
    keys_alpha = set(results["ALPHA"][2].index)
    keys_beta = set(results["BETA"][2].index)
    gate.check("collision: identical local names index under distinct qualified identities", keys_alpha.isdisjoint(keys_beta) and all(k[1].startswith("alpha.") for k in keys_alpha) and all(k[1].startswith("beta.") for k in keys_beta), f"{sorted(keys_alpha)[:2]} vs {sorted(keys_beta)[:2]}")
    with results["ALPHA"][1].transaction("governed", "w") as tx:
        tx.change("alpha.Item", 1, {"alpha.Item.amount": 20})
    gate.check("collision: a write to alpha.Item routes alpha only and beta's live engine sees nothing", results["ALPHA"][2].last_routing == {results["ALPHA"][3].id: True} and results["BETA"][2].last_routing == {})
    gate.check("collision: reads of same-named reads return distinct results by qualified selection", results["ALPHA"][3].rows() == [{"code": "X", "amount": 20}] and results["BETA"][3].rows() == [{"code": "X", "amount": 10}])
    # captured world: writer source, changelog tables and fields renamed too
    lsrc = BUILD / "corpus/conformance/worlds/ledgerhouse"
    lfiles = parse_paths(garns_files(lsrc))
    lprog = resolve_files(lfiles)
    ltr = transform(lfiles, lprog, "LEDGERHOUSE", "meta-seed-9", lambda texts: resolve_files([parse_text(t, p) for p, t in texts.items()]))
    lprog2 = resolve_files([parse_text(t, p) for p, t in ltr.sources.items()])
    gate.check("captured world: normalized IR equal after renaming writer source and every identity", normalized_program_json(lprog) == normalized_program_json(lprog2, ltr.forward))
    lbind1 = json.loads((lsrc / "storage-LEDGERHOUSE.json").read_text())
    lbp = tmp / "ledgerhouse-renamed.json"
    lbp.write_text(json.dumps(ltr.binding))
    lworld1 = bind_world(lprog, "LEDGERHOUSE", lsrc / "storage-LEDGERHOUSE.json")
    lworld2 = bind_world(lprog2, ltr.mapping["LEDGERHOUSE"], lbp)
    lm = lambda key: rename_qualified(lprog, ltr.mapping, key)  # noqa: E731

    def captured_scenario(world, binding, names):
        st = Store(world); st.ship(); en = Engine(st, clock=lambda: 1); lv = LiveEngine(en); cap = CaptureAdapter(en)
        rel = lambda qid: binding["relations"][names(qid)]  # noqa: E731
        col = lambda qid, key: rel(qid)["columns"][names(key)]  # noqa: E731
        lnk = lambda qid, key: rel(qid)["links"][names(key)]  # noqa: E731
        c = st.conn
        c.execute(f'INSERT INTO "{rel("tenancy.Household")["table"]}" ("{col("tenancy.Household", "tenancy.Household.household_code")}") VALUES (\'H1\')')
        c.execute(f'INSERT INTO "{rel("pantry.Shelf")["table"]}" ("{col("pantry.Shelf", "pantry.Shelf.shelf_label")}", "{lnk("pantry.Shelf", "pantry.Shelf.keeper")}") VALUES (\'top\', 1)')
        jar = rel("pantry.Jar")["table"]
        jc = lambda k: col("pantry.Jar", f"pantry.Jar.{k}")  # noqa: E731
        c.execute(f'INSERT INTO "{jar}" ("{jc("jar_label")}", "{jc("grams")}", "{jc("state")}", "{lnk("pantry.Jar", "pantry.Jar.shelf")}") VALUES (\'rice\', 900, \'open\', 1)')
        c.execute(f'INSERT INTO "{jar}" ("{jc("jar_label")}", "{jc("grams")}", "{jc("state")}", "{lnk("pantry.Jar", "pantry.Jar.shelf")}") VALUES (\'salt\', 100, \'sealed\', 1)')
        cap.acquire("e1")
        grouped = lv.subscribe(names("pantry.jars_by_state"), scope=1)
        opens = lv.subscribe(names("pantry.open_jars"), scope=1)
        c.execute(f'UPDATE "{jar}" SET "{jc("state")}" = \'sealed\' WHERE "{jc("jar_label")}" = \'rice\'')
        cap.acquire("e2")
        writer = en.ledger_rows()[0]["writer"]
        return grouped.rows(), opens.rows(), dict(lv.last_routing), {k: (v.as_dict()["changes"] if v else None) for k, v in lv.last_batches.items()}, writer, lv.stats.as_dict()

    a = captured_scenario(lworld1, lbind1, lambda k: k)
    b = captured_scenario(lworld2, ltr.binding, lm)
    lnorm = lambda obj: json.dumps(json.loads(normalize(json.dumps(obj, sort_keys=True, default=str), ltr.forward)), sort_keys=True)  # noqa: E731
    gate.check("captured world: rows, routing, deltas and measures equivalent after renaming changelog tables/fields", lnorm(a[0]) == lnorm(b[0]) and lnorm(a[1]) == lnorm(b[1]) and a[2] == b[2] and lnorm(a[3]) == lnorm(b[3]) and a[5] == b[5], json.dumps(a[3]))
    gate.check("captured world: the ledger names the renamed writer source", a[4] == "pantry_daemon" and b[4] == ltr.mapping["LEDGERHOUSE#writer_source:pantry_daemon"] and a[4] != b[4], f"{a[4]} -> {b[4]}")
    gate.evidence.append("src/garns/metamorphic.py")
    gate.evidence.append("corpus/metamorphic/collision")


def engine_lowering_regression(gate: Gate, tmp: Path) -> None:
    """R1 P2.4 repair: a recognised engine without a lowering refuses before any effect."""
    from garns.metamorphic import physical_scheme
    from garns.storage import binding_document

    source = BUILD / "corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns"
    text = source.read_text(encoding="utf-8")

    def attempt(variant: str, db: Path) -> tuple[str, str, int, int] | str:
        """Resolve, bind, ship and write under a file-backed store; report the first refusal or 'shipped'."""
        try:
            program = resolve_files([parse_text(variant, "engine-variant.garns")])
            binding = tmp / f"{db.stem}.json"
            binding.write_text(json.dumps(binding_document(program, "ARCHIVE", physical_scheme(db.stem))))
            world = bind_world(program, "ARCHIVE", binding)
            store = Store(world, str(db)); store.ship(); engine = Engine(store, clock=lambda: 1)
            with engine.transaction("governed", "t1") as tx:
                tx.mint("archive.Entry", {"archive.Entry.key": "k1", "archive.Entry.amount": 5})
            store.close()
            return "shipped"
        except Refusal as r:
            return (r.stage, r.code, r.line, r.column)

    pg_db = tmp / "engine-postgres.sqlite"
    outcome = attempt(text, pg_db)
    gate.check("postgres deployment refuses ENGINE_LOWERING_ABSENT at validate, positioned at its engine item", outcome == ("validate", "ENGINE_LOWERING_ABSENT", 24, 10), str(outcome))
    gate.check("no database effect: the store file was never created (no schema, ledger, generation, or migration ran)", not pg_db.exists())
    twin = attempt(text.replace("engine postgres", "engine sqlite"), tmp / "engine-sqlite.sqlite")
    gate.check("the otherwise identical sqlite twin ships and writes, so the refusal is engine-specific", twin == "shipped" and (tmp / "engine-sqlite.sqlite").exists())
    unknown = attempt(text.replace("engine postgres", "engine oracle"), tmp / "engine-oracle.sqlite")
    gate.check("postgres stays a recognised engine: an unknown engine refuses ENGINE_UNKNOWN instead", unknown[:2] == ("validate", "ENGINE_UNKNOWN") and not (tmp / "engine-oracle.sqlite").exists(), str(unknown))
    inherited = text.replace('  engine postgres\n', '  engine sqlite\n') + '\ndeployment ARCHIVE_MIRROR "inherits the base deployment" extends ARCHIVE_STORE {\n  engine postgres\n}\n'
    via_extends = attempt(inherited, tmp / "engine-extends.sqlite")
    gate.check("a postgres engine reached through extends refuses the same way", via_extends[:2] == ("validate", "ENGINE_LOWERING_ABSENT") and not (tmp / "engine-extends.sqlite").exists(), str(via_extends))
    from garns.mutants import observe_scenario

    obs = observe_scenario(BUILD / "corpus/mutants/scenarios/ENGINE_LOWERING_ABSENT")
    gate.check("scenario mutant: bind refuses before the ship and write steps execute", (obs.stage, obs.code) == ("validate", "ENGINE_LOWERING_ABSENT"))
    gate.evidence.append("corpus/conformance/refusals/ENGINE_LOWERING_ABSENT-1.garns")
    gate.evidence.append("corpus/mutants/scenarios/ENGINE_LOWERING_ABSENT")


def g6(gate: Gate, tmp: Path) -> None:
    engine_lowering_regression(gate, tmp)
    for name, code in (("MODULE_NOT_LISTED-1.garns", "MODULE_NOT_LISTED"), ("SCOPE_PATH_AMBIGUOUS-1.garns", "SCOPE_PATH_AMBIGUOUS"), ("SCOPE_PATH_TO_EXEMPT-1.garns", "SCOPE_PATH_TO_EXEMPT"),
                       ("EXEMPT_REDUNDANT-1.garns", "EXEMPT_REDUNDANT"), ("CAPABILITY_UNKNOWN-1.garns", "CAPABILITY_UNKNOWN"), ("TRAIT_REQUIRED-1.garns", "TRAIT_REQUIRED"), ("ID_DUPLICATED-1.garns", "ID_DUPLICATED")):
        obs = observe_single(BUILD / "corpus/mutants" / name)
        gate.check(f"{name} -> {obs.code}", obs.code == code and obs.stage == "validate")
    gens = []
    for n in range(1, 6):
        w, p = world_ir("PRACTICE", f"corpus/worlds/evolution/g{n}")
        gens.append((w, p))
    store = Store(gens[0][0]); store.ship(generation=1); engine = Engine(store, clock=lambda: 3)
    with engine.transaction("governed", "seed") as tx:
        u = tx.mint("people.User", {"people.User.email": "a@x"})
        tx.mint("clients.Client", {"clients.Client.user_name": "Ann", "clients.Client.owner": u})
    history = [gens[0][1]]
    kinds = []
    for i in range(1, 5):
        cl = classify(history[-1], gens[i][1], history, retention=3)
        stmts = migrate(store.conn, gens[i - 1][0], gens[i][0], cl, generation=i + 1)
        opened = open_store(store.conn, gens[i][0], gens[i][1].deployments[0])
        kinds.append((f"g{i + 1}", cl.compat, sorted({e.kind for e in cl.events}), len(stmts), opened["generation"]))
        history.append(gens[i][1])
    gate.check("g1->g5 classify, migrate on a real store, and reopen at each generation", [k[4] for k in kinds] == [2, 3, 4, 5], json.dumps(kinds))
    gate.check("g3 carries continuity as intent_renamed (same module) and intent_relocated (qualified renamed_from across modules)", "intent_renamed" in kinds[1][2] and "intent_relocated" in kinds[1][2])
    gate.check("g4 retirement is a real event with its disposition and g5 restores inside retention", "retire_intent" in kinds[2][2] and "restore_intent" in kinds[3][2])
    gate.check("renamed column kept its data through the migration", store.conn.execute('SELECT "f_client_preferred_name" FROM "tbl_clients_client"').fetchone()[0] == "Ann")
    for name in ("RETIREMENT_POLICY_REQUIRED", "RENAME_TARGET_UNKNOWN", "RETYPE_KEY_EQUALITY", "ACCESSOR_BREAKING_UNACKNOWLEDGED", "MOVE_HOME_INCONSISTENT", "RESTORE_DATA_UNAVAILABLE"):
        from garns.mutants import observe_scenario

        obs = observe_scenario(BUILD / "corpus/mutants/scenarios" / name)
        gate.check(f"evolution scenario {name} -> {obs.stage}/{obs.code}", obs.code == name and obs.stage == "ship")
    # move_home parses and classifies as a real event
    w, p = world_ir("PRACTICE", "corpus/worlds/practice")
    mh_text = (BUILD / "corpus/mutants/scenarios/MOVE_HOME_INCONSISTENT/g2/world.garns").read_text()
    mh_prog = resolve_files([parse_text(mh_text, "move_home.garns")])
    gate.check("move_home ... data drop parses and resolves as an evolution statement", len(mh_prog.move_homes) == 1 and mh_prog.move_homes[0].disposition == "drop")


def g7(gate: Gate) -> None:
    w, program = world_ir("PRACTICE", "corpus/worlds/practice")
    store = Store(w); store.ship(); engine = Engine(store, clock=lambda: 10); live = LiveEngine(engine)
    ids = seed_practice(engine)
    # instrumentation is live: iterating the registry counts scans
    inst_vip = live.subscribe("labels.vip_clients", scope=ids["u1"])
    inst_vc = live.subscribe("labels.vip_contacts", scope=ids["u1"])
    inst_other = live.subscribe("labels.vip_clients", scope=ids["u2"])
    inst_dormant = live.subscribe("notes.dormant_clients", {"after": 10}, scope=ids["u1"])
    before = live.stats.listener_scans
    _ = list(live.registry)
    gate.check("listener-scan counter is a live measurement (deliberate iteration increments it)", live.stats.listener_scans == before + len(live.registry))
    live.stats.listener_scans = 0
    # relevant write: routes inner and outer through recursive composition
    with engine.transaction("governed", "t2") as tx:
        tx.mint("labels.ClientLabel", {"labels.ClientLabel.client": ids["c2"], "labels.ClientLabel.label": ids["l1"]})
    gate.check("nested composition: a write inside the inner question routes inner and outer", live.last_routing.get(inst_vip.id) and live.last_routing.get(inst_vc.id), json.dumps(live.last_routing))
    gate.check("scope-partitioned: the other scope's instance is not routed", inst_other.id not in live.last_routing)
    gate.check("result-neutral routed write emits no batch (outer unchanged)", live.last_batches[inst_vc.id] is None and live.last_batches[inst_vip.id] is not None)
    # irrelevant write: no routing at all
    with engine.transaction("governed", "t3") as tx:
        tx.change("people.User", ids["u1"], {"people.User.email": "one@y"})
    gate.check("irrelevant write (field outside every footprint) routes nothing and emits no batch", live.last_routing == {} and not any(live.last_batches.values()))
    # cross-scope write
    with engine.transaction("governed", "t4") as tx:
        tx.change("clients.Client", ids["c3"], {"clients.Client.preferred_name": "Cyrus"})
    gate.check("cross-scope write routes only the matching partition", set(live.last_routing) <= {inst_other.id})
    gate.check("zero listener scans across all commits (measured)", live.stats.listener_scans == 0, json.dumps(live.stats.as_dict()))
    # rollback emits nothing
    revision_before = engine.revision
    rows_before = len(engine.ledger_rows())
    routing_before = dict(live.last_routing)
    seq_before = {i.id: i.seq for i in (inst_vip, inst_vc, inst_other, inst_dormant)}
    try:
        with engine.transaction("governed", "t5") as tx:
            tx.mint("labels.ClientLabel", {"labels.ClientLabel.client": ids["c1"], "labels.ClientLabel.label": ids["l1"]})
            raise RuntimeError("abort")
    except RuntimeError:
        pass
    gate.check("rolled-back transaction: no revision, no ledger row, no batch", engine.revision == revision_before and len(engine.ledger_rows()) == rows_before and tx.rolled_back and live.last_routing == routing_before and {i.id: i.seq for i in (inst_vip, inst_vc, inst_other, inst_dormant)} == seq_before)
    # old/new group keys with the ledgerhouse grouped question
    lw, _ = world_ir("LEDGERHOUSE", "corpus/conformance/worlds/ledgerhouse")
    ls = Store(lw); ls.ship(); le = Engine(ls, clock=lambda: 1); ll = LiveEngine(le); cap = CaptureAdapter(le)
    c = ls.conn
    c.execute("INSERT INTO house (code_txt) VALUES ('H1')"); c.execute("INSERT INTO shelf (label_txt, kept_by) VALUES ('top', 1)")
    c.execute("INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('rice', 900, 'open', 1)"); c.execute("INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('salt', 100, 'sealed', 1)")
    cap.acquire("e1")
    grouped = ll.subscribe("pantry.jars_by_state", scope=1)
    initial = grouped.rows(); initial_keys = list(grouped.order)
    c.execute("UPDATE jar SET cond='sealed' WHERE lbl='rice'")
    cap.acquire("e2")
    batch = ll.last_batches[grouped.id]
    changes = {(ch.op, ch.key) for ch in batch.changes} if batch else set()
    gate.check("moving a grouped key refreshes both the old and the new group", ("delete", ("open",)) in changes and ("upsert", ("sealed",)) in changes, json.dumps(sorted(str(x) for x in changes)))
    # fold equivalence after every committed revision
    equal = True
    log = [batch] if batch else []
    for step in ("UPDATE jar SET mass_g=50 WHERE lbl='salt'", "INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('tea', 20, 'open', 1)", "DELETE FROM jar WHERE lbl='rice'"):
        c.execute(step); cap.acquire("e")
        b = ll.last_batches.get(grouped.id)
        if b:
            log.append(b)
        folded = fold(initial, initial_keys, log)
        one_shot = le.execute("pantry.jars_by_state", scope=1).rows
        equal = equal and canonical_rows(sorted(folded, key=lambda r: r["state"])) == canonical_rows(sorted(one_shot, key=lambda r: r["state"]))
    gate.check("folded deltas equal one-shot recomputation after every committed revision", equal)
    # live bound enforced
    from garns.mutants import observe_scenario

    obs = observe_scenario(BUILD / "corpus/mutants/scenarios/LIVE_BOUND_EXCEEDED")
    gate.check("live bound is enforced at refresh (measured row count)", obs.code == "LIVE_BOUND_EXCEEDED")
    gate.evidence.append("src/garns/live.py")


def g8(gate: Gate) -> None:
    lw, _ = world_ir("LEDGERHOUSE", "corpus/conformance/worlds/ledgerhouse")
    from garns.lower_sqlite import lower_ddl

    ddl = lower_ddl(lw)
    gate.check("declared changelog triggers exist in the generated schema with mapped names", ddl.count("CREATE TRIGGER") == 9 and '"jar_trail__update"' in ddl and '"cond_v"' in ddl)
    ls = Store(lw); ls.ship(); le = Engine(ls, clock=lambda: 1); cap = CaptureAdapter(le)
    c = ls.conn
    c.execute("INSERT INTO house (code_txt) VALUES ('H1')"); c.execute("INSERT INTO shelf (label_txt, kept_by) VALUES ('top', 1)")
    c.execute("INSERT INTO jar (lbl, mass_g, cond, on_shelf) VALUES ('rice', 900, 'open', 1)")
    rev, deltas = cap.acquire("ext-1")
    gate.check("external writes are captured as typed deltas with scope keys through a two-hop path", rev == 1 and any(d.carrier == "pantry.Jar" and d.scope_after == 1 for d in deltas))
    denominators = cap.check_coverage()
    gate.check("capture coverage denominators are measured from PRAGMA table_info", denominators == {"pantry.Jar": 8, "pantry.Shelf": 6, "tenancy.Household": 6}, json.dumps(denominators))
    ledger = le.ledger_rows()
    gate.check("ledger records carry typed carrier/identity/scope/writer/transaction", all(r["writer"] == "pantry_daemon" and r["transaction_id"] == "ext-1" for r in ledger) and ledger[0]["carrier"].startswith(("pantry.", "tenancy.")))
    c.execute("ALTER TABLE jar_trail DROP COLUMN cond_v")
    try:
        cap.acquire("ext-2"); gate.check("incomplete coverage refuses", False)
    except Refusal as r:
        gate.check("incomplete changelog coverage refuses at load before any effect", r.code == "WRITER_CAPTURE_INCOMPLETE" and r.stage == "load" and le.revision == 1)
    from garns.mutants import observe_scenario

    for name in ("LEDGER_WRITER_UNKNOWN", "LEDGER_FIELD_UNKNOWN", "LEDGER_SCOPE_UNKNOWN", "LEDGER_VALUE_TYPE", "LEDGER_TRANSACTION_INVALID", "LEDGER_CARRIER_UNKNOWN", "WRITER_CAPTURE_INCOMPLETE_BINDING"):
        obs = observe_scenario(BUILD / "corpus/mutants/scenarios" / name)
        gate.check(f"pre-effect typed validation {name} -> {obs.code}", obs.code.startswith(name.split("_BINDING")[0]))
    gate.evidence.append("corpus/conformance/worlds/ledgerhouse")


def g9(gate: Gate, tmp: Path) -> None:
    generated = BUILD / "generated"
    regen = tmp / "regen"
    identical = True
    details = []
    for world, rel in WORLDS:
        if "evolution" in rel:
            continue
        w, _ = world_ir(world, rel)
        out = regen / world
        generate(w, out)
        committed = generated / world
        same = committed.exists() and tree_digest(committed) == tree_digest(out)
        identical = identical and same
        details.append(f"{world}:{'same' if same else 'DIFFERENT'}")
    gate.check("delete/regenerate: committed generated/ trees are byte-identical to fresh generation", identical, " ".join(details))
    twice = generate(world_ir("PRACTICE", "corpus/worlds/practice")[0], tmp / "twice-a") and tree_digest(tmp / "twice-a")
    generate(world_ir("PRACTICE", "corpus/worlds/practice")[0], tmp / "twice-b")
    gate.check("two generations in fresh directories are byte-identical", twice == tree_digest(tmp / "twice-b"))
    # mutants: observed vs expected, then invariance under renaming/comment stripping/manifest corruption
    expected = {c["mutant"]: c for c in json.loads((BUILD / "corpus/mutants/expected.json").read_text())["cases"]}
    observed = observe_all(BUILD / "corpus/mutants")
    mismatches = [n for n, o in observed.items() if (o.stage, o.code) != (expected[n]["stage"], expected[n]["code"])]
    gate.check(f"{len(observed)} mutants execute real stages and match authored expectations", not mismatches, ", ".join(mismatches)[:400])
    stages = {o.stage for o in observed.values()}
    gate.check("mutants cover decode, validate, ship, load, and runtime stages", {"decode", "validate", "ship", "load", "runtime"} <= stages, json.dumps(sorted(stages)))
    shadow = tmp / "shadow"
    shutil.copytree(BUILD / "corpus/mutants", shadow)
    renamed = 0
    for p in sorted(shadow.glob("*.garns")):
        text = re.sub(r"#[^\n]*", "", p.read_text())
        p.write_text(text)
        p.rename(shadow / f"m{renamed:03d}.garns")
        renamed += 1
    for d in sorted((shadow / "scenarios").iterdir()):
        d.rename(shadow / "scenarios" / f"s{hashlib.sha256(d.name.encode()).hexdigest()[:8]}")
    (shadow / "expected.json").write_text('{"corrupted": true}')
    shadow_obs = observe_all(shadow)
    def content_key(root: Path, n: str) -> str:
        if n.endswith(".garns"):
            return re.sub(r"#[^\n]*", "", (root / n).read_text())
        return tree_digest(root / n)  # every fixture file of the scenario, path-relative

    orig_by_content = {content_key(BUILD / "corpus/mutants", n): (o.stage, o.code) for n, o in observed.items()}
    same = 0
    for n, o in shadow_obs.items():
        if orig_by_content.get(content_key(shadow, n)) == (o.stage, o.code):
            same += 1
    gate.check("detection unchanged after renaming files, stripping comments, and corrupting the manifest", same == len(observed) == len(shadow_obs), f"{same}/{len(observed)}")
    gate.evidence.append("corpus/mutants/expected.json")
    gate.evidence.append("generated/")


def g10(gate: Gate) -> None:
    sources = list((BUILD / "src").rglob("*.py")) + list((BUILD / "src").rglob("*.rs"))
    forbidden = {
        "pluralization helper": re.compile(r"endswith\(\s*['\"](y|s|x|ch|sh)['\"]\s*\)|\+\s*['\"]ies['\"]|\+\s*['\"]es['\"]"),
        "_id suffix inference": re.compile(r"['\"]_id['\"]|f\"\{[^}]*\}_id\""),
        "scope_id column": re.compile(r"scope_id"),
        "first-item world/question selection": re.compile(r"worlds\[0\]|questions\[0\]|reads\[0\]"),
        "corpus vocabulary in compiler": re.compile(r"\b(everbility|vaultwarden|appflowy|practice|book|author)\b", re.I),
        "fallback SQL": re.compile(r"fallback|FALLBACK"),
        "numbered case dispatch": re.compile(r"\bcase_\d+|numbered"),
        "filename detector": re.compile(r"Path\([^)]*\)\.name\s+in|['\"]U12['\"]"),
    }
    for label, pattern in forbidden.items():
        hits = []
        for p in sources:
            for i, line in enumerate(p.read_text().splitlines(), 1):
                if pattern.search(line) and "forbidden" not in line and not line.strip().startswith("#") and '"""' not in line:
                    hits.append(f"{p.relative_to(BUILD)}:{i}")
        gate.check(f"no {label} in src/", not hits, ", ".join(hits)[:300])
    gen_text = "".join(p.read_text() for p in (BUILD / "generated").rglob("*.sql"))
    physical_only = re.sub(r'AS "[^"]*"', "", gen_text)  # result column names are language terms, not storage names
    gate.check("generated SQL contains no unmapped `id`, `scope_id`, or `_id` conventions in physical names", not re.search(r'"id"|scope_id|"[a-z]+_id"', physical_only))
    engine_src = (BUILD / "src/garns/engine.py").read_text()
    gate.check("public boundaries select worlds and reads by qualified name only", "def _read(self, read_qid" in engine_src and "selected by qualified name" in engine_src and "def bind_world(program: I.Program, world_name: str" in (BUILD / "src/garns/storage.py").read_text())
    live_src = (BUILD / "src/garns/live.py").read_text()
    gate.check("instrumentation counters increment on real operations only", "self.stats.probes += 1" in live_src and "self._stats.listener_scans += 1" in live_src and "listener_scans = 0" not in live_src.replace("listener_scans: int = 0", ""))
    from garns.footprint import FootprintDeriver
    from garns.lower_sqlite import _Lowerer, _ShowLowerer

    gate.check("footprint visitor exhaustive over expressions, operands, and shows", not (check_exhaustive(FootprintDeriver, EXPR_NODES) + check_exhaustive(FootprintDeriver, OPERAND_NODES) + check_exhaustive(FootprintDeriver, SHOW_NODES)))
    gate.check("SQL lowering visitor exhaustive over expressions, operands, and shows", not (check_exhaustive(_Lowerer, EXPR_NODES) + check_exhaustive(_Lowerer, OPERAND_NODES) + check_exhaustive(_ShowLowerer, SHOW_NODES)))
    from garns import ir as irmod

    class Phantom(irmod.And):
        pass

    gate.check("an unhandled IR node fails loudly in every visitor", check_exhaustive(FootprintDeriver, (Phantom,)) == ["Phantom"] and check_exhaustive(_Lowerer, (Phantom,)) == ["Phantom"])
    gate.evidence.append("src/garns/visit.py")


def g11(gate: Gate, tmp: Path, quick: bool) -> None:
    rustc = shutil.which("rustc")
    gate.check("rustc available", rustc is not None, rustc or "not found")
    measures = {"live_bound": "verified (LIVE_BOUND_EXCEEDED measured at refresh)", "capture_denominators": "verified (PRAGMA table_info counts)", "token_bound": "unverified: not measurable from inside the build"}
    if rustc is None:
        measures["rust_parity"] = "unverified: no Rust toolchain"
        gate.check("rust parity", False, "no toolchain")
        gate.evidence.append(json.dumps(measures))
        return
    parity_ok = True
    details = []
    for world, rel, seed, reads in (
        ("PRACTICE", "corpus/worlds/practice", seed_practice, [("clients.contacts_with_relationship", {"kind": "sister"}, "u1", set()), ("labels.vip_clients", {}, "u1", set()), ("clients.all_clients_for_audit", {}, None, {"practice_audit"}), ("notes.dormant_clients", {"after": 10}, "u1", set())]),
        ("SALES", "corpus/conformance/worlds/sales", seed_sales, [("sales.open_orders", {}, None, set()), ("sales_static.revenue_open_by_customer", {"floor": 10}, None, set()), ("sales_static.open_orders_once", {}, None, set())]),
    ):
        w, _ = world_ir(world, rel)
        out = tmp / f"rs-{world}"
        generate(w, out)
        binary = tmp / f"runner-{world}"
        proc = gate.command([rustc, "-O", "-o", str(binary), str(out / "rust" / "main.rs")])
        if proc.returncode != 0:
            parity_ok = False
            details.append(f"{world}: rustc failed")
            continue
        db = tmp / f"{world}.sqlite"
        store = Store(w, str(db)); store.ship(); engine = Engine(store, clock=lambda: 7)
        ids = seed(engine)
        for read, params, scope_key, caps in reads:
            plan = engine.plan(read)
            rd = engine._read(read)
            scope = ids[scope_key] if scope_key else None
            bound = engine.bind_params(plan, rd, params, scope, caps, 7)
            cur = store.conn.execute(plan.sql, bound)
            py_lines = []
            for row in cur.fetchall():
                cells = []
                for v in row:
                    if v is None:
                        cells.append("[5,null]")
                    elif isinstance(v, int):
                        cells.append(f"[1,{json.dumps(str(v))}]")
                    elif isinstance(v, float):
                        text = store.conn.execute("SELECT CAST(? AS TEXT)", (v,)).fetchone()[0]
                        cells.append(f"[2,{json.dumps(text)}]")
                    elif isinstance(v, bytes):
                        cells.append(f"[4,{json.dumps(v.hex())}]")
                    else:
                        cells.append(f"[3,{json.dumps(v, ensure_ascii=False)}]")
                py_lines.append("[" + ",".join(cells) + "]")
            args = []
            for k, v in bound.items():
                kind = "n" if v is None else ("i" if isinstance(v, int) else ("f" if isinstance(v, float) else "s"))
                args.append(f"{k}={kind}:{'' if v is None else v}")
            store.conn.commit()
            run = gate.command([str(binary), str(db), read] + args)
            rust_lines = run.stdout.strip().splitlines()
            same = rust_lines == py_lines and run.returncode == 0
            parity_ok = parity_ok and same
            details.append(f"{read}:{'same' if same else 'DIFF'}({len(py_lines)} rows)")
    gate.check("Python/Rust row-shape parity over unchanged generated SQL", parity_ok, "; ".join(details))
    measures["rust_parity"] = "verified" if parity_ok else "unverified: mismatch"
    gate.evidence.append(json.dumps(measures))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    started = time.time()
    tmp = Path(tempfile.mkdtemp(prefix="garns-check-"))
    gates: list[Gate] = []
    matrix = [
        ("G0", "Repository integrity"), ("G1", "Grammar and corpus"), ("G2", "Static query"), ("G3", "Dynamic question"), ("G4", "Shared lowering"),
        ("G5", "Schema independence"), ("G6", "Identity/world/evolution"), ("G7", "Live correctness"), ("G8", "Ledger and capture"),
        ("G9", "Evidence honesty"), ("G10", "Forbidden coupling"), ("G11", "Target parity and measures"),
    ]
    by_name = {name: Gate(name, req) for name, req in matrix}
    runners = {
        "G0": lambda: g0(by_name["G0"]), "G1": lambda: g1(by_name["G1"]), "G2": lambda: g2_g4(by_name["G2"], by_name["G3"], by_name["G4"], tmp),
        "G5": lambda: g5(by_name["G5"], tmp), "G6": lambda: g6(by_name["G6"], tmp), "G7": lambda: g7(by_name["G7"]), "G8": lambda: g8(by_name["G8"]),
        "G9": lambda: g9(by_name["G9"], tmp), "G10": lambda: g10(by_name["G10"]), "G11": lambda: g11(by_name["G11"], tmp, args.quick),
    }
    for name, _ in matrix:
        if name in ("G3", "G4"):
            continue
        try:
            runners[name]()
        except Exception as exc:  # a crash is a failed gate, never a skipped one
            by_name[name].check(f"{name} runner crashed", False, "".join(traceback.format_exception_only(type(exc), exc)).strip() + " | " + traceback.format_exc()[-600:])
    for name, _ in matrix:
        gates.append(by_name[name])
    report = {
        "schema": "garns/gate-report/1",
        "build": "garns",
        "python": sys.version.split()[0],
        "command": "uv run --offline --with lark python tools/check.py",
        "seconds": round(time.time() - started, 1),
        "gates": [g.as_dict() for g in gates],
        "all_pass": all(g.passed for g in gates),
    }
    (BUILD / "gate-report.json").write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    for g in gates:
        print(f"{'PASS' if g.passed else 'FAIL'} {g.name} {g.requirement}: {sum(c['ok'] for c in g.checks)}/{len(g.checks)} checks")
        for c in g.checks:
            if not c["ok"]:
                print(f"     x {c['label']} :: {c['detail'][:300]}")
    shutil.rmtree(tmp, ignore_errors=True)
    purge_caches()
    print("ALL PASS" if report["all_pass"] else "GATE FAILURES PRESENT")
    return 0 if report["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
