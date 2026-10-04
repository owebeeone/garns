# Worker exit implementation manager verification

Date: 2026-10-04. Owner: manager.
Status: verified candidate for handoff, not accepted source.

The builder declared STOP-WRITES before these checks. The operator requests
stopping at the first handoff, after verification and tuple freezing and before
any review launch. No reviewer was launched; all five stopped source roots
remain open pending executable closure. This record does not change the
accepted design or old two-correction histories.

## Reproduced test matrix

| CPython | Focused contracts | Full tests | Product checks |
|---|---:|---:|---:|
| 3.11.14 | 130 passed | 233 passed | 5 passed |
| 3.12.12 | 130 passed | 233 passed | 5 passed |
| 3.13.12 | 130 passed | 233 passed | 5 passed |
| 3.14.3 | 130 passed | 233 passed | 5 passed |

All 12 commands exited zero. Exact commands and captured complete outputs are
in [VerificationLogs-1](W1A11-WorkerExitImplementation-VerificationLogs-1.md).
Inherited SQLite ResourceWarnings remained visible in the 3.13 and 3.14 full
runs. No output was truncated by the command tool and no warning filter was
applied. No dependencies, services or network access were used.

The baseline was 97 focused and 200 full tests. The builder maps seven former
worker tests to six replacements, then adds 27 causal tests and seven
source-rule tests: 130 focused and 233 full. This arithmetic is reproduced;
the equivalence of the retained attacks remains a reviewer obligation, not
a manager closure claim. AST parsing separately passed all 27 Python contract
and contract-test files.

## Immutable guards and inventory

Every following content check exited zero, with exactly the stated OK count:

| Verification map | Entries passed |
|---|---:|
| Implementation Inputs | 31 |
| Implementation Baseline | 20 |
| Implementation ReadOnly | 741 |
| Legacy accepted worker-exit design | 115 |
| Legacy stopped source | 71 |
| Legacy old read-only set | 111 |
| Legacy old product set | 614 |
| Design AcceptanceEvidence | 13 |

Historical Legacy maps rebase only the archived mutable originals. The old
live manifests themselves remain unchanged and are not falsely checked
against new source. The current source receives its own separate manifest.

Hash comparison with the 20 archived originals finds exactly 15 changed
existing paths. The other five authorized existing files remain identical:
authority.py, consumers.py, lifetime.py, protocols.py and __init__.py.
The two new test files and the candidate implementation document are the
three authorized builder additions. The source/test inventory is exactly
64 files, matching the planned 62 plus two; no missing or extra path exists.
No .pyc, .pyo or __pycache__ artifact was found under source/tests.

The manager read the full candidate implementation record and checked its
test counts, declared limits and 1,780-line lifetime-owner size against actual
results/files. The size exception is documented under the split-files skill,
not a finding closure or a proof that fragmentation would be unsafe. Full
source call-graph/state review and design conformance are still pending.

## Frozen handoff limits

No Git/GWZ mutation, accepted-design edit, production runtime, planner/lowerer,
database backend, activation or external-capture work occurred. The builder
testimony is filed verbatim in DRAFT. Trusted fixture observations do not
establish physical stop, durable request release or database provenance.

The next manager must verify the separate MANIFEST-1 and all guards before
launching peer-blind full Code/State review plus originating executable closure.
No source writes are authorized while that review tuple is frozen.
Implementation correction count is zero. Any accepted-design change requires
operator direction regardless of that counter.
