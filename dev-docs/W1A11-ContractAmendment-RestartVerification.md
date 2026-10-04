# GARNs W1 A11 verification after session restart

Date: 2026-10-04. Status: manager execution evidence, not acceptance or finding
closure. Product root `/Volumes/projects/limbo/datascad/garns-v9-6` remains at
71-file MANIFEST-3 SHA-256
`23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.
No source file was edited during this verification.

## Reproduced checks

All current manifest entries verified, as did ReadOnly111, ProductGuard614,
RemInputs-2 16, Inputs9, Control3 and Baseline120. Both original canonical
review prompt hashes matched. Inline ast.parse checked all 25 contract/test
Python files. Inventory across src/tests/docs/grammar/corpus/tools/generated/
evidence/research matched 633 expected files, with zero missing or unexpected
paths. No .pyc or __pycache__ was present.

Using each of the four interpreters from the execution brief, all checks passed:

| Python | Focused contracts | Full suite | Product checks |
|---|---|---|---|
| 3.11 | 97 | 200 | 5 |
| 3.12 | 97 | 200 | 5 |
| 3.13 | 97 | 200 | 5 |
| 3.14 | 97 | 200 | 5 |

Commands were -B -m unittest discover -s tests/contracts -t ., -B -m unittest
discover -s tests -t ., and -B tools/check_product.py, with
PYTHONDONTWRITEBYTECODE=1 and PYTHONPATH=src plus cached Lark 1.3.1 at
`/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`.
All 12 commands exited zero. Existing unclosed SQLite connection ResourceWarnings
appeared in full runs on 3.13 and 3.14 and were not filtered. No generation,
dependency installation, database service, Git/GWZ mutation or compilation
that writes bytecode was run.

## Independently reproduced open closure defects

An inline Python 3.14 -B probe reused existing test fixture functions and drove
actual public reference transitions. Private registration fields were read
only to observe delivery accounting; no private state was overwritten.

For the FreshCodeClosure-2 counterexample: register, publish ranges (0,1] and
(1,2], dequeue the head, complete it REFUSED without publication, then dequeue
and publish the second. Output columns are label, global count, delivered
revision:

```text
handoff_before 2 0
handoff_refused 1 1
tail_published 0 2
```

The refused head falsely advanced deliveredThrough despite no outward handoff,
allowing the next range to cross the delivery gap. This corroborates the filed
reviewer's finding; passing FIFO success tests do not close the failure path.

For OriginStateClosure-2: begin drain, install the participant barrier, issue
a DRAINING proof, transition the same attempt to MIGRATING with generation 2,
then present the earlier proof. Output columns are label, state, generation,
admission epoch:

```text
phase_before migrating 1 1
stale_phase_accepted current 1 2
```

The pre-transition proof reopened the old binding after the migration phase
had changed. This corroborates the original State counterexample, not an
independent closure verdict or permission to patch.

Both full replacement reviewers remain peer-blind to this evidence and the
current closure reports. Their verdicts must be collected and merged first.
