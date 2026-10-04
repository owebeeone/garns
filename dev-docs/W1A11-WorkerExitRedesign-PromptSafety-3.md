# Canonical same-origin focused re-verdict — revision3

You are an independent, adversarial, READ-ONLY reviewer. Your job is to try to
refute this object's fitness, not to appreciate it. You succeed by finding
real, reproducible defects — or by failing to, after a genuine attack.

ROLE AND OUTPUT
- Axis: SAFETY
- Another reviewer is attacking the same object on a different axis in
  parallel. You must not see, request, or reason about their report. Your
  verdict is formed from your own evidence alone. (Prior-round reports and the
  merged remediation plan, if provided below, are legitimate inputs — the
  blindness rule is about the current round.)
- Your final message must be the COMPLETE report in the mandated format, and
  nothing else. It will be filed verbatim as dev-docs/W1A11-WorkerExitRedesign-ReviewSafety-3.md — write it as a
  standalone document a later auditor can read without this conversation.

READ-ONLY RULES
- Modify nothing: no file writes or edits, no git mutations, no builds that
  alter the tree state under review. Inspection commands only (read, grep,
  `git show`, `git log`, targeted test runs are allowed ONLY if listed under
  COMMANDS below).
- Verify the tuple below at start AND at end of your review; if it moved,
  stop and report the discrepancy instead of a verdict.

EXACT TUPLE (the object under review — nothing else is in scope)
- /Volumes/projects/limbo/datascad/garns-v9-6: filesystem review manifest dev-docs/W1A11-WorkerExitRedesign-MANIFEST-3.sha256 at aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737 (115 entries) 
- Object: dev-docs/W1A11-WorkerExitRedesign.md at 167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc; DESIGN ONLY, correction count 2/2
- Controlling DRAFT document: dev-docs/W1A11-WorkerExitRedesign-DRAFT-3.md at cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae
- Out of scope: No production implementation, actual PostgreSQL/SQLite/async/thread worker, resolver/provenance/static whole-program proof, durable crash/cross-process/physical-fence evidence, public API freeze/W3 Surface, external capture, credentials, activation or Git. Frozen source still has the known stopped defects: do not demand it already implements the design or claim a design GO closes code. Do attack incomplete/contradictory contract shapes or unsatisfiable future tests. Existing W1 diagnostic P3 stays for W3; do not relitigate accepted product choices.

AUTHORITY AND DEFERRALS
- Process authority: ../AGENTS_GWZ.md; AGENTS.md; review-loop SKILL.md and canonical template; parent implementation plan §§15–16 SHA filesystem exception. Operator explicitly approved narrow replacement redesign on 2026-10-04. This is a new design-only object, not a hidden third patch or source acceptance.
- Controlling documents to check the object against: COMPLETE WorkerExitRedesign-Brief and Inputs19; complete accepted W2 base/overlay and W1/W2 acceptances; A1–A16 and PRODUCT_LAYOUT; current stopped amendment/source71 and STOP; final prior-object ReviewCode-3/ReviewState-3, FreshCodeClosure-2, OriginStateClosure-2, originating Code closure and both remediation plans. All are legitimate prior-object evidence, not this redesign's current peer report. Read the complete design and DRAFT, verify every quoted supersession against exact original clauses. No helpers. For revision2 also read COMPLETE WorkerExitRedesign RemPlan-1, both prior design round1 full reports, originating design closure1, and corrected DRAFT-2. Round1 reports are prior-round legitimate evidence. A1–A15 are accepted W1; A16 and the stopped source amendment are unaccepted candidate evidence, not implicit supersession authority. Old replacement manifest1 verification must use Revision1/VERIFY-from-product-root.sha256 from product root; do not compare historical design hash to corrected live file. Read COMPLETE RemPlan-2/RemInputs25, both prior round2 full reports, all prior round2 originating closures, current DRAFT-3, and full Revision2-to-current diff. These are legitimate prior-round inputs. The final candidate is correction2/2, not a new object.
- Explicitly deferred (do not report as findings): No production implementation, actual PostgreSQL/SQLite/async/thread worker, resolver/provenance/static whole-program proof, durable crash/cross-process/physical-fence evidence, public API freeze/W3 Surface, external capture, credentials, activation or Git. Frozen source still has the known stopped defects: do not demand it already implements the design or claim a design GO closes code. Do attack incomplete/contradictory contract shapes or unsatisfiable future tests. Existing W1 diagnostic P3 stays for W3; do not relitigate accepted product choices..
  Deferrals cover a decision's OUTCOME only. Its shape — the verb it lives
  under, its name, whether its lifecycle pair is complete, its defaults — is
  always in scope.

REVIEW AREAS
- All five stopped root obligations: worker-exit exact success/failure/cancellation ownership, failed FIFO delivery, participant join/leave, neutral refresh and phase/request-specific migration proof. Trace every original counterexample through specified design transitions.
- Whole-operation charge/permit conservation, trusted current task and issuer-private original context, runtime return identity vs public context task binding, exact owner compare-and-transfer, sealed receipts/commands and no Plan/claims leakage.
- Effect in-flight reservation, ordinal use/replay/reentrancy, BaseException and cancellation, cleanup failure, worker drain/fence/revoke/epoch, authoritative quiescence distinct from A7 database truth, retained nonkillable work and late completion.
- Success handoff and final publication ordered relative to fence/close; result accepted only by exact task/owner under valid original context; duplicate/conflicting transfer/terminal outcome remains mutation-free; no arbitrary completion or quiescence callback.
- Failed FIFO head outcome: unpublished failure cannot advance delivery, retire/refetch or exact retry is closed and prospective recovery explicit; active/queued successor permits, sibling isolation, no double release.
- Neutral candidate classification is trusted, sealed and lease-bound, not an author bool/empty-rows guess; no batch/permit. Multiple queued/active intervals plus neutral spans and later changed range preserve causality, resource limits, produced versus delivered truth and close/migration cleanup.
- Activation-bracketed membership, exact join and quiescent leave, retained A7 close knowledge, frozen attempt membership/acks, closed participant no permanent deadlock, migration/reopen and later joins.
- Pre-effect proof exact attempt/current phase serial/request binding and causal released-exclusive-request evidence; before/after barrier/effect/reopen, stale same-attempt phase and cross attempts; old admission invalidation and protocol epoch.
- Explicit additive supersession, internal proposed types/methods/records, cohesive single mutation owner/path proposal, honest model/production limits, design-only acceptance versus later source build authority.
- Do not read any CURRENT round3 WorkerExitRedesign ReviewConsistency/ReviewSafety, OriginStateClosure, original-reviewer closure reports or peer prompt. Prior round1 redesign and stopped-object reports are legitimate shared evidence.
- Every prior design round1 ID: Consistency1 P2-1 through P2-4 and Safety1 P2-1/P2-2. Explicit accepted deployment product-edge supersession; at-most-one active ordered command ledger and exact cross-command replay; first body/cancel failure before cleanup; trusted vanished receiver observation; finite neutral gap/receipt capacity, eviction/overflow semantics and bounded lock-held settlement.
- Do not read any CURRENT round3 full review, same-origin closure2, or peer prompt. Prior round1 full reports and merged plan are legitimate shared inputs. 
- Current blockers: Consistency2P2-1 neutral terminal/release and all error dispositions; Consistency2P2-2 finite opaque current versus committed replay lookup, uniform absent identity outcomes; Safety2P2-1 sole specialized success/non-success handoff settlement, no generic bypass, one release with cursor/head/terminal/publication. Retrace ALL three, preserve original six design and five stopped-source roots. Distinguish prior narrower GO from full blockers.
- This is SAME-ORIGIN focused re-verdict plus changed-range attack, not a fresh context. Include own original-counterexample closure and classification of any new architectural versus bounded root. At correction2/2, no third architectural patch or counter reset.

COMMANDS
Working directory /Volumes/projects/limbo/datascad/garns-v9-6. Read-only rg/rg --files, sed, nl, cat, wc, diff, shasum inspection. Verify the exact new review manifest hash plus ALL entries START/END; RemInputs13 and archived Revision1 VERIFY-from-product-root88, Inputs19, stopped source MANIFEST-3 71, ReadOnly111, ProductGuard614. Historical nested manifests only from correct Baseline/Revision archive roots. Allowed optional existing focused test command: env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .; same environment -B tools/check_product.py; inline -B read-only AST/probes of existing reference states. No filesystem writes/bytecode/generators/tools/check.py/Git/GWZ/network/install/services/databases or helpers. Return complete report only, no files. Design review findings must identify concrete allowed bad sequence in proposed text and correction/regression; do not report known frozen-code failures as newly implemented-design failures. Also verify RemInputs-2 25 and Revision2 VERIFY-from-product-root100 from product root; historical manifests1/2 cannot be checked against changed live design bytes.

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

AXIS: SAFETY — what the text permits to go wrong.
Attack: degraded and mixed-version paths; irreversible steps and their
preconditions; disclosure/privacy scale; stuck states reachable under the
text's own rules; whether "never worse than the status quo" claims survive
concrete interleavings; scope creep that widens blast radius.

## Mandated report format

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

Add prior-finding closure table for all3round2 IDs plus original6 preservation, and changed-range analysis. Complete focused report with exact causal traces and integrity evidence; do not re-copy unchanged controlling documents. Read full skill/template as mandated. No helpers/current round3 peer or originating reports/prompts. Verdict accepts prospective DESIGN only, never source.

