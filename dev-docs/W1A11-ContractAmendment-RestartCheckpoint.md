# GARNs W1 A11 review restart checkpoint

Status: source frozen, final reviews complete, lane STOPPED pending operator
decision. Date: 2026-10-04. This record preserves the work boundary
for another session; it does not grant new implementation authority.

Both final full reports are filed. State classified worker-exit ownership as a
new architectural blocker after two corrections; the bounded-only exception
therefore cannot be used. [STOP](W1A11-ContractAmendment-STOP.md) pins all reports
and maps five distinct P2 roots. No source edit or replacement object is
authorized. Earlier notes below preserve the actual resumption chronology.

## Frozen package

Product root: `/Volumes/projects/limbo/datascad/garns-v9-6`.

- Complete 71-file MANIFEST-3 SHA-256:
  `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.
- Controlling amendment SHA-256:
  `f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f`.
- Complete DRAFT-3 testimony SHA-256:
  `3a6a1a342573b060b1c102318c7502fbcdeddd43438209c51c29899bfae95c2e`.
- Code prompt SHA-256:
  `2513eca98f453dd5fbaed2f2bd6e19809b81dea58600d165eac8d5b3ef4e8ad0`.
- State prompt SHA-256:
  `b3112bae56d1ebf58bf77de56de8ae7b0bd6e21a8b3d5c73c48f1dc48dc6bc8b`.

On resumption the manager verified all current manifest entries, 111 read-only
inputs, 614 product guard entries, 16 remediation inputs, nine original inputs,
three control entries and the 120-file baseline. No source edits were made.
The recorded pre-pause matrix remains 97 focused tests, 200 full tests and five
product checks on Python 3.11–3.14, with AST checks on 25 files. Those results
are evidence of tests passing, not closure of reviewer findings.

The manager subsequently reran all twelve matrix commands after restart and
reproduced both filed open counterexamples. Exact results and limits are in
[RestartVerification](W1A11-ContractAmendment-RestartVerification.md).

## Reports and missing contexts

OriginCodeClosure-2 is filed and reports GO on its original nine findings.
FreshCodeClosure-2 is filed and reports NO-GO: refusing or cancelling a handoff
can falsely advance deliveredThrough and permit later delivery across the gap.
OriginStateClosure-2 was received before pause and is now filed verbatim; it
reports NO-GO because a DRAINING proof can reopen the same attempt after it
enters MIGRATING. Both reviewers classified their residuals as bounded.

The unfinished full Code-3, full State-3 and FreshStateClosure-2 attempts had
no final verdicts. They were interrupted at the operator's pause; no verdict
may be inferred. Old collaboration contexts are unavailable after restart.
Fresh replacement Code and State agents read the complete original canonical
prompts and retrace prior cases. They must not read current closure reports,
this checkpoint or each other's current report. Original-context closure is
unavailable: any later focused correction review must explicitly record that
limitation and independently retrace the filed original counterexamples.

## Next action and hard boundary

Collect both full peer-blind reports on the frozen tuple and file them
verbatim. Merge all current findings before any patch. Two architecture
corrections have been used. A new architectural root stops this object for
an operator redesign-or-accept decision. The review-loop skill permits a
third round only if confined to reviewer-classified non-architectural fixes;
that requires a consolidated plan, exact archive/pin, regression gates and
independent re-verdicts. No implementer may self-close a finding.

The narrow authorization covers internal contract/reference tests and additive
ADR changes only. Production planner/lowering, PostgreSQL/async runtime,
activation, external capture, dependencies and Git/GWZ mutations remain outside
this step. Accepted W1 and composed W2 records and earlier stop histories stay
intact. Do not run tools/check.py, which writes generated evidence.

## Offline checks

Use PYTHONDONTWRITEBYTECODE=1 and -B. Cached Lark 1.3.1 is at
`/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`.
Python 3.14 is `/opt/homebrew/bin/python3.14`.
From the product root the permitted focused command is:

```sh
env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .
```

Use the same environment for tools/check_product.py. Do not use py_compile or
compileall. Historical 47-file and 59-file manifests verify inside Revision1
and Revision2 respectively; accepted historical nested manifests verify inside
Baseline, not against legitimately amended live source.
