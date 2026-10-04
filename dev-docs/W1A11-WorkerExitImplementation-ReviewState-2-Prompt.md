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
  nothing else. It will be filed verbatim as dev-docs/W1A11-WorkerExitImplementation-ReviewState-2.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- /Volumes/projects/limbo/garns-wz/garns: MANIFEST-2 SHA-256 ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720 (128 entries) — approved filesystem tuple; not a Git commit
- Object: the corrected worker-exit internal contracts/reference implementation after consolidated source correction 1 of 2. Compare it with the round-1 object, whose exact 117 files are archived under dev-docs/W1A11-WorkerExitImplementation-Revision1/garns (MANIFEST-1 7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544), and with the archived 20-file writable baseline
- Controlling DRAFT document: dev-docs/W1A11-WorkerExitImplementation-DRAFT-2.md at cf10c9f683c48cd23eb5cbf37c85fd6c276ff6108c3360c3f349d00ae63acd30; controlling disposition dev-docs/W1A11-WorkerExitImplementation-RemPlan.md at a2d625e1c695b231b3e264470cbd61dfef1ed628744ec25255e59d37e366b2a1
- Out of scope: manager handoff/checkpoint/prompt artifacts and future report outputs; accepted design and source guard sets are read-only controls, not source acceptance; the Revision1 and Baseline archives are evidence copies, never live source

AUTHORITY AND DEFERRALS
- Process authority: complete review-loop skill plus canonical template, accepted program plan §§15–17 approved filesystem hashing, ExecutionBrief, AGENTS_GWZ.md and product AGENTS.md. Read fully before review. The operator directed this round to Claude reviewers; no helpers or writes.
- Controlling documents to check the object against: Read the complete accepted worker-exit design/acceptance and its composed W1/W2 inputs, all controls in dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256, the RemPlan, DRAFT-2, BuilderPrompt-2, Verification-2 and VerificationLogs-2, the corrected implementation record and A16/index, plus PRODUCT_LAYOUT and the legitimate stopped-source/design reports named by Inputs. Preserve precedence over historical proposed headers. The four round-1 reports (ReviewCode-1, ReviewState-1, OriginCodeClosure-1, OriginStateClosure-1) are prior-round inputs and may be read. Read only your own supplied prompt; do not read any current-round report (ReviewCode-2, ReviewState-2 or any *-Reverdict.md), peer prompt or message. Full reviewers independently retrace all former attacks; originating re-verdicts are narrower and cannot substitute for either full review.
- Explicitly deferred (do not report as findings): production async/thread/process runtime, locks/durability/crash/database provenance, actual planner/lowering/backend execution, external capture, PostgreSQL services, credentials/activation, dependency/Git operations, public W3 name freeze, and RemPlan IR20 (tools/check.py G10 in read-only semantic.py, placed outside this correction by the operator). These deferred outcomes do not excuse missing deterministic contract transitions or lifecycle shape. Every round-1 finding and the five historical stopped roots remain open until executable closure.
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
- Correction 1: verify each RemPlan disposition IR1–IR19 against the accepted design clause it cites. Independently re-run the round-1 counterexamples of every mapped finding (do not rely on the builder's tests or the manager's failing-before classification). Hunt for new stuck states introduced by the correction's shared mechanisms: the single containment routine (terminal absorption, retiring preservation, lease+command+result atomicity, §8 phase-one entry), refresh disposition routing, registry-witnessed leave and membership binding, history discard and indexes (no replay or settlement that needs discarded state; no index that outlives or misses a live record). Check every interpretation DRAFT-2 declares in its limits against the accepted design.
- Keep all historical18/F1-F10 and design-found adverse sequences executable. Count zero never conceals resumable work; close remains local; A7 UNKNOWN/commit retention is independent of worker stop and operation terminal state.
- Exact identity/replay/conflict refusal snapshots must check owners, effect sets, primary/result records, publication, resources/generation counts, lineage/membership/migration state. Test code must drive real transitions, not echo answers or overwrite private state to manufacture outcomes; confirm retained-test adaptations preserve their attacks.
- Production locks, scheduling, durability/database/cross-process proof are deferred outcomes, not a license to omit deterministic transitions. Inspect complete changed source against its Revision1 copy and source-rule evidence, actual documented limits and immutable guards.
- Classify findings bounded source repair versus requiring an accepted-design change, and label any NEW ARCHITECTURAL root cause explicitly. The latter triggers STOP/operator direction regardless of implementation round; no silently new architecture or counter reset.

COMMANDS
Working directory: /Volumes/projects/limbo/garns-wz/garns. No network, installations, services, Git/GWZ mutations or file writes; do not spawn helpers.
Allowed inspection: pwd, rg/rg --files, sed, nl, wc, find, shasum, cmp, and diff against the Revision1 and Baseline archives. Read files directly from this approved filesystem SHA-256 tuple, not Git HEAD.
START and END:
shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256
Expected: ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720.
shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256
Expected 128 OK. Also individually verify content of these maps with shasum -a 256 -c:
dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline.sha256
dev-docs/W1A11-WorkerExitImplementation-ReadOnly.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-WorkerExitRedesign-MANIFEST-3.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-MANIFEST-3.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ReadOnly.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ProductGuard.sha256
dev-docs/W1A11-WorkerExitRedesign-AcceptanceEvidence.sha256
dev-docs/W1A11-WorkerExitImplementation-RemInputs.sha256
Expected counts in that order: 31, 20, 741, 115, 71, 111, 614, 13, 18.
From inside dev-docs/W1A11-WorkerExitImplementation-Revision1/garns: shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256 — expected 117 OK.
Do NOT check MANIFEST-1 or historical live manifests against the corrected source; MANIFEST-1 verifies only from inside its archive, and the explicit Legacy rebased maps preserve the older content checks. Confirm no .pyc/.pyo/__pycache__ artifacts. Any tuple movement stops the verdict.

Allowed deterministic read-only tests set PYTHONDONTWRITEBYTECODE=1 and PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:
/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11
/Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12
/opt/homebrew/bin/python3.13
/opt/homebrew/bin/python3.14
For any listed interpreter: -B -m unittest discover -s tests/contracts -t . (173); -B -m unittest discover -s tests -t . (276); -B tools/check_product.py (5).
Targeted unittest modules/methods and inline -B stdin Python attacks against the contract reference APIs are allowed with the same environment, provided no files are written and no private state is overwritten to fabricate proof. To compare with the round-1 object, the same inline attacks may run with the working directory set to dev-docs/W1A11-WorkerExitImplementation-Revision1/garns and PYTHONPATH=src:<the same lark path>: that archive's own tests/__init__.py resolves its own src. Pure ast.parse/source inspection is allowed; no compileall/py_compile. Keep inherited SQLite ResourceWarnings visible. Do not run tools/check.py, which writes out-of-scope gate-report evidence.
Record actual commands, outputs and causal unchanged-state/owner/count/publication/cursor facts; a passing suite or a builder's or manager's claim is not closure.

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
Implementation correction count is 1 of 2: correction 1 produced this object, and at most one more consolidated source correction remains. Any accepted-design/architecture/ownership/compatibility change requires STOP/operator direction regardless of this counter. A new architectural root cause found on this object counts toward the lane's cap; label it as such. Classify each blocker accordingly. Historical stopped source/design two-round histories remain unchanged. No self-acceptance or physical backend proof.

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

## Prior-finding retrace table
| Root (RemPlan) | Mapped round-1 IDs | Original counterexample re-run on this tuple | Status |
{One row per RemPlan root IR1–IR19, plus one row per historical stopped root. "Re-run" means the original reproduction was executed or retraced on the new tuple by you — a claim of fixing is not closure.}

## Changed-range analysis
{What actually changed against the Revision1 archive, whether any change falls outside the dispositions or the allowlist, and new-root-cause candidates — label NEW ARCHITECTURAL root causes as such.}

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
