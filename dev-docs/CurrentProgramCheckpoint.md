# Garns v9-6 current program checkpoint

**Status:** relocated byte-exact to garns-wz on 2026-10-04; parked at first handoff; worker-exit candidate built, verified and frozen; reviewers not launched; source acceptance pending  
**Date:** 2026-10-04  
**Owner:** manager

This is the current execution-state index. Historical reports remain unchanged;
exact acceptance records below control their respective tuples.

## Relocation — 2026-10-04

This product tree now lives at `/Volumes/projects/limbo/garns-wz/garns` (GWZ member
`mem_garns` of the garns-wz workspace), imported byte-exact at commit `a4ade29`. The
datascad copy is left untouched as the historical record. **Resume from
[GarnsV9-6-Relocation](GarnsV9-6-Relocation.md)**, then the handoff below. Launch
the reviews with the four `W1A11-WorkerExitImplementation-*-Prompt-2.md` files,
which differ from Prompt-1 only in the product-root path.
`W1A11-WorkerExitImplementation-RelocationEvidence.sha256` pins the relocation
record, the Prompt-2 files, MANIFEST-1, the handoff and this checkpoint; after this
edit, HandoffEvidence's entry for this checkpoint differs by design. The relocation
record also files a pre-existing finding for the reviewers: `tools/check.py` G10
fails on `src/garns/backends/contracts/semantic.py:98`.

## Current resume status

The operator requested stopping at the first clean handoff and saving a
standalone document. The builder is STOP-WRITES and complete. Manager reproduced
130 focused, 233 full and five product checks on Python3.11–3.14, AST27 and
Inputs31/baseline20/ReadOnly741/Legacy115/71/111/614/acceptance13. All pass;
inherited SQLite warnings remain visible. Exactly15 existing paths changed,
three authorized builder paths were added, and source/tests64 are exact.

[WorkerExitImplementation-Handoff](W1A11-WorkerExitImplementation-Handoff.md)
is the next manager's entry point. The complete117 MANIFEST1 is
`7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544`.
Verbatim DRAFT SHA
`e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2`.
Manager Verification1 SHA
`07145115ec29cf8d3ea3899ac31b23c442d64031c999463680eed38536505bca`.
Four canonical full/origin review prompts are saved but NOT dispatched.
No reviewer, correction or downstream build is running. All five stopped
source roots remain OPEN; tests are not acceptance or executable closure.
Implementation correction count zero; accepted-design changes require
STOP/operator direction. On operator resumption, verify the frozen tuple and
launch its independent full Code/State plus originating executable closure,
without source edits. HandoffEvidence separately pins the handoff, this
checkpoint, the source manifest and prompts.

### Historical implementation launch record

The operator's subsequent “go on next” explicitly authorizes the narrow
contract/reference implementation. One 5.6 Sol builder owns the exact 20
existing and three new paths in
[WorkerExitImplementation-ExecutionBrief](W1A11-WorkerExitImplementation-ExecutionBrief.md),
SHA `aa75d255cf5d07b0f94a5311596150ea6d992e33bc9c354053c70080f666be44`.
Inputs31 SHA `89ee484c8a4980972f0cc7e0cc0f12577a8f00dd5aba07c0eb8c7b83ab884cb5`;
baseline20 SHA `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a`;
readOnly741 SHA `53d32f0522a5c0ff7434cfa97ac569fe064ac180f2ccb1294355588ea254d1da`.
All initial guard sets pass. Manager reproduced 97 focused and 200 full tests
on Python3.14, retaining inherited SQLite warnings; those passing tests do not
close the five known stopped roots. Existing Python3.11–3.14 are available.

The 20 mutable originals are byte-identically archived. Explicit rebased
verification maps preserve historical design115/source71/readOnly111/product614
objects after authorized changes; do not check their original live manifests
against amended source. New source will receive its own frozen tuple.
Implementation correction count zero. Old source/design two-round histories
remain unchanged; accepted-design changes require STOP/operator direction.
Builder must stop writes before fresh full Code/State review and originating
executable closure. No implementation acceptance, planner/backend/production
runtime, activation, external capture or Git/GWZ work is launched.

### Prior design acceptance gate

The narrow worker-exit replacement design is now accepted, DESIGN ONLY, after
exactly two corrections. Final Consistency/Safety re-verdicts and all four
originating preservation/counterexample retraces are GO on the unchanged
115-entry tuple. The Code report's hash transcription error is preserved with
a separate same-reviewer evidence erratum; the verdict is unchanged.

[WorkerExitRedesign-ACCEPTANCE](W1A11-WorkerExitRedesign-ACCEPTANCE.md) controls
this decision at SHA
`884a0bfb8c5db660f8ee0f79b658a0c3eaf8c5c49e25ea3e2c04d4825d975d89`.
Design SHA `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`;
reviewed MANIFEST3 SHA
`aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`;
acceptance-evidence SHA
`882a3fec6ddecf7a7230a9e332e649be29020a326fe917b75ac523a691c84854`.
Manager final verification reproduces all final/archive/source guard sets and
the exact 62-file source/test inventory. No source, tests, ADRs or generated
evidence changed; no tests or Git/GWZ operations were run for this design gate.

All five stopped source roots remain OPEN, and the historical source STOP
remains intact. The next action is a separately authorized narrow
contract/reference execution brief and build, then executable regressions,
a new frozen source tuple and independent/originating Code/State closure.
No build, planner/lowering, backend, production async runtime or activation
work is launched by design acceptance. External-write capture stays deferred.

### Historical replacement-design drafting and review record

The operator explicitly approved the narrow worker-exit redesign on 2026-10-04.
[WorkerExitRedesign-Brief](W1A11-WorkerExitRedesign-Brief.md) authorizes one
5.6 Sol design owner, sole output W1A11-WorkerExitRedesign.md, followed by fresh
peer-blind Consistency/Safety review and originating worker-exit design closure.
The four bounded defects are included, not deferred away. New design object
correction count zero; old amendment STOP/two-round history remains intact.
All stopped source71 and guards remain frozen; no source implementation,
backend/runtime/planner/activation/Git work is launched. Acceptance will mean
design only; a later contract build requires its own authority and brief.
Earlier stop/resume statements below describe their historical gates.

The design owner has stopped writes. The replacement design is pinned at
`62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`,
with verbatim testimony in W1A11-WorkerExitRedesign-DRAFT.md. Its complete
88-entry MANIFEST-1 is
`79f38cc23f884efcfbca7906555296735b8f57756083b730d0c5dcfe6f2202dd`.
Fresh 5.6 Sol Consistency/Safety reviewers are running peer-blind on this exact
tuple; the originating State reviewer is separately retracing prospective
worker-exit closure. New design correction count remains zero. No GO or source
closure is inferred from drafting, guards or existing passing tests.

Both new full design reviews are filed: Consistency-1 NO-GO four P2s and
Safety-1 NO-GO two P2s; they independently converge on unbounded neutral
lineage/replay. Originating State prospective GO does not override them.
RemPlan-1 consolidates all six IDs into five roots, with no deferral or dispute.
The sole design owner is authorized for one consolidated correction; source
remains frozen. Material command/lifecycle/edge changes require fresh full dual
review plus same-origin closures after the replacement tuple is pinned.

Correction1 was interrupted by a quota limit before final stop-writing testimony.
The operator then explicitly requested continuation. Manager reproduced the
13-entry remediation inputs, original 88-entry archive verification, stopped
source71, ReadOnly111 and ProductGuard614, all passing. The same owner resumes
the partial 897-line design; no completed revision, review attempt, acceptance
or extra remediation round is inferred from this interruption.

The resumed owner has now stopped writes on correction1. Current design SHA
is `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`;
verbatim DRAFT-2 SHA is
`444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`.
Complete100 MANIFEST-2 is
`bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`.
Correction count1/2. Fresh full Consistency/Safety and separate same-origin
closure are being dispatched on the same frozen tuple; no acceptance yet.

Full revision2 verdicts are now filed: Consistency2 NO-GO two bounded P2s,
Safety2 NO-GO one bounded P2. All four narrower originating closures are GO,
but do not override the fresh blockers. RemPlan2 accepts all three IDs:
neutral terminal conservation, implementable evicted opaque identity lookup,
and single handoff publication/settlement release. Both full reviewers classify
these roots as bounded; no new architectural root. The same design owner may
perform one consolidated correction2/2, source untouched. No third patch or
architecture counter reset is authorized.

The design owner has stopped writes on correction2/2. Current design SHA:
`167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`;
DRAFT3 SHA `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae`;
complete115 MANIFEST3 SHA
`aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`.
Same full Consistency2/Safety2 reviewers receive peer-blind focused re-verdicts,
with original finding/source counterexample retracing at this same final tuple.
No design GO or source closure inferred from delivery. Two corrections used;
new architectural blockers require STOP/operator decision.

### Historical stopped-object review and restart record

Both final replacement reviews are now filed verbatim on unchanged71 MANIFEST-3:
Code NO-GO2P2; State NO-GO3P2. State P2-1 identifies a new architectural root
in worker result/failure ownership. Both architecture corrections are exhausted,
so the lane is STOPPED; see [the stop decision](W1A11-ContractAmendment-STOP.md).
The merged record retains five distinct P2 roots: worker exit, failed delivery,
participant lifecycle, neutral refresh and cross-phase proof freshness. Both
fresh full axes independently converge on failed delivery. No patch, successor
object, acceptance or downstream implementation is launched. Recommended next
action is an operator-authorized narrow worker-exit redesign carrying the four
bounded defects. Historical resumption notes below are not current acceptance.

The operator requested a session pause and then continuation. Source remains
frozen at the complete 71-file W1/A11 MANIFEST-3 SHA-256
`23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.
The final Code/State reviews and one focused State closure attempt were
interrupted without final reports or verdicts. Their collaboration contexts
did not survive restart. Replacement 5.6 Sol Code/State reviewers now use the
same hash-pinned canonical prompts, peer-blind, against the unchanged tuple;
this procedural retry is not a new correction round.

OriginCodeClosure-2 reports GO on its original findings. FreshCodeClosure-2
reports one bounded residual: failed handoff advances the delivery cursor.
OriginStateClosure-2 reports one bounded residual: a DRAINING no-effect proof
can survive transition into MIGRATING. Both remain open; no acceptance or
source correction is authorized by test success alone. The State closure
report received before the pause has now been filed verbatim.

Finish and file both full replacement reviews before merging current findings.
Both architecture corrections are exhausted. A new architectural blocker
requires STOP and operator redesign-or-accept. Only independently classified
non-architectural corrections may use the skill's bounded third-round exception.
No planner, database backend, async runtime, activation or Git work is launched.
See [the restart checkpoint](W1A11-ContractAmendment-RestartCheckpoint.md).

## Accepted through

- [Worker-exit replacement design](W1A11-WorkerExitRedesign-ACCEPTANCE.md):
  final115 tuple, Consistency/Safety GO/GO and all four originating retraces GO;
  design only. Exact additive supersessions compose with accepted W2; source
  amendment remains stopped/open and a new build requires separate authority.
- [Composed W2 design](W2-AdmissionLifetimeRedesign-ACCEPTANCE.md): exact
  stopped planning base plus accepted lifetime overlay; design only, not W1/A11
  amendment, backend/runtime implementation or activation authority.
- [W0 baseline](W0-ACCEPTANCE.md): repaired B2 promotion and renewed baseline
  verification, without a clean-commit or PostgreSQL claim.
- [Provider-neutral seam](GarnsV9-6-ProviderNeutralSeamAmendment-Acceptance.md):
  accepted historical plan/seam tuple.
- [Python, trust and delivery decisions](GarnsV9-6-OperatorDecisions-D6a-D7-D8.md):
  Python >=3.11, in-process trust and one convergent product.
- [Backend support decisions](GarnsV9-6-OperatorDecisions-D4-D6b.md): supported
  secondary SQLite, PostgreSQL 15–18 and subsequent stable majors with evidence.
- [Governed-write scope](GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md):
  GO/GO at the corrected exact tuple, one bounded remediation round used;
  migration effect-accounting P2 closed by its originating Safety reviewer.
- [W1 architecture](W1-ACCEPTANCE.md): A1–A15 and internal async contracts
  accepted at complete manifest SHA-256
  `95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`
  after final replacement Code/State GO/GO; no backend/runtime claim.

D1–D8 are closed for W1. External capture is deferred, not a passing feature
gate. Its [future project](GarnsExternalWriteCapture-ProjectBrief.md) is not
launched and does not block v9-6.

## Package ownership and next action

The sole 5.6 Sol builder has stopped writes. The current117 source tuple is
frozen at the operator-requested handoff. Existing20/new3 ownership, archived
baseline20 and ReadOnly741 remain controlling; no helper or competing writer
is authorized. The next manager must verify the handoff and tuple, then obtain
full peer-blind Code/State review and originating executable closure on operator
resumption. The 1,780-line atomic lifetime-owner cohesion exception is recorded,
not self-accepted. Historical source71/readOnly111/product614 verify through
rebased maps; no old manifest is rewritten. No downstream planner/backend/
runtime, activation or Git work is launched.

### Historical source-amendment execution record

The operator's latest “go” authorizes the narrow internal W1/A11 amendment in
[its execution brief](W1A11-ContractAmendment-ExecutionBrief.md), SHA-256
`1400d30c27e844a35ed1f59a75ec1bce5742e76fafb6df5fce41d984417e14c7`.
One 5.6 Sol builder owns only the exact contract, reference-test and additive
ADR allowlist. The manager freezes the complete current tuple before two
peer-blind 5.6 Sol Code/State reviews; all P0/P1/P2 findings block acceptance,
with at most two architecture correction rounds for this amendment object.
The 120-file immutable baseline archive preserves the accepted W1/W2 tuples;
old live source manifests become historical after authorized contract changes,
and are checked inside that archive, never rewritten to imply new acceptance.
No planner, SQL lowering, backend/runtime implementation, activation, public
API freeze, dependencies, Git landing or workspace reconfiguration is launched.
Carry existing W1 Code P3-1 into W3 with its originating closure requirement.
External capture remains deferred. Amendment acceptance is not yet granted.

The remediation1 builder has stopped writes. Current complete59 manifest2 is
`7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`;
current testimony and manager evidence are in DRAFT-2 and Verification-2.
Manager independently reproduced85 focused,188 full and5 product checks on
Python3.11–3.14, AST23, all guards and unchanged unowned inventory. Fresh
peer-blind5.6Sol Code/State reviews and separate original Code/State closure
checks are running against this same frozen tuple. No finding is self-closed,
no amendment acceptance or downstream launch is granted. Correction count1;
one further architecture correction remains. Initial history follows.

Fresh State review2 is filed verbatim: NO-GO, six P2s (four architectural,
one bounded successor check, one incomplete original publication-barrier fix).
ReviewCode2 and originating closure reports remain pending. Quota interrupted
three reviewers without verdicts; operator restored quota and requested
continuation. They resumed against unchanged manifest2, not a new review round.
No source writes or remediation2 have started; verdict merge comes first.

All four remediation1 reports are now filed, all NO-GO. Fresh Code3/State6
plus original Code3/State1 blocking IDs map into10 groups under RemPlan-2.
Accepted disposition: one final consolidated correction by the same builder,
architecture correction2 of2. Revision2 preserves exact59 files+manifest;
RemInputs-2 pins the review/control tuple. No finding is self-closed. After
this patch, fresh dual review and original closure are mandatory; a further
architectural blocker stops for operator redesign-or-accept. No production
planner/backend/runtime/activation scope or Git operation is authorized.

Final correction2 is builder-complete and source writes stopped. Complete71
MANIFEST-3 is23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424.
Full testimony DRAFT-3 and separate BuilderFinal-3 are filed verbatim.
Manager independently reproduced97focused/200full/5product on3.11–3.14,
AST25, all guards and zero unowned source additions/deletions. Fresh Code/State
review3 and focused closure by every originating reviewer now examine this
same frozen tuple. No acceptance or self-closure. Both architecture allowances
used; another architectural blocker triggers STOP for operator decision.

The initial amendment builder stopped writes. Verbatim testimony is filed in
`W1A11-ContractAmendment-DRAFT.md`; the complete 47-file current manifest has
SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`.
The approved additive ownership extension splits deployment coordination into
`generation_reference.py`. Manager verification independently reproduced
focused 76/76, full 179/179 and product 5/5 on Python 3.11–3.14; all immutable
guards verified and no unexpected product file additions/deletions appeared.
Initial peer-blind Code and State reports are filed verbatim and both NO-GO
(9 and 8 P2s). A same-tuple State supplement confirms the manager's revocation
counterexample under State P2-4 and adds one bounded rejected-owner-transfer P2.
All18 IDs map to13 root groups in `W1A11-ContractAmendment-RemPlan.md`, accepted
for one consolidated builder correction. Initial47 bytes are preserved under
Revision1. Architecture correction1 is authorized; at most one further remains.
Fresh full peer-blind Code/State review will be required after the new pin;
original closure checks remain mandatory. No amendment acceptance or downstream
planner/backend/runtime launch is granted.

The following chronology preserves the full review and stop history. Earlier
status statements describe their historical tuples, not current acceptance.

The architecture builder completed W1 under
[the execution brief](GarnsV9-6-W1-ExecutionBrief.md), SHA-256
`1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344`.
Exclusive writes are `docs/adr/**`, `src/garns/backends/contracts/**` and
`tests/contracts/**`. Manager records and reviews stay in `dev-docs/`.

The builder uses the operator-selected 5.6 Sol model. It is the sole owner of
shared contracts; no competing whole-product architecture is assigned.

`W1-MANIFEST.sha256` preserves the initial 22 owned files' review tuple
at SHA-256 `5e04e8ece03d3a98d0bef293b3140a74c86cf967ff63fedc2a19359973d05bed`.
Its complete report is filed in `W1-DRAFT.md`, SHA-256
`4680ff38273b1958a06b59cfa75b347ff209f88256c7aeefde436f902006d6f5`.
The manager reproduced 128/128 unit tests on Python 3.14 and all five product
checks, with the previously recorded inherited SQLite resource warnings.

At the initial draft stage W1 decisions were proposed, not accepted. Current
acceptance is additive and does not rewrite the reviewed source headers.
No W2 or backend/runtime implementation builder is launched. W6 is dormant.

## Review tiers and gate history

W1 receives independent peer-blind Code and State reviews after the builder
stops writing and the manager pins the complete scoped file manifest. All
P0/P1/P2 findings block acceptance; corrections use one consolidated patch per
round, with at most two architectural remediation rounds. Reports are filed
verbatim and originating reviewers verify closure.

Public API names are provisional. The W3 public API freeze must also receive
the separately required Surface review. Final P12 review remains mandatory.

Initial Code and State reviews both report NO-GO (six and seven P2 findings,
with cancellation and authority roots independently convergent). No finding
is closed yet. The same architecture owner is authorized to correct them under
`W1-RemPlan.md`, then stop writing for a new pin and fresh review because
shared interfaces change. Remediation round 1 is complete; at most two
architectural remediation rounds are allowed. No finding is independently
closed yet.

The corrected 26-file tuple is preserved in `W1-MANIFEST-2.sha256` at
SHA-256 `3dd854040ffbf58ad8992f57b755a3f8ebb790643ef8bf20e74ce4f7690a1eb6`.
The complete builder report is filed verbatim in `W1-DRAFT-2.md`. The builder
reports focused 26/26 and full 129/129 tests on Python 3.11–3.14; the manager
independently reproduced 129/129 on 3.14 without hiding inherited SQLite
ResourceWarnings. Fresh peer-blind Code and State reviewers receive this
exact tuple and the merged remediation plan. Source writes remain stopped.

Fresh round-2 Code and State reports are filed verbatim. Both independently
verified all original counterexamples closed, but W1 remains NO-GO: Code has
one new architectural P2; State has two architectural and two bounded P2s.
`W1-RemPlan-2.md` accepts all five for one consolidated final architecture
correction. No third architecture patch is authorized. Fresh round-3 review
will verify the revised tuple; any further architecture issue stops the lane
for operator redesign-or-accept.

Final correction is settled: `W1-MANIFEST-3.sha256` SHA-256
`3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13`,
26 owned files; builder testimony is verbatim in `W1-DRAFT-3.md`.
Builder reports focused 34/34 and full 137/137 on Python 3.11–3.14, plus five
product checks. Manager reproduced 34/34 focused tests before dispatch.
Final round-3 Code and State reports are both NO-GO and filed verbatim.
Both verify the round-2 fixes, but reopen two original incomplete closures:
Code-3 P2-1 exposes serializable claims from the supposedly opaque context
(architectural); State-3 P2-1 permits unresolved commit identity erasure during
worker close (bounded model correction). See `W1-STOP.md` for exact tuple,
remaining findings and recommendation. Two architecture rounds are exhausted.
Source writes remain stopped; no W1 acceptance, W2 or further repair is launched.

The operator subsequently approved the recommended narrow redesign and
re-review. `W1-RegistryContainmentRedesign-Brief.md` records that new authority:
identity-only caller handle with issuer-owned claims, plus outcome-bound worker
resolution. This is a replacement design object, not a silently continued
third W1 architecture patch; the preceding stop and two-round history remain.
Its exclusive six-file boundary and fresh Code/State gate are recorded in the
brief. No W1 acceptance or W2 launch is implied. Source changes are authorized
only within that redesign boundary.

The redesign builder has stopped writes. Its complete report is filed verbatim
in `W1-RegistryContainmentRedesign-DRAFT.md`. The complete 26-file integrated
manifest is `W1-RegistryContainmentRedesign-MANIFEST.sha256`, SHA-256
`fbd11e908f97938b23ad8870e86e703976e7859660b38058ac9188593d13eeff`.
Only the six authorized paths differ from the stopped tuple. The builder
reports 39/39 focused and 142/142 full tests on Python 3.11–3.14; no finding
is self-closed. Fresh Code/State initial review of the replacement object is
next, with its remediation count zero and prior W1 two-round history intact.

Initial replacement-object Code and State reports are both NO-GO, filed
verbatim. Both verify original stop fixes, but three current P2 findings remain:
duplicate/reused worker identities, malformed final knowledge, and absence of
a legal nonquiescent zero-identity close state. The manager independently
reproduced the malformed uncertain-outcome case. All findings are accepted in
`W1-RegistryContainmentRedesign-RemPlan.md` for one consolidated correction.
The State reviewer classifies close-state completion as architectural; this
is replacement-object remediation 1, with one further allowance remaining.

The owner completed the consolidated correction and stopped writes. Corrected
26-file manifest `W1-RegistryContainmentRedesign-MANIFEST-2.sha256` has SHA-256
`aec374e0e727ec604bfecd9c4c5e72777ccce6db7bf70f8c6d08efc21f329e66`;
full builder testimony is verbatim in `W1-RegistryContainmentRedesign-DRAFT-2.md`.
Only state, contract tests, A8 and ADR README changed. Manager independently
reproduced full 146/146 tests on each Python 3.11–3.14 without filtering the
inherited SQLite warnings, plus product and evidence checks. Tests are not
finding closure. Fresh peer-blind Code/State round-2 reviews are running
against this exact tuple; source writes remain stopped.

Fresh replacement round-2 reports are filed verbatim: Code GO (one nonblocking
P3 diagnostic follow-up); State NO-GO (one bounded, non-architectural P2: raw
strings/invalid values at cancellation/reconciliation helpers). Both verified
all three initial replacement findings and original stopped-W1 roots closed.
Originating Code and State reviewers separately filed verified closure of
their initial findings at this exact tuple. Architecture is still unaccepted.

`W1-RegistryContainmentRedesign-RemPlan-2.md` accepts the State P2 for a
single bounded entry-validation patch and records Code P3 for W3 integration.
Same owner, only state.py and tests; no new representation/interface/algebra.
Replacement-object remediation round 2 is underway; architecture root count
remains 1. Continue the same round-2 reviewers for focused re-verdicts after
pinning. No W2 launch, new architecture patch or Git landing is authorized.
The bounded correction is settled in full manifest3 SHA-256
`95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`;
complete builder report is `W1-RegistryContainmentRedesign-DRAFT-3.md`.
Only state.py and contract tests changed. Manager reproduced 148/148 full
tests on every Python 3.11–3.14 without warning filtering, plus all product
and inherited evidence checks. Same Code/State reviewers are independently
performing focused re-verdicts. Source writes stay stopped; acceptance pending.

Final focused Code and State replacement round-3 reports are GO on that exact
tuple, filed verbatim. State's latest P2 is independently closed by its
originating reviewer. All earlier blockers remain closed. Code's single P3
diagnostic remains explicitly deferred to W3; it does not block acceptance.
The manager accepted the complete integrated W1 object in `W1-ACCEPTANCE.md`.
Original W1 stop/two-round history is retained, not silently reset or accepted.

The design owner completed a 450-line draft and stopped writes. Design SHA-256
is `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`;
review manifest `W2-Design-MANIFEST.sha256` has SHA-256
`4014506528289e2d7d31c45ca433960271c8e5c3dd0e8486a7f53a183a425881`.
All 48 source/test/grammar files, 13 controls and 26 W1 files remain unchanged.
Complete testimony is filed verbatim in `W2-Design-DRAFT.md`; fresh peer-blind
Consistency/Safety reviewers receive generated canonical prompts and this
exact tuple. W2 design remediation count is zero. No source builder is active.

Initial W2 design reviews are filed verbatim: Consistency and Safety are both
NO-GO, with five P2 findings (one architectural, four bounded). The initial
design is preserved byte-identically in W2-QueryPlanningDesign-Initial.md.
W2-Design-RemPlan.md accepts every finding for one sole-owner consolidated
design correction; remediation count is 1. Source, W1 contracts and grammar
remain frozen. Fresh reviewers are required after the provenance change.

The sole owner completed remediation 1 and stopped writes. The revised design
SHA-256 is db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074;
nine-file W2-Design-MANIFEST-2.sha256 has SHA-256
4203848778247457db3041f3a25ad06abfa33d288ac0debac22ad2f71f320521.
All source/control/W1 entries are unchanged. Full testimony is filed verbatim
in W2-Design-DRAFT-2.md. The design explicitly identifies a required W1
result-shape amendment before full executable projection and an ownership
brief before runtime admission/legacy integration. Neither is authorized here.

Originating reviewers verified all five original cases closed at design level;
their complete reports are filed verbatim. Fresh full-design reviews are both
NO-GO: independent convergence on stripped admission proof at backend entries,
plus one bounded resource-witness contradiction. Their full reports are filed.
W2-Design-RemPlan-2.md accepts all findings for one final sole-owner correction.
The preceding design is preserved exactly in W2-QueryPlanningDesign-Revision2.md.
Remediation count is 2; no third architecture patch is authorized. W1 source,
source48, controls13 and grammar remain frozen; protocol/result amendments are
future prerequisites, not silently enacted changes.

The final design correction is settled, writes stopped: design SHA-256
0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e,
thirteen-file W2-Design-MANIFEST-3.sha256 SHA-256
5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36.
Complete owner testimony is verbatim in W2-Design-DRAFT-3.md. Source48,
controls13 and W1 26 entries remain byte-identical. The final draft requires
reviewed W1 structural-role and admitted-handle/verifier protocol amendments;
it does not enact them. All bare-plan consumers must fail closed during future
migration. Resource boundary evidence now distinguishes dominated ceilings.

Final full reports are filed verbatim: Consistency GO, Safety NO-GO. Both
originating round-2 reviewers verify their original blockers closed, but fresh
Safety identifies a new architecture P2: admission validity ends at verifier
resolution instead of spanning operation lifetime, leaving close/migration
revocation unfenced for already-resolved work. Focused GO does not supersede
this full-review NO-GO. All earlier cases are closed; one new blocker remains.

W2 design is STOPPED at the exact manifest3 above; see W2-Design-STOP.md.
Two architecture corrections are exhausted. No acceptance, third patch,
W1 amendment or implementation is launched. Source/control/W1/grammar bytes
remain unchanged. Manager recommends operator-authorized narrow replacement
design connecting admission leases to A3/A8/A12 draining and containment.

The operator has explicitly authorized the narrow replacement redesign.
W2-AdmissionLifetimeRedesign-Brief.md defines one additive design-only overlay,
sole writable drafter path W2-AdmissionLifetimeRedesign.md, fresh independent
Consistency/Safety review and originating final Safety closure. Stopped W2
bytes/history remain immutable. Replacement remediation count starts at zero
under this new operator directive, not by silently resetting the old object.
No source/W1/ADR/grammar/implementation/Git/service changes are authorized.

The sole owner completed the 578-line lifetime overlay and stopped writes.
Overlay SHA-256 is ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638;
four-entry W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256 has SHA-256
9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5.
Full owner testimony is filed verbatim. Manager independently verified all
4/11/13/48/13/26 recursive entries; source, W1 and stopped bytes are unchanged.
Fresh 5.6 Sol Consistency and Safety reviews and the originating final Safety
closure are running independently against this exact composed design tuple.

Initial replacement reviews are filed verbatim: both NO-GO. Originating final
Safety verifies the stopped lifetime case closed but also reports local/global
drain confusion. W2-AdmissionLifetimeRedesign-RemPlan-1.md accepts four merged
roots: worker authority handshake, local versus deployment drain, queued-buffer
migration ordering, and already-open legacy activation fencing. One sole-owner
consolidated design correction is running, replacement remediation count 1.
Initial overlay is preserved byte-identically; stopped/source/W1 inputs remain
unchanged. The old manifest1 is historical after its mutable overlay changes;
manager will pin the new current tuple before fresh independent full reviews
and originating closures. No source/contract/ADR changes are authorized.

Replacement remediation 1 is settled; sole owner stopped writes. Overlay
SHA-256 is 28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4;
nine-entry W2-AdmissionLifetimeRedesign-MANIFEST-2.sha256 has SHA-256
55271fb9926809c70d46b646ae307796df1ff08e4b6647ce7f081860aa353eea.
Owner testimony is verbatim in DRAFT-2. Manager read the full correction and
verified all 9/11/13/48/13/26 recursive entries. Two fresh 5.6 Sol full reviews
and three originating focused checks are running on that same exact tuple.
The correction names a future separately reviewed A11/W1 worker-authority
extension and deployment activation ownership; neither is enacted here.

Fresh full reviews on manifest2 are GO/GO; originating Consistency and stopped
Safety are GO. Originating replacement Safety closes its original cases but
reports a new architecture P2: ACTIVE -> ACTIVATION_RETIRED has no quiescence
or recovery contract. Its NO-GO blocks acceptance despite the other GO reports.
All five reports are filed verbatim. RemPlan-2 accepts the root and removes
unsupported activation retirement/decommissioning rather than expanding this
narrow design. Previous corrected overlay is preserved in Revision2.
The sole owner is applying replacement correction 2 of 2; no third architecture
correction is authorized. Existing stopped/source/W1/ADR/grammar inputs remain
frozen. Fresh same-tuple full reviews and originating closure follow pinning.

The final sole-owner correction is settled and writes stopped. Overlay
SHA-256 is 01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26;
eighteen-entry W2-AdmissionLifetimeRedesign-MANIFEST-3.sha256 has SHA-256
86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2.
Owner testimony is verbatim in DRAFT-3. Manager inspected the full changed
ranges and verified 18/11/13/48/13/26 entries. Fresh full 5.6 Sol reviews and
originating replacement/stopped Safety checks are running on that tuple.
Unsupported activation retirement is removed; the active epoch stays enforced
across lifecycle/generation changes. Replacement correction count is 2 of 2.

Final same-manifest full reviews are GO/GO. Originating replacement Safety
verifies the removed-retirement root closed, and originating stopped Safety
retains the original lifetime/local-close closures; both GO. All four complete
reports are filed verbatim. ReviewEvidence.sha256 pins the manifest and reports
at SHA-256 4f4931f516cdf117e2ab3a63176471f870c8a93f7acf706667be8d319ef20123.
Final manager checks pass 5/18/11/13/48/13/26 entries. No open design finding
remains. W2-AdmissionLifetimeRedesign-ACCEPTANCE.md accepts ONLY the exact
stopped base plus final overlay; historical STOP and reviewed bytes remain
unchanged. No executable, backend or production evidence is claimed.

Current next action: remain parked at the first handoff. On operator resumption,
read WorkerExitImplementation-Handoff, verify the frozen117 tuple and guards,
then launch saved independent and originating executable Code/State reviews.
The historical source amendment stays stopped/open; the new source candidate
is unaccepted, with zero implementation corrections used. No reviewers or
downstream planner/backend/runtime, activation or Git work are launched.
W3 Surface and final P12 remain gates.
Document and reference-model tests cannot establish PostgreSQL execution or
recovery evidence.
