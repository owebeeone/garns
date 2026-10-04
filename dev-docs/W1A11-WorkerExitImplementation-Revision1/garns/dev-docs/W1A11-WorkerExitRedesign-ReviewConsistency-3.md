# W1A11-WorkerExitRedesign — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`; operator-authorized correction 2/2 design candidate, not accepted and not implementation authority; 2026-10-04.  
**Baseline:** Approved no-Git filesystem-SHA exception, read directly from `/Volumes/projects/limbo/datascad/garns-v9-6`; 115-entry `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-3.sha256` at SHA-256 `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`. Comparison baseline was archived Revision 2 design SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`, verified through its 100-entry product-root map. The stopped 71-file source remains immutable, unaccepted evidence.  
**Date:** 2026-10-04  
**Axis:** Consistency — same-origin focused re-verdict on the three round-2 blockers, changed-range attack, internal coherence, controlling-contract agreement, exact supersession and satisfiable future evidence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — all three round-2 blockers are prospectively closed, all six round-1 design dispositions remain preserved, and the correction-2 changed range introduces no P0–P3 finding or new architectural root. This accepts no source and grants no implementation authority.

---

## Prior-finding closure table

| ID | Disposition claimed | Original counterexample retraced on correction 2 | Status |
|---|---|---|---|
| `Consistency-2 P2-1` | Make neutral candidate consumption, cursor/span/replay mutation, terminal refresh success and the one ancestry/generation release one atomic transition; give every known-candidate refusal/refetch route an explicit owner/terminal disposition. | One charged neutral refresh now commits cursor, lineage and replay together with terminal `SUCCEEDED` and one release, producing no batch, buffer permit or publication. Exact candidate/receipt replay reads the retained terminal facts without release. A presentation-only mismatch retains the live owner and charge; an unusable quiescent candidate terminalizes/releases before `RefetchRequired`; a nonquiescent candidate transfers to containment and retains its charge until exact stop and specialized settlement. Overflow, retirement, close and migration use those same dispositions. | **CLOSED PROSPECTIVELY** |
| `Consistency-2 P2-2` | Distinguish only bounded current issued candidates from bounded committed replay; make every opaque identity absent from those records return one uniform typed unavailable outcome. | Candidate lookup examines only the target registration’s one current candidate field per charged refresh operation and its `R == C` replay ring. Receipt lookup examines only that ring. After more than `R` commits, evicted candidate/receipt identities, cross-registration identities, retired-registration identities and counterfeits all return `RefreshRecordUnavailable` without reconstructing cursor, registration or provenance. Current and in-window identities retain their exact distinct behavior. No history side table is permitted. | **CLOSED PROSPECTIVELY** |
| `Safety-2 P2-1` | Make specialized handoff settlement the sole final delivery publication barrier; unify publication, FIFO settlement, terminal success and one release; use specialized two-phase non-success settlement with no generic bypass. | From nonterminal `PUBLICATION_READY`, `settle_delivery_success` atomically records publication, removes/folds the FIFO head, advances delivery, records terminal `SUCCEEDED`, removes active ownership and releases once before exposure. Generic success/containment completion refuses for delivery operations. Every precommit non-success first retires the registration and invalidates queued successors without releasing the active handoff; only exact worker-plus-iterator stop permits specialized terminal `REFUSED` settlement and the one active release. | **CLOSED PROSPECTIVELY** |
| `Consistency-1 P2-1` | Explicitly supersede the accepted deployment-edge grammar and define the deployment-state × attempt-phase product. | §§2 and 11 remain unchanged in substance. A DRAINING proof becomes stale on entry to `MIGRATING_PRE_EFFECT`; only a newly issued exact phase/request/successor proof can take the pre-effect return edge, and no such edge exists after `EFFECT_BEGUN`. | **PRESERVED CLOSED PROSPECTIVELY** |
| `Consistency-1 P2-2` | Replace singular command fields with a finite operation-owned ledger, unique command serials, one active record and retained tombstones under one outer permit. | C1→C2 remains exact: C2 cannot dispatch before C1 acceptance, receives distinct command/worker/authorization/ordinal state without a new permit, and cannot be affected by C1 replay or conflicting C1 outcomes. One outer terminal route releases once. Delivery specialization narrows, rather than bypasses, that final route. | **PRESERVED CLOSED PROSPECTIVELY** |
| `Consistency-1 P2-3` | Commit body failure before cleanup; make cleanup-only failure primary and later cleanup failures bounded diagnostics. | §5.3 still commits body/effect/cancellation primary ownership before competing cleanup, preserves the first primary receipt and containment transfer, and bounds cleanup/race diagnostics by the finite cleanup schedule. Delivery non-success explicitly retains this ordering through iterator cleanup and stop. | **PRESERVED CLOSED PROSPECTIVELY** |
| `Consistency-1 P2-4` | Bound/coalesce neutral lineage and replay with deterministic eviction and bounded settlement work. | `Q`, `C == Q + 1`, `R == C`, at most `C` spans, `2C` lineage records and `C` replay records remain. Correction 2 removes the impossible history-sensitive post-eviction result while preserving deterministic bounded lookup and constant-work current-candidate disposition. | **PRESERVED CLOSED PROSPECTIVELY** |
| `Safety-1 P2-1` | Add trusted exact receiver-lifecycle observation and fail-closed transitions for every prepublication state. | Task loss still invalidates the exact original binding and removes or contains queued, running, pending-success, quiescent-success and accepted-before-publication work. Delivery `PUBLICATION_READY` now routes explicitly through specialized retirement and quiescent settlement, so receiver loss cannot reach generic early release. | **PRESERVED CLOSED PROSPECTIVELY** |
| `Safety-1 P2-2` | Bound neutral spans/receipts, eviction behavior and cleanup work. | Arbitrarily many neutral commits behind a delayed changed head still coalesce into one span per gap while replay remains `R == C`. Evicted handles now receive the implementable uniform unavailable result; retirement remains bounded and releases only real permits. | **PRESERVED CLOSED PROSPECTIVELY** |

## Changed-range analysis

The complete Revision-2-to-current diff grows the design from 937 to 1,121 lines. Its behavioral changes are confined to the three accepted correction-2 dispositions and their necessary tests, finding maps and future ownership descriptions:

- §§2–8 add an operation-kind distinction, delivery publication/settlement identities, a nonterminal `PUBLICATION_READY` state, the sole specialized successful delivery barrier and specialized two-phase non-success settlement. Generic terminalization explicitly rejects delivery operations.
- §10 accounts current issued candidates inside existing charged refresh-operation records, defines `A <= L_refresh`, replaces history-sensitive evicted lookup with uniform `RefreshRecordUnavailable`, restores atomic neutral terminal/release semantics and specifies every known current-candidate error disposition.
- §§7, 12–14 add the required causal schedules, correction-2 mapping, future cohesive ownership and correction-cap language.

These are **bounded contract corrections within the selected architecture**, not new architectural roots. They retain the same sole lifetime-registry mutation owner, existing operation ledger, generation ownership domain, compatibility model, public-surface deferral and platform assumptions. `DeliveryStopObservation` completes the prescribed handoff settlement grammar without creating an independent state owner; current refresh-candidate storage is attached to an already charged operation rather than a new history subsystem.

No changed range falls outside the consolidated RemPlan-2 dispositions except status, evidence and review-gate text. The earlier architectural correction ranges—migration product, finite command ledger and trusted receiver lifecycle—remain intact. No correction-2 change reopens any of the six round-1 findings or the five stopped roots. No new bounded root was found either. The two-correction cap is therefore not triggered: there is no third patch to request and no redesign STOP condition.

## 0. Evidence base

At both START and END:

| Evidence | Exact SHA-256 | Verification |
|---|---|---:|
| Consistency prompt | `d88c6f341ea29a159f8e78a638af9077e09132d26eadb4150653fbcd47af8cf9` | exact |
| MANIFEST-3 | `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737` | 115/115 |
| Design | `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc` | exact, 1,121 lines |
| DRAFT-3 | `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae` | exact |
| RemInputs-2 | `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993` | 25/25 |
| Revision-2 product-root map | `4d1cbcc6626b6f41d6a0b04e08919d25177fed779f57338db79f36d05f88234c` | 100/100 |
| RemInputs-1 | `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c` | 13/13 |
| Revision-1 product-root map | `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8` | 88/88 |
| Original Inputs | `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52` | 19/19 |
| Stopped source MANIFEST-3 | `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424` | 71/71 |
| ReadOnly | `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d` | 111/111 |
| ProductGuard | `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818` | 614/614 |

I read completely:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, the review-loop skill and canonical reviewer template;
- the complete 1,121-line candidate, DRAFT-3, RemPlan-2, RemInputs-2 and complete Revision-2-to-current unified diff;
- both complete round-2 full reports and all four prior round-2 originating closure reports;
- both complete round-1 design reports, RemPlan-1, originating design closure material and archived Revision-1/Revision-2 designs;
- the complete brief, accepted W2 base/overlay and W1/W2 acceptances, ADRs A1–A16 and `PRODUCT_LAYOUT.md`;
- the stopped amendment/source evidence, STOP and execution records, both stopped remediation plans, final `ReviewCode-3`/`ReviewState-3`, `FreshCodeClosure-2`, `OriginCodeClosure-2` and `OriginStateClosure-2`.

Principal current line-level attacks covered:

- authority and exact supersession at lines 9–76;
- identities, private ownership and command-ledger shape at lines 78–157;
- command/effect/worker transition grammar at lines 158–423;
- operation-kind-specific publication and generic bypass refusal at lines 425–482;
- mandatory worker and last-permit traces at lines 484–509;
- specialized delivery success/non-success grammar at lines 511–642;
- participant lifecycle at lines 644–707;
- neutral storage, lookup, terminal/release and retirement grammar at lines 709–895;
- migration product at lines 897–995;
- complete finding maps, ownership, deferrals and cap language at lines 997–1121.

Exact controlling comparisons included accepted overlay ownership/publication at `W2-AdmissionLifetimeRedesign.md:230–269`, worker authority at `:315–359`, subscription/refresh/delivery lifecycle at `:615–674`, and A6 neutral/capacity requirements at `docs/adr/A6-subscription-snapshot.md:10–21`.

Inspection used only permitted read-only `shasum`, `wc`, `rg`, `sed`, `nl`, `cat` and `diff`. Optional source tests were not run because the source remains deliberately stopped and cannot prove prospective design closure. No helper was used. No current round-3 peer report, peer prompt, same-origin closure or originating closure report was read. No file, source, test, ADR, report, manifest, archive, bytecode, generated artifact, Git/GWZ state, network resource, service or database was modified.

## 2. Invariant analysis

### Neutral terminal and release conservation

The original `Consistency-2 P2-1` trace now has one closed outcome:

1. A refresh operation owns one lease and one ancestry/generation charge.
2. Its charged operation record holds at most one exact current candidate.
3. On a trusted neutral classification, one mutation consumes that candidate; advances `produced_through`; extends or creates the sole neutral span for the gap; performs at most one replay eviction; appends the exact replay record; records terminal refresh `SUCCEEDED`; and releases the charge once.
4. It creates no batch, envelope, buffer permit or publication.
5. If no changed work blocks semantic delivery, the neutral prefix folds immediately; otherwise it remains behind the exact changed head.
6. Exact candidate or receipt replay while retained reads the committed terminal/release facts and changes no cursor, owner, count or publication.
7. After eviction, either opaque handle is unavailable and cannot select a lease or cause another release.

The error dispositions also form a closed grammar. Presentation-only mismatch preserves the candidate, owner and charge for the original authority. Cursor divergence, registration retirement, overflow, close, fence, migration or trusted classification failure terminalizes/releases immediately only when authoritative quiescence already holds. Otherwise the exact lease transfers to containment, retains its charge and can terminalize only after exact worker stop. `RefetchRequired` is not exposed for a known active candidate before its refresh lease is terminal and released.

This restores the accepted overlay’s requirement that each refresh remains leased through cursor/candidate disposition while preserving the zero-buffer-permit neutral outcome.

### Finite opaque lookup is now implementable

The original `Consistency-2 P2-2` contradiction is removed without changing the identity representation:

- empty handles expose no cursor, registration, issuer or serial;
- the internal receiver fixes the target registry/registration;
- candidate lookup examines only the target’s exact current candidate fields and its replay ring;
- receipt lookup examines only the replay ring;
- current fields are bounded by `A <= L_refresh` and cannot outlive their charged operations;
- replay remains bounded by `R == C`;
- no evicted identity tombstone or side table survives.

After substantially more than `R` commits, the oldest candidate and receipt are absent and receive `RefreshRecordUnavailable`, exactly like a cross-registration, counterfeit or retired-registration identity. The result is deliberately non-provenance-bearing. In-window candidate/receipt replay remains exact; a current unconsumed candidate remains distinguishable only because the charged operation still owns its exact private record.

The required future test is therefore satisfiable with finite state: it can assert current, replay and uniform-absent outcomes plus `A`, `C`, cursor, owner and count bounds without reconstructing discarded history.

### Delivery publication has one linearization point

The `Safety-2 P2-1` last-permit trace now closes:

1. Final command acceptance and guarded assembly create nonterminal `PUBLICATION_READY`; no publication bit, terminal outcome or release exists yet.
2. Generic success and generic containment completion inspect the delivery operation kind and refuse mutation-free.
3. The specialized success mutation validates exact candidate, handoff lease, continuation owner, receiving task/lifecycle serial, original context, registration, binding/generation, barriers, value digest and FIFO head.
4. One indivisible commit records publication, removes/folds the head, advances `delivered_through`, records terminal `SUCCEEDED`, removes active ownership and releases ancestry/shared charge once.
5. Only after that commit may the closed value be exposed.
6. Exact replay reads one settlement tombstone without exposure, cursor movement, folding, terminalization or release. Conflict changes nothing.

A migration, close, fence or receiver-loss race before the commit instead enters specialized non-success retirement while the active charge remains. The same race after the commit sees publication, FIFO truth, terminal state and count already settled together. There is no state in which the last permit is released while the FIFO head remains unsettled.

### Non-success delivery settlement retains ownership through exact stop

Every legal non-success before delivery publication uses the same two-phase grammar:

1. `begin_delivery_non_success` leaves `delivered_through` unchanged, fails the head, marks the registration `RETIRING_REFETCH`, invalidates successors and releases their real queued permits once, blocks new registration work, revokes remaining authority and transfers the active handoff to its preallocated containment owner.
2. It does not terminalize or release the active handoff, regardless of cancellation, fence, receiver loss, cleanup failure, close or migration.
3. Only the bound executor can prove both command and iterator-frame stop after all finite cleanup.
4. Stop observation marks the retained handoff quiescent without release.
5. Specialized final settlement alone records terminal `REFUSED`, removes active ownership, releases once, records `RETIRED` and returns `RefetchRequired`.

The route cannot claim `CANCELLED_CONFIRMED` after a handoff began, cannot accept a previously releasing generic outcome and cannot be bypassed by generic containment. Exact replay of either phase is read-only; conflicting success/non-success is mutation-free.

### All five stopped roots remain prospectively covered

- **Worker exit:** effect reservation remains atomic before invocation; failures, `BaseException`, cancellation and receiver loss revoke unused ordinals and transfer to containment before another effect can begin. Exact stop remains distinct from A7 truth.
- **Failed FIFO:** unpublished head failure leaves delivery unchanged, invalidates successors, retains the active charge through stop and requires a complete A6 refetch baseline. The specialized success path now strengthens the original disposition.
- **Participant lifecycle:** membership remains activation-bracketed; pre-join authority is impossible; frozen attempt membership cannot mutate; final leave requires local closure and absence of every retained obligation.
- **Neutral refresh:** trusted classification, produced/delivered separation, coalesced spans, finite replay and atomic neutral terminal release preserve causal progress without a batch or delivery permit.
- **Phase proof:** exact phase, serial, request and successor remain required; stale same-attempt DRAINING proof, replay, wrong successor/request and every post-effect presentation refuse without mutation.

### Surrounding accepted invariants remain coherent

The correction leaves no raw `Plan` seam, no worker transfer of public-context claims, no caller-supplied task/worker/containment identity, no independent child permit and no second worker-state owner. Parameters, resource ancestry, operation kind, binding and generation remain pinned. The finite command schedule retains at most `M` records and one active serial. Body/effect/cancellation primacy remains ordered before cleanup diagnostics. Publication, worker quiescence and A7 transaction knowledge remain independent.

The accepted overlay’s former `PUBLISHING` then completion/release grammar is expressly and narrowly refined at the final barrier: non-delivery uses one generic commit; iterator delivery uses one specialized commit that additionally owns FIFO settlement. The supersession table, state grammar, causal tests and future ownership table agree on that rule.

## 3. Risks and next action

This GO is prospective design closure only. The frozen source still contains the known stopped defects and remains unaccepted. The report does not prove production executor ordering, locks, async/thread cancellation, database behavior, durable crash recovery, physical or cross-process fencing, resolver/provenance, credentials, activation, packaging, external capture or the W3 public surface.

Correction 2/2 is exhausted, but no new architectural root or other blocker was found, so the STOP rule does not activate and no third patch is warranted.

The single next action is the lane owner’s exact merge of the required focused Consistency/Safety verdicts and originating retracing on this same 115-file tuple. Only the complete required GO set may accept the replacement design, and that acceptance must remain design-only. Any source implementation requires a separately authorized execution brief, write boundary, executable regressions and source review.
