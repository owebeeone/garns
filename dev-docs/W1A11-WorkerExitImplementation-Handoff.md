# Garns v9-6 worker exit implementation handoff

Date: 2026-10-04. Author: manager. Recipient: next manager agent.
Status: parked at the operator-requested first handoff, before review launch.

The builder has stopped writing. The manager has reproduced verification and
frozen the exact candidate source tuple. No reviewer was launched, no finding
was closed, and no source acceptance was granted. On operator resumption, the
next action is review of these bytes, not another build or query-planning work.

## Start here

Workspace: /Volumes/projects/limbo/datascad.
Product root: /Volumes/projects/limbo/datascad/garns-v9-6.

Read this document, ../AGENTS_GWZ.md, product AGENTS.md, the current
[checkpoint](CurrentProgramCheckpoint.md), the complete review-loop skill at
/Users/owebeeone/.claude/skills/review-loop/SKILL.md and its canonical template.
Read the [execution brief](W1A11-WorkerExitImplementation-ExecutionBrief.md)
and all controlling inputs before dispatch. The saved prompts identify the
complete review scope and allowed inspection commands.

Use apply_patch for edits and preserve unrelated changes. No Git/GWZ command,
network access, installation, service or workspace reconfiguration is
authorized. Do not edit managed AGENTS_GWZ.md or gwz.conf. The standing explicit
braced-control-flow and conditional-compilation scope rules still apply to new
or modified applicable code; this build modified Python only.

## Frozen candidate

| Artifact | SHA-256 |
|---|---|
| MANIFEST-1, 117 entries | 7e80ca67fc365e566c9bdefb580887a809c1441b35c14362d608ba5cc47ea544 |
| Builder DRAFT, filed verbatim | e8e2f73ec2667e898f294ecb7a0f549ab0c65df77de423c78a07e96222657ff2 |
| Candidate implementation record | 64626738a9507aa8bec64c6c3052b4299561bef530f6bebd4a1ff9d7a3fc3783 |
| Manager Verification-1 | 07145115ec29cf8d3ea3899ac31b23c442d64031c999463680eed38536505bca |
| Manager VerificationLogs-1 | abde89830461470f1f4a8a867f00c34f26a49746b20e049368d30c60a360b5e0 |
| Execution brief | aa75d255cf5d07b0f94a5311596150ea6d992e33bc9c354053c70080f666be44 |
| Implementation Inputs, 31 entries | 89ee484c8a4980972f0cc7e0cc0f12577a8f00dd5aba07c0eb8c7b83ab884cb5 |
| Archived writable baseline, 20 entries | d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a |
| Current read-only guard, 741 entries | 53d32f0522a5c0ff7434cfa97ac569fe064ac180f2ccb1294355588ea254d1da |

All artifacts above use the prefix W1A11-WorkerExitImplementation and reside in
dev-docs. The [manifest](W1A11-WorkerExitImplementation-MANIFEST-1.sha256)
pins all source/tests, ADRs, candidate records, verification and controlling
inputs. Its 117-entry contents are the source review object. Prompt files,
this handoff and the live checkpoint are separately pinned by
W1A11-WorkerExitImplementation-HandoffEvidence.sha256; they do not rewrite or
expand the frozen source tuple.

The accepted worker-exit design is SHA
167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc;
its acceptance is
884a0bfb8c5db660f8ee0f79b658a0c3eaf8c5c49e25ea3e2c04d4825d975d89.
That acceptance is DESIGN ONLY. The historical source amendment remains
stopped; its original source manifest is
23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424.
The new candidate is a separately authorized implementation object, not a
silent third correction to either older object.

## What the builder changed

The [candidate implementation record](W1A11-WorkerExitImplementation.md) contains
the full method/type inventory, supersession map, test mapping and limitations.
The [verbatim testimony](W1A11-WorkerExitImplementation-DRAFT.md) lists exact
changed paths and builder results.

Hash comparison confirms 15 changed existing files and three authorized new
files: two contract test modules and the implementation record. Five other
authorized existing files remain byte-identical. Source/tests contain exactly
64 paths, the prior 62 plus two. The 741-file immutable guard passes.

Implemented candidate transitions cover one mutable lifetime/worker owner,
finite command ledgers, exact worker exit and stop, receiver-loss containment,
atomic publication/delivery settlement, stop-gated failed delivery retirement,
activation-bracketed membership, bounded neutral lineage/replay and exact
migration-phase request proofs.

lifetime_reference.py is 1,780 lines. The split-files skill influenced the
documented decision to retain one cohesive mutable owner rather than add a
second state owner. This is an explicit size exception, not automatic evidence
of correctness. Review cohesion and source ownership; do not launch an
unrelated line-count refactor.

## Reproduced verification

| CPython | Focused contracts | Full tests | Product checks |
|---|---:|---:|---:|
| 3.11.14 | 130 passed | 233 passed | 5 passed |
| 3.12.12 | 130 passed | 233 passed | 5 passed |
| 3.13.12 | 130 passed | 233 passed | 5 passed |
| 3.14.3 | 130 passed | 233 passed | 5 passed |

These are manager-reproduced results, separate from the builder's testimony.
All 12 commands exited zero. Complete captured outputs are in
[VerificationLogs-1](W1A11-WorkerExitImplementation-VerificationLogs-1.md).
Inherited SQLite ResourceWarnings remained visible in the 3.13/3.14 full runs.
AST parsing passed 27 contract/contract-test files. No bytecode/cache artifact
was found. Tests are not reviewer closure or backend/concurrency evidence.

The test-count change is explicit: baseline 97 focused/200 full; seven former
worker tests became six replacements, producing 96/199; 27 causal and seven
source-rule tests bring the totals to 130/233. Reviewers must verify preservation
of the seven attack themes, initial18, correction1's13/F1–F10 and expanded
revocation attacks. Arithmetic and the builder's mapping alone do not establish
equivalent coverage.

Guard checks pass: Inputs31, baseline20, ReadOnly741, Legacy115/71/111/614 and
design AcceptanceEvidence13. Before review, verify MANIFEST-1 and all those
maps again. Use the Legacy maps inside the baseline directory to verify
historical content. They rebase only the archived mutable originals. Do not
run old live source/design manifests against new source or rewrite an old
manifest/report to imply acceptance.

## Review launch on resumption

The operator selected gpt-5.6-sol, high reasoning effort, for builders and
reviewers. No helpers or competing writers are authorized. Source writes stay
stopped while reviews inspect the tuple.

1. Verify HandoffEvidence, MANIFEST-1's exact hash and all 117 contents, then
   all guards listed in the saved prompts. Stop on any unexplained mismatch.
2. Launch two fresh independent full reviewers on the same tuple, one Code
   and one State. Use fresh contexts (fork_turns none), the saved canonical
   prompts verbatim, and separate current-round reports. Neither may read
   the other's or any current originating report.
3. Also obtain executable originating Code/State closure on this same tuple.
   Continue the original agents if accessible; otherwise disclose lost context
   and reconstruct their actual counterexamples with independent replacements.
   Originating closure never substitutes for either full review.
4. File every complete report verbatim, then merge all verdicts. Do not
   self-close a finding based on tests or a previous design-only GO.

Prepared prompts, not dispatched:

| Prompt | SHA-256 |
|---|---|
| ReviewCode-Prompt-1.md | 1dab3110e9fbda6a75a5ffebccf83e34205b9d7bd585b46c194d85ef81e3e017 |
| ReviewState-Prompt-1.md | a9ac786eb7156816942b239e23741be72dfa91ca320c1476e7ac6b962917c584 |
| OriginCodeClosure-Prompt-1.md | 30568d0cf5ecb18e74cb03f7e0e42bc9545c56f37f8825194763e1ad7d0c428e |
| OriginStateClosure-Prompt-1.md | 6410763a569af75da89fb8a5eed8200ef857002ef5adda4cf3310df8f58f81fa |

Every filename in this table has the W1A11-WorkerExitImplementation- prefix.
Full reviewers are fresh; original source-review agents were
/root/v96_w1a11_code_resume and /root/v96_w1a11_state_resume. Do not assume
these contexts survive the handoff. Builder /root/v96_workerexit_impl is done,
with testimony persisted; no active worker is needed to reconstruct this object.

The earlier OriginStateClosure-2 F8 reviewer context was already lost. The
saved State closure prompt explicitly identifies its replay as a fresh-review
replacement after material design change, not intact same-origin testimony.

## Open findings and correction rules

All five stopped roots remain OPEN until actual executable closure:

- Worker exit: State ReviewState-3 P2-1.
- Failed FIFO delivery: Code ReviewCode-3 P2-1, State ReviewState-3 P2-2 and
  FreshCodeClosure-2 P2-1.
- Participant lifecycle: Code ReviewCode-3 P2-2.
- Neutral refresh: State ReviewState-3 P2-3.
- Stale same-attempt phase proof: OriginStateClosure-2 State-Closure-P2-1.

Design-review finding mappings are in the candidate record and controlling
design. Review all accepted clauses, not only these five roots.

Implementation correction count is zero; at most two consolidated source
corrections are allowed. P0/P1/P2 blocks acceptance. Merge blockers into one
disposition plan and one patch, preserving original counterexample closure
and fresh full review after material interface/call-graph changes. Any remedy
requiring an accepted-design, architecture, ownership or compatibility change
requires STOP and operator direction regardless of that counter. The older
source/design two-round histories remain unchanged.

Source acceptance, if later granted, is internal contracts/reference tests
only. W3 Surface and final P12 remain future gates. Existing W1 P3 remains
assigned to W3 with originating closure.

## Product direction and scope limits

PostgreSQL is the primary future backend, SQLite a supported secondary backend,
and the future public database API async-only. Python support is 3.11 and above.
PostgreSQL support begins at 15, with 15–18 and later stable majors requiring
real verification before claims. Identity is an in-process provider-neutral
trusted seam; external cryptographic verification belongs outside core. There
is one convergent product tree.

Static query remains fetch-only; dynamic question remains closed-algebra,
footprinted and live. The ratified grammar and standalone unenforced flag are
unchanged. Governed writes only: external-write capture is deferred and does
not block this release.

No actual planner/lowerer, backend adapter, production async/thread/process
executor, lock, durability, crash recovery, database provenance or activation
has been implemented by this narrow build. Trusted fixture observations do not
prove physical stop or durable request release. Do not launch these downstream
packages from this handoff. First finish the frozen candidate's review gate.

## Suggested next operator instruction

“Resume from dev-docs/W1A11-WorkerExitImplementation-Handoff.md. Verify the
frozen tuple, then launch the saved peer-blind Code/State reviews and originating
executable closure. Do not rebuild or change accepted design.”

