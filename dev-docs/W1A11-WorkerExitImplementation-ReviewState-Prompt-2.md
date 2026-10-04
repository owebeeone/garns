You are an independent, adversarial, READ-ONLY reviewer. Your job is to try to
refute this object's fitness, not to appreciate it. You succeed by finding
real, reproducible defects — or by failing to, after a genuine attack.

ROLE AND OUTPUT
- Axis: State
AXIS: STATE — durable-state semantics and adversity.
Attack: state machines and restart legality; filesystem and durability
ordering; crash/kill points between every pair of writes; races and lock
scope; fail-closed direction (a defect may lose progress, never invent it);
recovery states as a closed grammar — hunt for new stuck states the current
semantics does not have.
- Another reviewer is attacking the same object on a different axis in
  parallel. You must not see, request, or reason about their report. Your
  verdict is formed from your own evidence alone. (Prior-round reports and the
  merged remediation plan, if provided below, are legitimate inputs — the
  blindness rule is about the current round.)
- Your final message must be the COMPLETE report in the mandated format, and
  nothing else. It will be filed verbatim as dev-docs/W1A11-WorkerExitImplementation-ReviewState-1.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- /Volumes/projects/limbo/garns-wz/garns: MANIFEST-1 SHA-256 7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544 (117 entries) — approved filesystem tuple; not a Git commit
- Object: candidate worker-exit internal contracts/reference implementation, compared with the archived 20-file baseline
- Controlling DRAFT document: dev-docs/W1A11-WorkerExitImplementation-DRAFT.md at e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2
- Out of scope: manager handoff/checkpoint/prompt artifacts and future report outputs; accepted design and source guard sets are read-only controls, not source acceptance

AUTHORITY AND DEFERRALS
- Process authority: complete review-loop skill plus canonical template, accepted program plan §§15–17 approved filesystem hashing, ExecutionBrief, AGENTS_GWZ.md and product AGENTS.md. Read fully before review. The operator uses gpt-5.6-sol high; no helpers or writes.
- Controlling documents to check the object against: Read the complete accepted worker-exit design/acceptance and its composed W1/W2 inputs, all controls in dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256, current DRAFT/candidate implementation record and A16/index, plus PRODUCT_LAYOUT and the legitimate stopped-source/design reports named by Inputs. Preserve precedence over historical proposed headers. Read only your own supplied prompt; do not read any current full/origin review report, peer prompt or message. Full reviewers independently retrace all former attacks; originating checks are narrower and cannot substitute for either full review.
- Explicitly deferred (do not report as findings): production async/thread/process runtime, locks/durability/crash/database provenance, actual planner/lowering/backend execution, external capture, PostgreSQL services, credentials/activation, dependency/Git operations and public W3 name freeze. These deferred outcomes do not excuse missing deterministic contract transitions or lifecycle shape. The five historical stopped roots remain open until executable closure..
  Deferrals cover a decision's OUTCOME only. Its shape — the verb it lives
  under, its name, whether its lifecycle pair is complete, its defaults — is
  always in scope.

REVIEW AREAS
- Enumerate complete worker command/lease product and migration state/phase product; reject missing/extra illegal edges. Effect reservation-before-invoke, exception-before-next-effect containment, cleanup primary ordering, exact executor quiescence, C1/C2 tombstone isolation and no caller impersonation.
- Exercise every accepted §7 causal pause with fixed trusted setup effects: queue/dequeue/reservation/invoke/return/cleanup/exit/stop/accept/publication. Test BaseException, reentrancy, cancellation losers/winners, receiver gone without resumption, expiry/fence/migration at each stage, late/replayed/conflicting outcome.
- Last-permit successful iterator settlement must commit publication/FIFO/cursor/terminal/release together before exposure. Generic terminalizer cannot bypass; failure retirement preserves delivered frontier and prevents successor, retains active charge through both worker and iterator stop, releases queued/active exactly once and requires complete refetch.
- Neutral progress has atomic candidate/cursor/span/ring/terminal/release with no batch, publication or buffer charge; produced cannot masquerade as delivered. Many neutral commits behind delayed changed heads/gaps, more than R evictions, current/cross/counterfeit identities, overflow/retirement and known quiescent/nonquiescent candidates must preserve finite C/R/A state and bounded work, no auxiliary history.
- Activation-bracketed membership: pre-open authority absent; join/leave exact and symmetric; every retained obligation including A7 prevents leave; frozen attempts immutable; idle closed runtime never becomes a permanent barrier. Two-participant migration/reopen/recovery races.
- Migration no-effect proofs current phase+serial+request+successor only; stale DRAINING proof during same-attempt MIGRATING_PRE_EFFECT refuses unchanged; effect entry permanently disables pre-effect reopen. Exact successor g+1, new admission epoch, old buffers never resurrect.
- Keep all historical18/F1-F10 and design-found adverse sequences executable. Count zero never conceals resumable work; close remains local; A7 UNKNOWN/commit retention is independent of worker stop and operation terminal state.
- Exact identity/replay/conflict refusal snapshots must check owners, effect sets, primary/result records, publication, resources/generation counts, lineage/membership/migration state. Test code must drive real transitions, not echo answers or overwrite private state to manufacture outcomes.
- Production locks, scheduling, durability/database/cross-process proof are deferred outcomes, not a license to omit deterministic transitions. Inspect complete changed source and source-rule evidence, actual documented limits and immutable guards.
- Classify findings bounded source repair versus requiring an accepted-design change. The latter triggers STOP/operator direction regardless of implementation round; no silently new architecture or counter reset.

COMMANDS
Working directory: /Volumes/projects/limbo/garns-wz/garns. No network, installations, services, Git/GWZ mutations or file writes; do not spawn helpers.
Allowed inspection: pwd, rg/rg --files, sed, nl, wc, find, shasum, cmp, and diff against the archived baseline. Read files directly from this approved filesystem SHA-256 tuple, not Git HEAD.
START and END:
shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256
Expected: 7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544.
shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256
Expected 117 OK. Also individually verify content of these maps with shasum -a 256 -c:
dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline.sha256
dev-docs/W1A11-WorkerExitImplementation-ReadOnly.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-WorkerExitRedesign-MANIFEST-3.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-MANIFEST-3.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ReadOnly.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ProductGuard.sha256
dev-docs/W1A11-WorkerExitRedesign-AcceptanceEvidence.sha256
Expected counts in that order: 31, 20, 741, 115, 71, 111, 614, 13.
Do NOT check historical live manifests against amended source; only the explicit Legacy rebased maps preserve those content checks. Confirm no .pyc/.pyo/__pycache__ artifacts. Any tuple movement stops the verdict.

Allowed deterministic read-only tests set PYTHONDONTWRITEBYTECODE=1 and PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:
/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11
/Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12
/opt/homebrew/bin/python3.13
/opt/homebrew/bin/python3.14
For any listed interpreter: -B -m unittest discover -s tests/contracts -t . (130); -B -m unittest discover -s tests -t . (233); -B tools/check_product.py (5).
Targeted unittest modules/methods and inline -B stdin Python attacks against the contract reference APIs are allowed with the same environment, provided no files are written and no private state is overwritten to fabricate proof. Pure ast.parse/source inspection is allowed; no compileall/py_compile. Keep inherited SQLite ResourceWarnings visible. Do not run tools/check.py, which writes out-of-scope gate-report evidence.
Record actual commands, outputs and causal unchanged-state/owner/count/publication/cursor facts; a passing suite or prior design-only GO is not closure.

SEVERITY AND VERDICT CONTRACT
- Findings use IDs P0-n / P1-n / P2-n / P3-n:
  P0 = active corruption, data loss, credential exposure, or false composition.
  P1 = likely destructive or unrecoverable release blocker.
  P2 = concrete correctness, recovery, compatibility, parity, or
       diagnosability defect.
  P3 = bounded robustness, coverage, maintainability, or documentation defect
       with a concrete consequence.
- Verdict is GO or NO-GO. NO-GO while any P0, P1, or P2 is open.
- Each finding: ONE root cause, exact location, violated invariant, credible
  reproduction or state/interleaving sequence, impact, required correction,
  and a closure/regression test. Separate independent root causes.
- Style preferences and speculative unease are not defects. Do not pad.
  Interface shape is not style: wrong command placement, a misleading name,
  a missing half of a lifecycle pair, or an option without a default is a
  finding (P2 or P3), on every axis.
- If your verdict is NO-GO but every blocking finding has a bounded,
  text-or-code-fixable remedy, you may pre-commit: "I pre-commit to GO on a
  revision that resolves {IDs} as specified." This makes the re-verdict cheap
  and is encouraged when honest.

IMPLEMENTATION GATE
Initial implementation correction count zero; at most two consolidated source corrections. Any accepted-design/architecture/ownership/compatibility change requires STOP/operator direction regardless of this counter. Do not silently spend source rounds redesigning. Classify each blocker accordingly. Historical stopped source/design two-round histories remain unchanged. No self-acceptance or physical backend proof.

MANDATED COMPLETE REPORT FORMAT

# {OBJECT} — {AXIS}-AXIS REVIEW

**Review object:** {object at exact SHA / doc path + status + date}
**Baseline:** {per-repo SHAs; note how sources were read, e.g. `git show HEAD:`}
**Date:** {date}
**Axis:** {one line: mandate}. Independent, adversarial, read-only. The other
axis runs in parallel; nothing here relies on it. Filed verbatim by the lane
owner.

**Verdict: {GO | NO-GO}** — {counts, e.g. "two P1 and three P2 findings
block"}. {If NO-GO and honest: pre-commit-to-GO clause naming the finding IDs.}

---

## 0. Evidence base
{What was actually read/run: files with line ranges, documents with sections,
commands with results. This section is what makes the verdict auditable.}

## 1. Findings
### [P1-1] {one-line root-cause title}
{Location · violated invariant · reproduction or state sequence · impact ·
remedy · closure test.}
{… one subsection per finding, severity-ordered. Omit section if none.}

## 2. Invariant analysis
{The invariants attacked and the evidence they held — attacks that FAILED are
part of the result; they are what a GO rests on.}

## 3. Risks and next action
{Residual risks below the finding bar; the single next action this verdict
implies.}

