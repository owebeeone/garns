# W1/A11 contract amendment — manager verification

**Status:** tests independently reproduced; Code/State review pending  
**Date:** 2026-10-04

The builder stopped writes. Complete 47-file current tuple is pinned by
W1A11-ContractAmendment-MANIFEST.sha256, SHA-256
76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8.
Controlling additive amendment SHA-256 is
e5293ebeb777a31f07203bcba6860e5875fb0d1e643ea98f3a49efc92438db48;
verbatim builder testimony DRAFT SHA-256 is
544c8052f4accf45280a03a749d51c66ea999b2abf7b23ecd6a528695b916f24.

The manager independently ran focused discovery, full discovery and product
checks on each exact interpreter listed in the execution brief, with
PYTHONDONTWRITEBYTECODE=1, src plus cached Lark 1.3.1 on PYTHONPATH and -B.
No warning filters or network/dependency/service operations were used.

| Python | Focused contracts | Full tests | Product checks | Exit codes |
|---|---:|---:|---:|---|
| 3.11 | 76/76 | 179/179 | 5/5 | all zero |
| 3.12 | 76/76 | 179/179 | 5/5 | all zero |
| 3.13 | 76/76 | 179/179 | 5/5 | all zero |
| 3.14 | 76/76 | 179/179 | 5/5 | all zero |

Commands used -m unittest discover -s tests/contracts -t .,
-m unittest discover -s tests -t . and tools/check_product.py. The inherited
SQLite ResourceWarnings remained visible on 3.13/3.14. AST parsing passed all
20 contract/test Python modules; a syntax-aware import check found no contract
foundation imports of compiler/runtime implementations. No Rust/C source
changed, so broader conditional-boundary migration is not claimed.

Current manifest47, input9, control3, archived baseline120, unchanged-input111
and protected-product614 entries all verified after tests. Product inventory
comparison found no unexpected new files or missing files outside the allowlist.
The state.py archive diff is confined to OperationIdentity import and separate
CloseOutcome retained-read fields/validation; the deferred W1 P3 body is intact.
All original A1–A15 bytes remain pinned, with only additive ADR README indexing.

The builder reported one caught cache-hygiene incident: explicit py_compile
created nine bytecode files despite -B. It removed exactly those generated
files and their empty directory; final cache checks and immutable guards pass.
The manager's syntax check used ast.parse, not a bytecode-writing compiler.

Historical nested manifests remain verifiable inside the immutable archive;
the old live W1/source manifest is intentionally superseded, not rewritten.
The archived original 45 contract tests also independently pass on all four
interpreters. Inherited evidence files are unchanged under ProductGuard; the
live tools/check.py report was not regenerated because that writes outside
this package. No new G0–G11 or real-server/backend support claim is made.

Passing tests do not close reviewer findings. This package is internal
contracts and deterministic reference models only, not planner/lowering,
actual async workers/adapters, cross-process coordination, activation,
physical-fence proof, crash/restart behavior, public Surface freeze or release.
