# W1A11-WorkerExitRedesign — ORIGINATING CODE DESIGN CLOSURE 3

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`; operator-authorized correction 2/2 replacement-design candidate, not accepted and not implementation authority. Complete filesystem object: `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-3.sha256` at SHA-256 `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`, 115 files.  
**Baseline:** Approved no-Git filesystem-SHA exception. Revision 2 was read through its archived 100-entry product-root verification map. The stopped 71-file source remains immutable evidence at `W1A11-ContractAmendment-MANIFEST-3.sha256` SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.  
**Date:** 2026-10-04  
**Axis:** Originating Code retrace of `ReviewCode-3 P2-1` and `P2-2`: FIFO publication/settlement interfaces, failure ownership, exact permit and cursor causality, activation-bracketed participant membership and lifecycle symmetry. Independent, adversarial and read-only. Current round-3 peer/origin reports and prompts were not read; nothing here relies on another current reviewer.

**Verdict: GO — prospective design closure only.** The correction-2 design preserves prospective closure of both originating Code3 findings. Its rewritten FIFO grammar removes the prior success/non-success ordering ambiguity without reopening the original refused-head sequence, and the participant lifecycle remains intact. No new P0–P3 finding, architectural root or bounded root arose from the assigned retrace. Both source findings remain **OPEN** on the immutable stopped implementation.

---

## Prior-finding prospective closure table

| Originating finding | Prior prospective disposition | Final-tuple retrace | Status |
|---|---|---|---|
| `ReviewCode-3 P2-1` — refusal of an unpublished FIFO head advances delivery and exposes its successor | Registration retirement/refetch, unchanged delivered cursor and successor invalidation | Correction 2 now separates nonterminal publication readiness, one atomic successful publication/FIFO/terminal/release commit, and two-phase non-success retaining the active charge through worker-plus-iterator stop. Direct refusal, cleanup failure, fence, cancellation, close and migration cannot advance the old head or admit a successor. | **PROSPECTIVELY CLOSED; SOURCE OPEN** |
| `ReviewCode-3 P2-2` — constructor-time participant membership permits preactivation authority and lacks quiescent final leave | Activation-bracketed join and retained-obligation-bound final leave | Section 9 is byte-identical to Revision 2. The rewritten delivery path strengthens its retained-work premise: an active or retiring handoff remains charged and containment-owned until specialized settlement, so membership cannot leave prematurely; final idle leave still removes the runtime from later attempts. | **PROSPECTIVELY CLOSED; SOURCE OPEN** |

## Changed-range analysis

The reviewed baseline is archived Revision 2 at design SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`. The complete 652-line unified diff was inspected.

Correction 2 changes:

- §2’s supersession table to make publication barriers operation-kind-specific.
- §§4–7 so iterator delivery enters nonterminal `PUBLICATION_READY` and generic publication/completion refuses that operation kind.
- §8 from ambiguous post-terminal settlement to:
  - one specialized atomic successful publication/FIFO/terminal/release transition; and
  - two-phase failed-head retirement followed by exact worker-plus-iterator stop and specialized terminal release.
- §10 to restore atomic neutral refresh terminalization/release and bounded uniform unavailable lookup.
- §§12–14 finding maps, ownership assignments, regressions and correction-cap status.

Section 9’s participant lifecycle—Revision 2 lines 551–614 and final lines 644–707—is byte-identical under direct diff.

The §8 rewrite is within the selected single-lifetime-owner architecture and implements the bounded `Safety-2 P2-1` remedy. It does not add another owner, subsystem, public surface, compatibility rule or platform assumption. No new architectural or bounded root was found, so this originating review does not trigger the post-correction architecture STOP rule.

## 0. Evidence base

I read completely:

- `../AGENTS_GWZ.md` and product `AGENTS.md`.
- The complete review-loop skill and canonical reviewer template.
- The complete split-files skill named by the governing brief.
- The complete 1,121-line final candidate.
- `W1A11-WorkerExitRedesign-DRAFT-3.md`.
- `W1A11-WorkerExitRedesign-RemPlan-2.md`.
- Both legitimate full prior `ReviewConsistency-2` and `ReviewSafety-2` reports.
- My complete `W1A11-WorkerExitRedesign-OriginCodeClosure-2.md`.
- The complete Revision2-to-final unified diff.
- The exact accepted W2 publication, delivery, participant and migration clauses and the A6 buffering rules previously controlling this continuous originating review.
- The final and historical input/verification manifests.

I did not read any current round-3 peer or originating report or prompt, or current manager finding/checkpoint material.

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-3.sha256` matched `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`; 115/115 entries verified.
- `W1A11-WorkerExitRedesign-RemInputs-2.sha256` matched `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993`; 25/25 entries verified.
- Revision 2’s product-root verification map matched `4d1cbcc6626b6f41d6a0b04e08919d25177fed779f57338db79f36d05f88234c`; 100/100 entries verified.
- Revision 1’s product-root verification map matched `50550d3e44adeea13c63240d4a28cd96444f5543c83cd1c86cda7e9d53`; 88/88 entries verified.
- `W1A11-WorkerExitRedesign-RemInputs-1.sha256` matched `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`; 13/13 entries verified.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; 19/19 entries verified.
- The stopped source manifest matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; 71/71 entries verified.
- ReadOnly matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; 111/111 entries verified.
- ProductGuard matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; 614/614 entries verified.

The controlling files remained exact:

- design: `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`;
- DRAFT-3: `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae`;
- RemPlan-2: `6f6ef5e31e7e2c488804a684337ad6f49db3ef7915d93a8a21eb5d8f78a1876e`.

No tests were run: the task prohibits them, source is frozen, and this is prospective design closure. Inspection used only permitted reading, hashing, searching, line-numbering, counting and diff operations. No helper, file write, source/test/ADR edit, bytecode generation, Git/GWZ operation, network request, service, database or generator was used.

## 1. Findings

No P0–P3 prospective-design findings.

## 2. Invariant analysis

### `ReviewCode-3 P2-1`: successful iterator handoff

Correction 2 eliminates the split terminalization that the prior Safety review identified.

The legal successful trace is now:

```text
ACTIVE_HANDOFF
  -> PUBLICATION_READY(candidate)
  -> COMMITTED_SUCCESS(settlement receipt)
```

1. `PUBLICATION_READY` is explicitly nonterminal. Candidate creation publishes nothing, releases nothing and records no publication bit.
2. The candidate privately binds the exact value digest, FIFO head, handoff lease, registration, owner, binding/generation and receiving-task lifecycle serial.
3. Generic publication and generic containment completion detect the delivery operation kind and refuse mutation-free. They cannot create terminal success, release the permit or bypass FIFO settlement.
4. `settle_delivery_success` is the sole final publication barrier.
5. Before mutation, it validates:
   - the exact nonterminal candidate and handoff lease;
   - runtime-continuation ownership;
   - the trusted current receiving task and lifecycle serial;
   - current A11 context authority;
   - registration, binding and generation;
   - local and migration barriers;
   - closed-value digest; and
   - the current exact FIFO head.
6. One indivisible lifetime-owner commit then:
   - records publication and its exact settlement receipt;
   - removes the FIFO head;
   - advances `delivered_through`;
   - folds only the immediately following eligible neutral span;
   - records terminal `SUCCEEDED`;
   - removes active handoff ownership; and
   - releases ancestry and the one shared generation charge exactly once.
7. Only after that commit may the closed value be exposed. No callback or separately releasing completion occurs between commit and exposure.

The previous special-success ambiguity cannot recur:

- Settlement does not require an already-terminal success or prior publication bit.
- Generic completion cannot release first.
- Migration or close racing before the commit still observes the retained last permit and cannot cross.
- Commit-first leaves no unsettled head or cursor for migration to overtake.
- Exact replay reads the settlement tombstone without exposure, cursor movement, fold, terminal transition or release.
- A different candidate, value, head, lease, owner, task or generation refuses mutation-free.

There is no reachable design state with a released last permit and an unsettled published head.

### `ReviewCode-3 P2-1`: unpublished failure and refused-head conservation

The original stopped-source sequence was:

```text
enqueue A=(0,1]
enqueue B=(1,2]
dequeue A
complete A as REFUSED before publication
advance delivered cursor to 1
allow B to dequeue
```

The final design forbids every enabling transition.

#### Phase 1 — retirement begins

For refusal, authority expiry, local fence, cancellation, receiver loss, cleanup failure, close or migration before the success commit:

1. `begin_delivery_non_success` requires a registry-issued cause that has not already terminalized or released the handoff.
2. One mutation:
   - leaves `delivered_through` unchanged;
   - marks A failed;
   - changes the registration to `RETIRING_REFETCH`;
   - invalidates B and every queued successor;
   - releases each queued successor permit exactly once;
   - prevents new refresh, enqueue, dequeue and handoff operations;
   - revokes remaining worker/iterator authority;
   - transfers A to the preallocated containment owner; and
   - records `RETIRING_HANDOFF`.
3. This mutation explicitly does not terminalize or release A.

B therefore has no remaining valid permit or dequeue edge, while A remains charged and blocks close/migration quiescence.

#### Stop observation

Worker-command stop and iterator-frame stop are separate facts. Only the bound executor may issue `DeliveryStopObservation`, and only after both frames and all finite trusted cleanup cannot resume.

`observe_delivery_stopped` marks the retained handoff quiescent but still neither terminalizes nor releases it. Cleanup failure cannot produce an early release: it becomes the primary non-success cause if first, otherwise only a bounded diagnostic.

#### Phase 2 — final non-success settlement

Only after exact stop:

1. `settle_delivery_non_success` validates the exact lease and retirement receipt.
2. One mutation:
   - records terminal `REFUSED`;
   - removes retained active ownership;
   - releases ancestry and the one shared charge once;
   - records `RETIRED`; and
   - returns `RefetchRequired`.

It cannot claim `CANCELLED_CONFIRMED` for an active handoff and never accepts a previously releasing generic outcome.

Exact replay of either phase performs no second invalidation, terminalization or release. Conflicting success after retirement refuses mutation-free. Known later use of the retired registration returns `RefetchRequired`; no path converts the old failed head into success, advances it, or reinstates B.

Recovery also cannot hide the gap. A complete new A6 snapshot/high-water/registration publication establishes a new baseline under a new registration. It never resumes from the retired registration’s produced cursor.

The original observation—

```text
HANDOFF1_PUBLISHED 0
HANDOFF1_STATE refused
SECOND_DEQUEUE_STATE acquired
COUNT 1
```

—is therefore impossible under the final design: publication remains zero, delivery remains at the old frontier, B is invalidated, and the active count remains charged until exact stop and specialized final settlement.

### `ReviewCode-3 P2-2`: preactivation admission

Section 9 remains exact and unchanged:

1. Construction before activation creates only `UNJOINED`.
2. `UNJOINED` has no coordinator member, admitted handle or executable authority.
3. Pre-join admission refuses, so no preactivation handle exists to survive a later epoch transition.
4. `join_runtime` is atomic with the exact lifetime-capable open.
5. It validates `ACTIVE_UNUSED(epoch)` or `ACTIVE(epoch)`, binding, protocol epoch, runtime identity and local open resource.
6. First open performs the `ACTIVE_UNUSED -> ACTIVE` transition and membership issuance in the same transaction.
7. Every admission and lease binds the exact membership and join serial.

The originating sequence—

```text
construct while UNACTIVATED
register participant
mint admission
activate/first-open
reuse admission successfully
```

—has no legal membership or minting step.

Closing before activation is also complete: `close_unjoined` reaches `LEFT` without ever creating, removing or acknowledging coordinator membership, and later join refuses.

### `ReviewCode-3 P2-2`: quiescent final leave and future topology

The lifecycle remains:

```text
UNJOINED -> JOINED
UNJOINED -> LEFT
JOINED -> LEAVE_PENDING -> LEFT
JOINED -> LEFT
```

`request_leave` installs the local drain/fence and rejects new acquisition. `finalize_leave` removes membership from future topology only after `LOCAL_CLOSED` and zero:

- operation or generation permits;
- queued or active delivery;
- worker or containment records;
- registration-close work; and
- unresolved close obligations, including A7 identities.

The new delivery grammar strengthens this proof:

- Successful handoff settlement removes active ownership and releases the charge in its single publication commit.
- Failed handoff retirement keeps both active ownership and the shared charge through worker-plus-iterator stop and specialized final settlement.
- Generic completion cannot erase either state early.
- A participant therefore cannot satisfy final-leave preconditions while a delivery is active or retiring.

During a migration attempt, exact participant identities remain frozen. A leave request becomes `LEAVE_PENDING` and cannot alter that attempt’s obligations. Once cutover, no-effect reopen or recovery closes the attempt, a quiescent pending member may become `LEFT`. It is then absent from every later attempt.

The originating ghost-participant sequence cannot occur: a fully closed, obligation-free runtime reaches `LEFT` before a later attempt freezes topology. The inverse unsafe sequence—leaving while retained delivery exists—is also barred.

Copied, duplicate, stale-epoch, wrong-runtime and cross-coordinator membership tokens refuse without membership loss.

### Root classification

- `ReviewCode-3 P2-1` remains a bounded stopped-source/interface residual of correction1 F2. Correction 2 strengthens its prospective disposition and closes the later bounded publication/settlement ambiguity.
- `ReviewCode-3 P2-2` remains a bounded stopped-source contract omission already resolved by the chosen participant lifecycle.
- No new bounded root was found.
- No new architectural root was found; the two-round cap is not triggered by this originating retrace.

The design also continues to preserve one lifetime mutation owner, exact sealed private identities, separate produced/delivered cursors, one permit release, frozen attempt topology, no raw `Plan`, task-bound claim-free public context, parent-owned derived commands and the historical initial18/correction1 regression obligations.

## 3. Risks and next action

This GO is deliberately limited:

- It does not accept the redesign; the required full final-tuple peer verdicts remain separate.
- It does not close either finding on the immutable stopped source.
- It does not authorize implementation, source/test/ADR changes or deployment.
- It does not prove production async/thread cancellation, locks, database durability, crash recovery, physical/cross-process fencing, provenance or backend behavior.
- Internal names remain provisional pending W3 Surface review.

The single next action is to use this report as originating prospective closure evidence for `ReviewCode-3 P2-1` and `P2-2` on the exact 115-file tuple. If the complete design independently receives its required final GO/GO verdicts, any later implementation must be separately authorized, implement the specialized §8 success and non-success barriers plus unchanged §9 lifecycle, add the exact causal regressions above, and return a new frozen source tuple for executable originating closure.
