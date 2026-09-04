# Provenance

This repository was cut on 2026-09-04 from the unanimously ratified B2 build of
the `datascad/garns-v9-5` convergence lane.

- Selected build: `datascad/garns-v9-5/build/B2`
- Original complete B2 composite SHA-256:
  `eaf4937f853861f76c26be55f5f8903b8b90caeb729ecec40315f93f3b5eb60b`
- Documentation source: `datascad/garns-v9-5/docs-staging/F51`
- Documentation composite SHA-256:
  `dc3fe76f79dc02291768c939e89331558970c49bfd87a637630238297dd69825`
- Independent final verdicts: R1 `ratify`; R2 `ratify`
- Original unit evidence: 103/103 tests
- Original gate evidence: 128/128 checks across G0-G11
- Original mutant evidence: 168/168 outcomes

The initial cut copied `corpus/`, `generated/`, `grammar/`, `src/`, `tests/`,
and `tools/` byte-for-byte before repository packaging changes, together with
all eleven final documentation files. The per-tree source hashes are recorded
in `CUT_MANIFEST.json`.

The original review lane remains the authority for builder comparisons,
private attacks, the bounded PostgreSQL repair, and final ratification. Those
experimental and review artifacts are intentionally not product dependencies.
