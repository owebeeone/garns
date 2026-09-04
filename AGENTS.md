# Garns contributor instructions

Read the parent workspace's `AGENTS_GWZ.md` before making changes. Use `gwz`
for workspace-wide status, staging, commits, history, and member topology.

`garns` owns the language grammar, Python compiler/runtime, portable artifact
contracts, conformance corpus, and generated evidence. It must not depend on
Glade, Taut, or the sibling `garns-rust` repository. Downstream runtimes and
adapters consume versioned Garns artifacts.

Before changing code, read `AI_DEVELOPER_GUIDE.md` and the relevant playbook in
`EXTENDING_GARNS.md`. Preserve qualified identity, explicit storage binding,
one typed IR, exhaustive visitors, deterministic generation, and typed refusal
before effects.

Run Python with `PYTHONDONTWRITEBYTECODE=1`. The minimum verification is:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --offline --with lark python -B -m unittest discover -s tests -t .
```

Generated files and corpus manifests are evidence. Do not hand-edit them; use
their owning tools and verify byte-identical regeneration.
