# Garns v9-6 W0 execution brief — promote and rebaseline B2

**Status:** prepared for launch; W0 output is not accepted until the manager
verifies every exit item below  
**Prepared:** 2026-10-03  
**Package:** W0  
**Delivery shape:** one convergent implementation

## 1. Objective

Create the canonical clean Garns v9-6 product repository from the repaired and
ratified v9-5 B2 implementation. This is a mechanical promotion and rebaseline,
not an architecture or feature package.

W0 must preserve the selected semantics, remove evaluation-lane structure from
the product, establish ordinary package/test entry points, materialize the
approved root layout and produce stable evidence for W1.

## 2. Binding inputs

### Reviewed architecture tuple

| Input | SHA-256 |
|---|---|
| `dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md` | `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512` |
| `dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md` | `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01` |

The builder also reads
`dev-docs/GarnsV9-6-OperatorDecisions-D6a-D7-D8.md` at SHA-256
`079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f`.
Any mismatch stops launch.

### Selected implementation

- Source root: `/Volumes/projects/limbo/datascad/garns-v9-5/build/B2/`.
- R2's final ratification records 569 non-`__pycache__` files and tree digest
  `09591d3f6809b33a7edeffe6f3251075f9486dae517ed633a0a9abd6d3d2247a`
  using sorted relative path, NUL, bytes, NUL hashing.
- The builder must independently reproduce that digest before promotion. A
  mismatch stops W0; it is not repaired or normalized silently.
- `build/B1/` and `build/B3/` are rejected inputs.

### Product documentation

Promote the current files under `docs-staging/F51/`:

- `README.md`
- `GARNS_DIRECTION.md`
- `ARCHITECTURE.md`
- `LIMITATIONS.md`
- `DSL_REFERENCE.md`
- `COMPILER_PIPELINE.md`
- `DIAGNOSTICS.md`
- `INTEGRATION.md`
- `TESTING.md`
- `EXTENDING_GARNS.md`
- `AI_DEVELOPER_GUIDE.md`
- `DOCUMENTATION_REPORT.md`

Statements made obsolete by the v9-6 direction remain visibly identified as
current B2 limitations. W0 must not rewrite them as completed v9-6 features.

### Stable inherited evidence

Copy these records into `evidence/v9-5-b2/` and include their path and SHA-256
in `evidence/v9-5-b2/MANIFEST.sha256`:

| Source | Current SHA-256 |
|---|---|
| `build/B2/REPORT.md` | `9da82bdd8a2d0b0a5f183d190e978403c84d46cd2647da8ef6232fe0bb999685` |
| `build/B2/REPAIR.md` | `54cf2362e075953da004f3dae49ad3320a34844e439f8ff694260ec06fbcb0a0` |
| `reviews/R1/REVIEW.md` | `c47b808d2540650e83f08d099c68c1db39f9098c170200a108fcb2bdbd7d795a` |
| `reviews/R2/REVIEW.md` | `b53f89c72261af9e5a5bd28efed07ed392a01d6623b83529936407a4c82a1ada` |

Copy the accepted plan, amendment, acceptance synthesis, this brief and the
operator-decision record into the product's durable planning/evidence area as
ordinary documentation. Record their copied-byte hashes in the W0 report.

## 3. Roots and write ownership

- Canonical target: `/Volumes/projects/limbo/datascad/garns-v9-6/`.
- The manager creates/registers that workspace member through `gwz` before the
  builder starts. Neither manager nor builder edits `gwz.conf/` directly.
- The W0 builder is the sole writer to the entire new root for this package.
- `/Volumes/projects/limbo/datascad/garns-v9-5/` is read-only input.
- No W1 builder or research sub-lane starts until the manager accepts W0.

W0 materializes at least these relative roots:

```text
src/garns/
grammar/
corpus/
tests/
tests/support/postgres/
tools/
tools/postgres/
docs/
docs/adr/
dev-docs/
evidence/v9-5-b2/
research/api-docs/
research/postgres-codecs/
research/capture/
```

The builder writes `docs/PRODUCT_LAYOUT.md` with the W1–W8 ownership and
handoff table from the accepted plan. Empty allocated research roots may use a
short README explaining that research is non-product and non-mergeable.

## 4. Archive and promotion policy

Promote product inputs, not the v9-5 evaluation lane.

The new product includes B2 source, grammar, corpus, tests, generation tooling
and any generated artifacts that reproduce from the promoted sources. It does
not include:

- `build/B1/` or `build/B3/`;
- v9-5 builder prompts or comparative manager machinery;
- reviewer sandboxes, ratification worktrees, temporary files or private
  execution copies;
- the v9-5 scaffold checker as a product runtime dependency;
- candidate selection, numbered-case or lane-path behavior; or
- stale generated output that cannot be reproduced from the promoted source.

The original v9-5 member remains the immutable historical archive. W0 copies
only the stable evidence named above; it never deletes or reorganizes that
member.

## 5. Required work

1. Verify the exact input tuple and selected-B2 tree digest.
2. Confirm the target is the registered empty/canonical v9-6 workspace member.
3. Promote B2 into ordinary product paths; remove `build/B2` path assumptions
   from package imports, test discovery, tools and user documentation.
4. Promote F51 documentation and the accepted planning tuple without claiming
   unimplemented PostgreSQL or async behavior.
5. Add ordinary package metadata with `requires-python = ">=3.11"` and no
   upper bound.
6. Define clean unit, integration, generation and gate commands that do not
   depend on the old lane root.
7. Materialize `docs/PRODUCT_LAYOUT.md` and every root allocated by D8.
8. Create the stable evidence bundle and checksum manifest.
9. Delete and regenerate generated artifacts from product source, then compare
   path and byte hashes.
10. Run the full inherited suite and record exact commands, interpreter
    versions, exits, counts and artifact hashes.
11. Audit product docs, manifests and generated artifacts for absolute v9-5
    lane paths and candidate-selection terminology.
12. Write `dev-docs/W0-REPORT.md` containing the input hashes, transformations,
    test evidence, deviations and final target-tree digest.

Mechanical import/path repairs needed to make the promoted tree ordinary are
in scope. Semantic redesign is not.

## 6. Python verification

Package metadata is exactly `>=3.11`. The W0 compatibility evidence covers
CPython 3.11, 3.12, 3.13 and 3.14 in clean environments. If another stable
minor exists at execution time, add it to the matrix.

The local absence of one interpreter may be handled by the approved CI or
clean-environment mechanism. It must be reported honestly and cannot be
represented as a local pass.

## 7. Required exit evidence

W0 passes only when all of the following hold:

- the selected input digest and every binding document digest match;
- at least 103 inherited unit tests pass, with every count change explained;
- all 128 inherited G0–G11 checks pass through product-owned entry points;
- all 168 inherited mutant expectations pass without expected-answer or
  filename/comment dispatch;
- generated artifacts reproduce byte-for-byte after deletion;
- grammar SHA-256 remains
  `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`;
- the real Rust parity check still compiles and executes independently;
- Python compatibility evidence satisfies section 6;
- no product source imports or executes v9-5 lane, review or candidate paths;
- no absolute lane path remains in shipped documentation, manifests or
  generated artifacts;
- no candidate-selection runtime code or comparative-build switch exists;
- `docs/PRODUCT_LAYOUT.md` agrees with D8 and the accepted plan;
- `evidence/v9-5-b2/MANIFEST.sha256` verifies; and
- `dev-docs/W0-REPORT.md` identifies the exact final bytes and contains no
  unexplained deviation.

The manager reruns or independently checks the digest, unit, gate,
regeneration, path-hygiene and evidence-manifest claims before acceptance.

## 8. Explicit non-goals

W0 does not:

- alter the frozen Garns grammar or language semantics;
- select a PostgreSQL driver;
- implement async APIs, PostgreSQL execution, live routing or capture;
- decide D4, D5 or D6b;
- freeze A1–A15;
- rewrite the SQLite engine or introduce an async facade;
- add a named identity provider or cryptographic authentication to Garns core;
  or
- begin any W1–W8 implementation package.

Any defect that requires one of those changes stops W0 and returns to the
manager for classification.

## 9. Handoff

The W0 builder returns:

- the canonical v9-6 root;
- `docs/PRODUCT_LAYOUT.md`;
- `dev-docs/W0-REPORT.md`;
- package metadata and Python matrix evidence;
- the stable v9-5 B2 evidence bundle and manifest;
- regenerated artifact hashes; and
- the complete command/execution record.

The manager either accepts that exact tuple as the W1 baseline or issues a
bounded W0 repair list. W1 is not authorized by a builder's completion claim
alone.
