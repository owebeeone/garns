"""Command-line entry points.

    garns resolve <source-dir>
    garns generate <source-dir> --world W --binding B --out DIR
    garns execute <source-dir> --world W --binding B --read module.name [--param k=v]... [--scope N] [--capability C]...
    garns ddl <source-dir> --world W --binding B

Every public boundary requires an explicit qualified world and read; nothing
is selected by position.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .engine import Engine, Store
from .generate import generate
from .lower_sqlite import lower_ddl
from .parse import garns_files, parse_paths
from .refuse import Refusal
from .resolve import resolve_files
from .storage import bind_world
from .ir import canonical_json


def _program(source: str):
    return resolve_files(parse_paths(garns_files(Path(source))))


def _world(args):
    program = _program(args.source)
    return bind_world(program, args.world, Path(args.binding))


def cmd_resolve(args) -> int:
    program = _program(args.source)
    sys.stdout.write(canonical_json(program) if args.json else f"resolved {len(program.modules)} modules, {len(program.carriers)} carriers, {len(program.reads)} reads, {len(program.worlds)} worlds\n")
    return 0


def cmd_generate(args) -> int:
    world = _world(args)
    files = generate(world, Path(args.out))
    print(f"generated {len(files)} files under {args.out}")
    return 0


def cmd_ddl(args) -> int:
    sys.stdout.write(lower_ddl(_world(args)))
    return 0


def cmd_execute(args) -> int:
    world = _world(args)
    store = Store(world, args.store or ":memory:")
    if args.ship:
        store.ship()
    engine = Engine(store)
    params = {}
    for p in args.param or []:
        k, v = p.split("=", 1)
        params[k] = json.loads(v)
    result = engine.execute(args.read, params, args.scope, set(args.capability or []))
    sys.stdout.write(json.dumps({"rows": result.rows, "total": result.total}, indent=1, sort_keys=True, default=str) + "\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="garns")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("resolve"); r.add_argument("source"); r.add_argument("--json", action="store_true"); r.set_defaults(fn=cmd_resolve)
    for name, fn in (("generate", cmd_generate), ("ddl", cmd_ddl), ("execute", cmd_execute)):
        s = sub.add_parser(name); s.add_argument("source"); s.add_argument("--world", required=True); s.add_argument("--binding", required=True); s.set_defaults(fn=fn)
        if name == "generate":
            s.add_argument("--out", required=True)
        if name == "execute":
            s.add_argument("--read", required=True); s.add_argument("--param", action="append"); s.add_argument("--scope", type=int); s.add_argument("--capability", action="append")
            s.add_argument("--store"); s.add_argument("--ship", action="store_true")
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except Refusal as refusal:
        print(f"refused: {refusal}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
