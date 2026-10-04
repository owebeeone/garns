# W1A11-WorkerExitRedesign — ORIGINATING CODE DESIGN CLOSURE 2

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; operator-authorized correction 1/2 replacement-design candidate, not accepted and not implementation authority. Complete filesystem object: `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-2.sha256` at SHA-256 `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`, 100 files.  
**Baseline:** Approved no-Git filesystem-SHA exception. The stopped 71-file source candidate remains immutable evidence at `W1A11-ContractAmendment-MANIFEST-3.sha256` SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`. Revision 1 was read from its archived design and 88-entry rebased verification map.  
**Date:** 2026-10-04  
**Axis:** Originating Code review of `ReviewCode-3 P2-1` and `P2-2`: interface/state ownership, FIFO completion causality, activation-bracketed membership, lifecycle symmetry, exact failure paths and future implementability. Independent, adversarial and read-only. Current round-2 peer and originating reports/prompts were not read; nothing here relies on another current reviewer.

**Verdict: GO — prospective design closure only.** The current design supplies complete prospective dispositions for both originating Code3 findings, and retracing their exact counterexamples found no design-level allowed bad sequence. No new P0–P3 finding arose. Both findings remain **OPEN on the stopped source** until separately authorized implementation and executable originating re-verdict.

---

## Prior-finding prospective closure table

| Originating finding | Exact counterexample retraced | Prospective design status | Stopped-source status |
|---|---|---|---|
| `ReviewCode-3 P2-1` — refusal of an unpublished FIFO head advances delivery and exposes its successor | Queue `(0,1]` and `(1,2]`; acquire the first; refuse it with publication count zero; attempt to dequeue the second | **PROSPECTIVELY CLOSED** by §§8 and 10 | **OPEN** on MANIFEST-3 |
| `ReviewCode-3 P2-2` — constructor-time membership permits preactivation authority and lacks quiescent final leave | Construct before activation and attempt to reuse preactivation admission after first open; separately close one of two idle participants and begin a later drain | **PROSPECTIVELY CLOSED** by §9 | **OPEN** on MANIFEST-3 |

## Changed-range analysis

The current design is correction 1 of the archived Revision 1 design at SHA-256 `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`.

The correction adds or strengthens:

- explicit supersession of the accepted deployment-state edge set;
- a bounded multi-command operation ledger;
- committed pre-cleanup failure ordering;
- trusted receiving-task lifecycle observation;
- capacity-derived neutral-lineage and replay bounds;
- the complete correction-1 finding map and regressions.

The complete FIFO and participant-lifecycle sections—Revision 1 lines 378–506 and current lines 487–615—are byte-identical under direct `diff`. The correction therefore does not replace or weaken the two originating Code dispositions. Its bounded neutral-lineage additions strengthen the failed-head rule by making retirement discard all successor changed and neutral lineage within explicit bounds.

No source, test, ADR or accepted W2 document changed. This is a prospective design review, not source closure.

## 0. Evidence base

I read completely:

- `../AGENTS_GWZ.md` and product `AGENTS.md`.
- The complete review-loop skill and canonical reviewer template.
- The complete split-files skill, because the controlling brief explicitly requires cohesion review of the recorded atomic-registry exception.
- `W1A11-WorkerExitRedesign-Brief.md`.
- The 937-line current redesign and complete DRAFT-2.
- `W1A11-WorkerExitRedesign-RemPlan-1.md`.
- Both legitimate full round-1 design reports, `ReviewConsistency-1` and `ReviewSafety-1`.
- Legitimate `OriginStateClosure-1`.
- My complete originating `W1A11-ContractAmendment-ReviewCode-3.md`.
- The exact accepted W2 admission/lifetime publication, participant, migration and subscription clauses and A6 buffering requirements.
- The complete revision1-to-current design diff and exact unchanged FIFO/participant sections.
- Both current input manifests.

I did not read any current round-2 Consistency/Safety report or prompt, current Fresh/Origin closure report or prompt, or manager current-finding/checkpoint material.

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-2.sha256` matched `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`; 100/100 entries verified.
- `W1A11-WorkerExitRedesign-RemInputs-1.sha256` matched `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`; 13/13 entries verified.
- The Revision1 verification map matched `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`; 88/88 entries verified.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; 19/19 entries verified.
- The stopped source manifest matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; 71/71 entries verified.
- ReadOnly matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; 111/111 entries verified.
- ProductGuard matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; 614/614 entries verified.

The controlling files also remained exact:

- design: `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`;
- DRAFT-2: `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`;
- brief: `9ba4854b5ce14c86b22b76f1b1a42c05acef228723aa427999c7a5123b1f6a56`;
- RemPlan-1: `c094975dce11a2bf735dc91f847a20dca58a6823d47e24735f3af3ae809c46da`.

No tests were run: the task prohibits them, the source is deliberately frozen, and existing source execution cannot close a prospective design finding. Inspection used only permitted hashing, reading, searching, line-numbering, counting and diff commands. No file, source, test, ADR, manifest, bytecode, Git/GWZ state, network resource, service or generator was modified or invoked. No helper was used.

## 1. Findings

No P0–P3 prospective-design findings.

## 2. Invariant analysis

### `ReviewCode-3 P2-1`: unpublished FIFO-head failure

The stopped source allowed this sequence:

```text
enqueue A=(0,1]
enqueue B=(1,2]
dequeue A
complete A as REFUSED before publication
delivered_through becomes 1
dequeue B succeeds
```

That produced the originating observation:

```text
HANDOFF1_PUBLISHED 0
HANDOFF1_STATE refused
SECOND_DEQUEUE_STATE acquired
COUNT 1
```

The current design no longer permits that sequence.

1. The registration begins `ACTIVE`, with separate `produced_through` and `delivered_through` cursors and A as the exact active FIFO head.
2. Dequeue exchanges A’s buffer permit for its exact handoff operation permit. B remains a queued successor.
3. Refusal before caller-visible publication presents a registry-issued exact non-success outcome to `settle_delivery_non_success`; an ordinary caller cannot substitute a boolean or selected label.
4. In the same lifetime-registry mutation, §8 lines 514–524 require:
   - `delivered_through` remains unchanged;
   - A is marked failed;
   - the registration becomes `RETIRING_REFETCH`;
   - B and every queued successor are invalidated;
   - every successor permit is released exactly once;
   - new refresh, enqueue, dequeue and handoff operations refuse;
   - A’s active charge remains until exact worker/iterator quiescence;
   - final retirement returns typed `RefetchRequired`.
5. Consequently B has no legal dequeue edge. The original false progress mutation and successor crossing are both structurally unavailable.
6. Exact repeated failure settlement is idempotent. A later success after retirement is a conflict and cannot advance delivery.
7. Close and migration use the same retirement mutation and cannot release queued or active charges twice.
8. Resumption requires a complete new A6 snapshot/high-water/registration handshake. Only publication of that complete snapshot establishes the new registration’s produced and delivered baseline; the failed old lineage is never silently resumed.

The successful path is equally constrained. `settle_delivery_success` requires the exact publication receipt, terminal success, exact handoff lease/envelope/owner and current FIFO head. One lifetime mutation advances delivery, removes only that head, releases its permit and folds only the newly eligible neutral prefix.

Section 10 preserves the same ordering for neutral progress:

- a changed record folds only after exact caller-visible publication;
- its immediately following coalesced neutral span can fold only with that publication;
- folding stops at the next queued, active or failed changed record;
- failed-head retirement discards all successor spans and changed records without inventing delivery.

I attacked direct refusal, cancellation, authority expiry, local fencing, cleanup failure, duplicate failure, conflicting late success, close, migration and neutral-successor variants. None has a design edge that advances delivery or makes B eligible after unpublished A failure.

**Classification:** `ReviewCode-3 P2-1` remains a bounded source/interface residual of correction1 F2, not a new architectural root. The redesign selects one exact architecture—registration retirement/refetch—and prospectively closes it. The stopped implementation remains unsafe.

### `ReviewCode-3 P2-2`: preactivation membership and missing final leave

#### Preactivation authority trace

The stopped source allowed:

```text
construct registry while coordinator is UNACTIVATED
constructor registers participant
create admission handle
activate and first-open coordinator
use the preactivation handle successfully
```

The originating observation was:

```text
PREACTIVATION_PARTICIPANT_AND_HANDLE_SURVIVE active acquired 1
```

The current design forbids the first enabling step.

1. A registry constructed before activation exists only in `UNJOINED`.
2. `UNJOINED` has no coordinator member, admitted handle or executable authority.
3. Pre-join admission refuses; there is therefore no handle whose epoch can accidentally survive activation.
4. `join_runtime` occurs atomically with an exact lifetime-capable open.
5. It validates `ACTIVE_UNUSED(epoch)` or `ACTIVE(epoch)`, binding, protocol epoch, runtime identity and the local open resource.
6. First open performs `ACTIVE_UNUSED -> ACTIVE` and membership issuance in the same transaction.
7. Every later admission and lease binds the exact `ParticipantMembership` and join serial.

Activating the coordinator after registry construction does not retroactively validate anything created in `UNJOINED`, because the design permits no such admission record. The original handle-reuse sequence has no first valid authority and cannot be reconstructed by epoch coincidence.

Closing before activation is also closed: `close_unjoined` performs only `UNJOINED -> LEFT`, creates/removes/acknowledges no coordinator membership, and permanently refuses later join on that registry.

#### Closed-participant topology trace

The stopped source also allowed:

```text
two participants are registered
participant A reaches local CLOSED with no retained work
A remains registered forever
a later drain freezes {A,B}
B acknowledges
migration expires waiting for closed A
```

The originating observation was:

```text
CLOSED_PARTICIPANT_STILL_BLOCKS closed deadline_exceeded draining_old 0
```

The redesigned lifecycle closes that sequence:

1. `request_leave` installs the local drain/fence and rejects new acquisition.
2. `finalize_leave` may remove the exact membership only after `LOCAL_CLOSED` and after proving absence of every operation/generation permit, queued or active delivery, worker/containment record, registration-close item, unresolved close obligation and A7 identity.
3. A quiescent joined runtime therefore reaches `LEFT` and is absent from every future attempt.
4. Duplicate, copied, stale-epoch, wrong-runtime and cross-coordinator membership identities refuse without membership loss.
5. If a drain is already active, its participant set remains frozen. A leave request becomes `LEAVE_PENDING`; the member stays in that attempt’s exact required set and must install/acknowledge its barrier.
6. Only after successful cutover, no-effect reopen or recovery closes that attempt may a quiescent `LEAVE_PENDING` member become `LEFT`.
7. A subsequent drain freezes exactly the still-joined live identities; the earlier closed idle runtime cannot reappear as a permanent acknowledgement obligation.

This also blocks the inverse unsafe implementation: membership cannot disappear early merely because local close started. Retained permits, buffers, handoffs, workers, containment and A7 obligations prevent final leave, and an active attempt’s frozen topology cannot mutate.

I attacked join before activation, admission between activation and join, reuse of pre-join authority, close before activation, leave with every retained obligation, direct idle final leave, leave during drain, close during migration, post-migration leave, duplicate/copy/stale/cross tokens and a later drain after quiescent close. The design supplies a single ownership-preserving edge for each case and no path matching either originating failure.

**Classification:** `ReviewCode-3 P2-2` was a new but bounded contract/interface omission in the stopped object. The accepted architecture had already required open-time participation and quiescent retention; §9 completes the missing join/leave pair without introducing a new architectural root. The stopped implementation remains unsafe.

### Preserved surrounding invariants

The current design continues to require:

- one lifetime-registry mutation owner for lease, worker-exit, handoff, buffer and terminal count changes;
- exact sealed identities with private records rather than caller-supplied worker, task, claims, epoch, outcome or containment proof;
- caller-visible publication as the only changed-head delivery advancement;
- separate produced and delivered cursors;
- one release per queued or active permit;
- frozen migration-attempt topology;
- no raw `Plan`, independently authorized child permit or claims-bearing worker handle;
- preservation of initial18, correction1 13 and expanded-revocation regression obligations.

The split-files cohesion attack did not produce a finding. At 796 lines, the future lifetime reference is below the skill’s approximate 1,000-line review trigger, and the design gives a concrete reason for retaining it: the affected subledgers require one atomic mutation owner. It also names a legitimate revisit point—when a real transactional owner permits mechanically separated subledgers without creating cyclic or independent mutation authorities.

## 3. Risks and next action

This GO is deliberately narrow:

- It does not accept the replacement design; the required full independent design gate remains separate.
- It does not close either Code3 finding on the stopped source.
- It does not authorize implementation, source edits, tests, ADR edits or deployment.
- It does not prove real async/task/thread cancellation, database durability, crash recovery, physical fencing, cross-process coordination or backend behavior.
- The method names remain provisional pending W3 Surface review.

The single next action is to treat this report as originating prospective closure evidence for `ReviewCode-3 P2-1` and `P2-2` only. If the complete replacement design independently earns its required GO/GO gate, a separately authorized contract/reference build must implement §§8–9, add the exact causal regressions above, preserve the full historical regression set, and return the resulting source tuple for executable originating re-verdict.
