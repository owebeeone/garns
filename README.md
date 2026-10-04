# Garns

Garns is a declarative language for stating what data means once and deriving
relational schema, queries, live-subscription metadata, ledger/capture
contracts, migrations and generated surfaces from that meaning.

This directory is the single convergent v9-6 product tree. Its current W0
baseline is the repaired and ratified v9-5 B2 compiler and SQLite semantic
reference. PostgreSQL-primary execution and the async-only public runtime are
the v9-6 direction; they are not yet implemented by the W0 baseline.

Start with:

- [Current implementation guide](docs/README.md)
- [v9-6 direction](docs/GARNS_DIRECTION.md)
- [Product layout and ownership](docs/PRODUCT_LAYOUT.md)
- [W0 execution brief](dev-docs/GarnsV9-6-W0-ExecutionBrief.md)
- [Binding launch decisions](dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md)

## Baseline commands

Run from this directory without network access:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -m unittest discover -s tests -t .
PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B tools/check.py
```

The supported Python range begins at 3.11 and has no package-metadata upper
bound. Release evidence must test every stable CPython minor in the claimed
range.
