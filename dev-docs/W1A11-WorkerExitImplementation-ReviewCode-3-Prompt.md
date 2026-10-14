You are an independent, adversarial, READ-ONLY reviewer. Your job is to try to
refute this object's fitness, not to appreciate it. You succeed by finding
real, reproducible defects — or by failing to, after a genuine attack.

ROLE AND OUTPUT
- Axis: Code
AXIS: CODE — architecture, interfaces, call graphs, and compatibility reality.
Attack: interface contracts vs. actual call sites; ownership and visibility;
API/wire compatibility with retained readers and older writers; error paths
and hidden panic/allocation paths; whether the diff does what its DRAFT doc
claims and nothing it forbids.
- Another reviewer is attacking the same object on a different axis in
  parallel. You must not see, request, or reason about their report. Your
  verdict is formed from your own evidence alone. (Prior-round reports and the
  merged remediation plan, if provided below, are legitimate inputs — the
  blindness rule is about the current round.)
- Your final message must be the COMPLETE report in the mandated format, and
  nothing else. It will be filed verbatim as dev-docs/W1A11-WorkerExitImplementation-ReviewCode-3.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- /Volumes/projects/limbo/garns-wz/garns: MANIFEST-3 SHA-256 9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9 (141 entries) — approved filesystem tuple; not a Git commit
- Object: the corrected worker-exit internal contracts/reference implementation after consolidated source correction 2 of 2, the last the implementation gate allows. Compare it with the round-2 object, whose exact 128 files are archived under dev-docs/W1A11-WorkerExitImplementation-Revision2/garns (MANIFEST-2 ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720), with the round-1 object archived under dev-docs/W1A11-WorkerExitImplementation-Revision1/garns (MANIFEST-1 7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544), and with the archived 20-file writable baseline
- Controlling DRAFT document: dev-docs/W1A11-WorkerExitImplementation-DRAFT-3.md at 62e2ec64f13b4aa9d9c878f097643ceb507e1dc8a66481aa102f559be13dede7 (correction 2), with DRAFT-2 at cf10c9f683c48cd23eb5cbf37c85fd6c276ff6108c3360c3f349d00ae63acd30 (correction 1); controlling dispositions dev-docs/W1A11-WorkerExitImplementation-RemPlan-2.md at ab617c0f96c5436652090179b9a19834a88934c16163300be9e9fe18ae0a678f and dev-docs/W1A11-WorkerExitImplementation-RemPlan.md at a2d625e1c695b231b3e264470cbd61dfef1ed628744ec25255e59d37e366b2a1
- Out of scope: manager handoff/checkpoint/prompt artifacts and future report outputs; accepted design and source guard sets are read-only controls, not source acceptance; the Revision1, Revision2 and Baseline archives are evidence copies, never live source

AUTHORITY AND DEFERRALS
- Process authority: complete review-loop skill plus canonical template, accepted program plan §§15–17 approved filesystem hashing, ExecutionBrief, AGENTS_GWZ.md and product AGENTS.md. Read fully before review. The operator directed this round to Claude reviewers; no helpers or writes.
- Controlling documents to check the object against: Read the complete accepted worker-exit design/acceptance and its composed W1/W2 inputs, all controls in dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256, the RemPlan and RemPlan-2, DRAFT-2 and DRAFT-3, BuilderPrompt-2 and BuilderPrompt-3, Verification-2/3 and VerificationLogs-2/3, the corrected implementation record and A16/index, plus PRODUCT_LAYOUT and the legitimate stopped-source/design reports named by Inputs. Preserve precedence over historical proposed headers. The four round-1 reports (ReviewCode-1, ReviewState-1, OriginCodeClosure-1, OriginStateClosure-1) and the six round-2 reports (ReviewCode-2, ReviewState-2, ReviewCode-1-Reverdict, ReviewState-1-Reverdict, OriginCodeClosure-1-Reverdict, OriginStateClosure-1-Reverdict) are prior-round inputs and may be read. Read only your own supplied prompt; do not read any current-round report (ReviewCode-3, ReviewState-3, ReviewCode-2-Reverdict, ReviewState-2-Reverdict or any *-Reverdict-2.md), peer prompt or message. Full reviewers independently retrace all former attacks; originating re-verdicts are narrower and cannot substitute for either full review.
- Explicitly deferred (do not report as findings): production async/thread/process runtime, locks/durability/crash/database provenance, actual planner/lowering/backend execution, external capture, PostgreSQL services, credentials/activation, dependency/Git operations, public W3 name freeze, RemPlan IR20 (tools/check.py G10 in read-only semantic.py, placed outside the corrections by the operator), and RemPlan-2 IR27 and IR28 (post-acceptance cancel return value; close/barrier/revocation scans over retained outer records), deferred to W3 by operator decision. These deferred outcomes do not excuse missing deterministic contract transitions or lifecycle shape. Every round-1 and round-2 finding and the five historical stopped roots remain open until executable closure on this tuple.
  Deferrals cover a decision's OUTCOME only. Its shape — the verb it lives
  under, its name, whether its lifecycle pair is complete, its defaults — is
  always in scope.

REVIEW AREAS
- Trace the complete accepted design §§2–13 through every current execution call site: admission, finite operation/command schedule, exact effect reservation/exit/stop/result acceptance, generic non-delivery publication and specialized delivery settlement. One mutable lifetime owner, no secondary authorization registry.
- Attack ordinary caller entry paths: no raw Plan/unwrap or arbitrary callback, no task/worker/claims/stop/containment-proof override; setup fixtures do not establish production provenance. Verify exact empty types/identity, copying/subclass/counterfeit/replay and detached pinned parameters.
- Trace successful and all non-success iterator handoff paths, source buffers and the sole final commit. Generic completion cannot publish/release an unsettled FIFO head. Two-phase retirement retains active worker+iterator work; registration refetch is a complete new baseline.
- Trace finite neutral state/lookup: Q/C/R/A bounds, no history side table, current candidates only charged operations, exact terminal/release and unchanged-owner/contained/refetch refusals. Fixed trusted classification, no guessed delivery progress.
- Trace participant construction/open/join/leave against activation and frozen attempt topology, and phase/serial/request/successor proof issuance/consumption through every migration edge.
- Corrections 1 and 2: verify each disposition IR1–IR19 (RemPlan) and IR21–IR26, IR29, IR30 (RemPlan-2) against the accepted design clause it cites, through actual call sites. Independently re-run the round-1 and round-2 counterexamples of every mapped finding (do not rely on the builder's tests or the manager's failing-before classification). Attack the mechanisms correction 2 changed — the join/admit/close ordering and its witness, the removed executor-façade member, the cleanup claim and reservation guard, terminal discard of the active serial and initial candidate, the expanded coordinator seam — for new bypasses, regressions of correction-1 behavior, and new stuck states. Check every interpretation and limit DRAFT-3 declares against the accepted design.
- Changed range: diff each changed path against its Revision2 copy (correction 2) and its Revision1 copy (both corrections). Confirm the changed set equals DRAFT-3's list and the brief's allowlist; check retained-test adaptations preserve coverage rather than weaken it; check the façade and coordinator seam changes against every call site and retained reader.
- Retain all initial18/F1-F10, expanded revocation and latest stopped/design roots; independently rerun counterexamples rather than trust prior closures. Verify regression/source-rule checks actually cover their claims and test production contract behavior.
- Names remain provisional; no public Surface freeze. Inspect internal shape/lifecycle/defaults despite outcome deferrals. The recorded atomic-state cohesion exception (lifetime_reference.py now 2,074 lines) permits justified cohesive growth, not a second owner or unrelated refactor.
- Classify every finding bounded source repair versus requiring accepted-design/architecture change, and label any NEW ARCHITECTURAL root cause explicitly. A required design change invokes STOP/operator direction; do not propose an automatic third architecture correction.

COMMANDS
Working directory: /Volumes/projects/limbo/garns-wz/garns. No network, installations, services, Git/GWZ mutations or file writes; do not spawn helpers.
Allowed inspection: pwd, rg/rg --files, sed, nl, wc, find, shasum, cmp, and diff against the Revision1, Revision2 and Baseline archives. Read files directly from this approved filesystem SHA-256 tuple, not Git HEAD.
START and END:
shasum -a 256 dev-docs/W1A11-WorkerExitImplementation-MANIFEST-3.sha256
Expected: 9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9.
shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-3.sha256
Expected 141 OK. Also individually verify content of these maps with shasum -a 256 -c:
dev-docs/W1A11-WorkerExitImplementation-Inputs.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline.sha256
dev-docs/W1A11-WorkerExitImplementation-ReadOnly.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-WorkerExitRedesign-MANIFEST-3.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-MANIFEST-3.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ReadOnly.sha256
dev-docs/W1A11-WorkerExitImplementation-Baseline/Legacy-W1A11-ContractAmendment-ProductGuard.sha256
dev-docs/W1A11-WorkerExitRedesign-AcceptanceEvidence.sha256
dev-docs/W1A11-WorkerExitImplementation-RemInputs.sha256
dev-docs/W1A11-WorkerExitImplementation-RemInputs-2.sha256
Expected counts in that order: 31, 20, 741, 115, 71, 111, 614, 13, 18, 22.
From inside dev-docs/W1A11-WorkerExitImplementation-Revision1/garns: shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-1.sha256 — expected 117 OK.
From inside dev-docs/W1A11-WorkerExitImplementation-Revision2/garns: shasum -a 256 -c dev-docs/W1A11-WorkerExitImplementation-MANIFEST-2.sha256 — expected 128 OK.
Do NOT check MANIFEST-1, MANIFEST-2 or historical live manifests against the corrected source; they verify only from inside their archives, and the explicit Legacy rebased maps preserve the older content checks. Confirm no .pyc/.pyo/__pycache__ artifacts. Any tuple movement stops the verdict.

Allowed deterministic read-only tests set PYTHONDONTWRITEBYTECODE=1 and PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:
/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11
/Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12
/opt/homebrew/bin/python3.13
/opt/homebrew/bin/python3.14
For any listed interpreter: -B -m unittest discover -s tests/contracts -t . (187); -B -m unittest discover -s tests -t . (290); -B tools/check_product.py (5).
Targeted unittest modules/methods and inline -B stdin Python attacks against the contract reference APIs are allowed with the same environment, provided no files are written and no private state is overwritten to fabricate proof. To compare with an earlier object, the same inline attacks may run with the working directory set to dev-docs/W1A11-WorkerExitImplementation-Revision2/garns (round 2) or dev-docs/W1A11-WorkerExitImplementation-Revision1/garns (round 1) and PYTHONPATH=src:<the same lark path>: each archive's own tests/__init__.py resolves its own src. Pure ast.parse/source inspection is allowed; no compileall/py_compile. Keep inherited SQLite ResourceWarnings visible. Do not run tools/check.py, which writes out-of-scope gate-report evidence.
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
Implementation correction count is 2 of 2: correction 2 produced this object and NO further consolidated source correction is available. If this round reports any new P0, P1 or P2, the lane stops and the operator decides between redesign and acceptance; do not propose a third correction. Any accepted-design/architecture/ownership/compatibility change requires STOP/operator direction. Label any NEW ARCHITECTURAL root cause explicitly. Classify each blocker accordingly. Historical stopped source/design two-round histories remain unchanged. No self-acceptance or physical backend proof.

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
{One row per root IR1–IR19 (RemPlan) and IR21–IR26, IR29, IR30 (RemPlan-2), plus one row per historical stopped root. "Re-run" means the original reproduction was executed or retraced on the new tuple by you — a claim of fixing is not closure.}

## Changed-range analysis
{What actually changed against the Revision2 archive (and, cumulatively, the Revision1 archive), whether any change falls outside the dispositions or the allowlist, and new-root-cause candidates — label NEW ARCHITECTURAL root causes as such.}

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
