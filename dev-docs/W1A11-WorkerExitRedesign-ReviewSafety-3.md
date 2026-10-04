# W1A11-WorkerExitRedesign — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`; operator-authorized correction 2/2 design candidate, not accepted and not implementation authority; 2026-10-04.  
**Baseline:** Approved no-Git filesystem-SHA exception. Files were read directly from `/Volumes/projects/limbo/datascad/garns-v9-6`. The complete 115-entry review object is `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-3.sha256` at SHA-256 `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`. Revision 2 remains archived at design SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1` under its 100-entry product-root verification map. The stopped 71-file source remains immutable, unaccepted evidence.  
**Date:** 2026-10-04  
**Axis:** Safety — degraded paths, irreversible transitions, retained ownership, stuck states, bounded resource behavior and fail-closed adversity. Same-origin focused re-verdict plus changed-range attack. Independent, adversarial and read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — all three correction-2 P2 findings are prospectively closed in the design, all six correction-1 findings remain preserved, and no P0–P3 finding or new architectural root was found. This is prospective design closure only; the stopped source remains open and unaccepted.

---

## Prior-finding closure table

### Correction-2 findings

| ID | Disposition claimed | Original counterexample retraced on correction 2 | Status |
|---|---|---|---|
| `Consistency-2 P2-1` — neutral commit lacks terminal/release disposition | Make candidate consumption, cursor/span/replay mutation, refresh terminal `SUCCEEDED` and one ancestry/generation release one atomic neutral transition; give every known-current-candidate error an unchanged-owner, quiescent terminal-release, or containment-until-stop disposition. | Starting with one charged refresh, §10’s neutral commit consumes the current candidate, advances `produced_through`, updates/folds the bounded lineage, updates the replay ring, records terminal `SUCCEEDED` and releases once while creating no batch, buffer permit or publication. Exact candidate/receipt replay reads the recorded release without repeating it. Presentation-only mismatch leaves the candidate, owner and charge unchanged. Cursor divergence, retirement, overflow, close, fence, migration and trusted-classification failure either terminalize/release immediately when quiescent or retain the charge in containment until exact stop. | **CLOSED PROSPECTIVELY; SOURCE OPEN** |
| `Consistency-2 P2-2` — post-eviction behavior requires forbidden opaque-candidate history | Retain current candidate fields only in charged refresh-operation records, retain committed replay only in the `R == C` ring, and return one uniform `RefreshRecordUnavailable` for every candidate or receipt absent from those records. | After substantially more than `R` commits, the evicted candidate and receipt are absent and return `RefreshRecordUnavailable`, exactly like a cross-registration, retired-registration, unknown or counterfeit identity. A live current candidate resolves only through its charged operation record; an in-window committed candidate or receipt resolves only through the replay ring. No former cursor, classification, registration or provenance is reconstructed, and no auxiliary history is permitted. | **CLOSED PROSPECTIVELY; SOURCE OPEN** |
| `Safety-2 P2-1` — generic publication and FIFO settlement split terminalization and the same permit release | Make specialized delivery success the sole iterator final barrier; atomically publish, settle FIFO, terminalize and release once. Route every precommit non-success through specialized two-phase retirement, retaining the active charge through exact worker-plus-iterator stop. | With the handoff holding the last permit, `PUBLICATION_READY` remains nonterminal and unreleased. Generic success and containment completion reject the delivery operation kind. `settle_delivery_success` performs publication, head removal/neutral-span fold, delivered-cursor advancement, terminal `SUCCEEDED` and one release in one mutation before exposure. Every direct refusal, authority expiry, fence, cancellation, receiver loss, cleanup failure, close and migration before that commit instead begins retirement, releases queued successors once, retains the active charge through exact combined stop, and only then terminalizes `REFUSED` and releases once. | **CLOSED PROSPECTIVELY; SOURCE OPEN** |

### Original six design findings

| ID | Preservation attack on correction 2 | Status |
|---|---|---|
| `Consistency-1 P2-1` — accepted migration grammar conflicts with the new pre-effect edge | §§2 and 11 still expressly supersede only the named accepted clauses and retain the closed deployment-state × attempt-phase product. A DRAINING proof becomes stale on phase/serial/request change; only an exact current pre-effect proof can reopen once; `EFFECT_BEGUN` structurally removes the edge. | **PRESERVED CLOSED PROSPECTIVELY; SOURCE OPEN** |
| `Consistency-1 P2-2` — singular command record cannot represent sequential commands | The finite schedule of at most `M` records, one active serial, distinct command authority/effect/cleanup/exit state, retained prior tombstones and one outer permit remain unchanged. C1 replay cannot mutate C2, and queued C2 removal cannot erase C1 work or claim whole-operation cancellation. | **PRESERVED CLOSED PROSPECTIVELY; SOURCE OPEN** |
| `Consistency-1 P2-3` — body failure can lose primary status to cleanup | Non-effect body failure still commits before cleanup; effect failure is already committed by `run_effect`; cleanup-only failure becomes primary; later cleanup or cancellation races occupy only bounded diagnostics and cannot replace ownership, effect knowledge or A7 truth. | **PRESERVED CLOSED PROSPECTIVELY; SOURCE OPEN** |
| `Consistency-1 P2-4` — neutral lineage/replay bypasses the live bound | `Q`, `C = Q + 1`, `R = C`, one span per changed-work gap, at most `2C` lineage records, at most `C` replay records and resource-proportional current candidate fields remain explicit. Correction 2 removes the impossible history-sensitive eviction result rather than weakening these bounds. | **PRESERVED CLOSED PROSPECTIVELY; SOURCE OPEN** |
| `Safety-1 P2-1` — vanished receiving task strands success and ownership | Exact provider-issued task/lifecycle observation still invalidates the original context/operation binding and removes or contains every queued-through-prepublication state. Delivery-specific containment now strengthens eventual release by routing through §8’s quiescent non-success settlement instead of generic completion. | **PRESERVED CLOSED PROSPECTIVELY; SOURCE OPEN** |
| `Safety-1 P2-2` — zero-permit neutral traffic creates unbounded state/work | Neutral gaps still coalesce, replay remains `R == C`, no lifetime-long handle history exists, normal settlement handles one changed record plus one span, and retirement work is bounded. Current candidate state exists only while backed by a charged live refresh operation. | **PRESERVED CLOSED PROSPECTIVELY; SOURCE OPEN** |

## Changed-range analysis

The complete Revision-2-to-current unified diff is 652 lines; the design grew from 937 to 1,121 lines. The behavioral changes are confined to the three RemPlan-2 dispositions and their test, finding-map, ownership and authority text:

- §§2, 4–8 split generic non-delivery completion from specialized delivery settlement. New empty delivery candidate/receipt/retirement/stop identities describe one private state machine under the existing sole lifetime-registry mutation owner.
- §8 replaces the split successful settlement with one atomic publication/FIFO/terminal/release mutation and expands failed delivery into explicit retirement, exact combined-stop observation and final non-success settlement.
- §10 adds one current-candidate field to each already charged refresh-operation record, defines uniform bounded candidate/receipt lookup, supplies every current-candidate error disposition, and makes neutral terminal success/release part of the cursor/span/ring commit.
- §§12–14 update finding maps, mandatory traces, prospective file ownership and the correction-cap language.

These are bounded transition, lookup and retention corrections inside the selected architecture. They do not add a second mutation owner, another permit, a public compatibility surface, an unbounded tombstone subsystem, a new platform assumption or a new deployment architecture.

The principal interaction attack was registration retirement while both an active handoff and current refresh candidates exist. Overflow/retirement performs §8’s first non-success phase for the head, invalidates queued successors and releases their real permits once, but retains the active handoff charge. The triggering refresh candidate separately terminalizes/releases if quiescent or remains charged in containment until exact worker stop. Other live current candidates observe the retirement marker through their existing operation records and take the same constant-work disposition. Replay/lineage retirement cannot release those operations because it retains no authority for them. This produces no zero-count gap, double release or unbounded identity history.

No change falls outside the merged dispositions except status, evidence mapping and explicit correction-cap text. No new bounded or architectural root-cause candidate survived attack. Because correction 2/2 is consumed, a future new architectural root would require STOP and operator direction; this review found none and therefore does not trigger STOP or authorize a third patch.

## 0. Evidence base

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-3.sha256` matched `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`; all 115/115 entries verified.
- The design matched `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc` and remained 1,121 lines.
- DRAFT-3 matched `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae`.
- The canonical Safety prompt matched `50fe121ed546faee962abfcf3497ac8994efbb6b432cc7674596899f70b8fb5f`.
- RemInputs-2 matched `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993`; all 25/25 entries verified.
- The Revision-2 product-root verification map matched `4d1cbcc6626b6f41d6a0b04e08919d25177fed779f57338db79f36d05f88234c`; all 100/100 entries verified.
- RemInputs-1 verified 13/13.
- The Revision-1 product-root verification map verified 88/88.
- Original Inputs verified 19/19.
- The stopped source MANIFEST-3 verified 71/71.
- ReadOnly verified 111/111.
- ProductGuard verified 614/614.

I read completely:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, the review-loop skill and canonical reviewer template;
- the 1,121-line correction-2 design and DRAFT-3;
- RemPlan-2 and the complete 25-entry RemInputs-2;
- both complete prior round-2 full reports, `ReviewConsistency-2` and my `ReviewSafety-2`;
- all four prior round-2 originating closure reports: Code, Consistency, Safety and State;
- the complete archived Revision-2 design and all 652 lines of its unified diff to the current object;
- the earlier controlling brief, accepted W2 pair and acceptances, W1/A1–A16 and product-layout material, stopped amendment/STOP evidence, prior stopped reports and closures, RemPlan-1, both round-1 full design reports, originating round-1 closure evidence, and the relevant frozen reference shapes, as already read in this continuous design-review task.

Principal correction-2 line attacks covered:

- operation-kind-specific publication and generic-completion exclusion at current lines 203–225 and 425–482;
- receiver-loss and post-acceptance delivery containment at lines 342–394;
- last-permit success, every non-success cause, replay/conflict and exact combined stop at lines 511–642;
- current candidate accounting, finite lookup, quiescent/nonquiescent error disposition, neutral terminal commit and eviction at lines 709–895;
- all correction finding maps, preservation obligations, ownership and cap language at lines 997–1121.

Inspection used only permitted read-only `shasum`, `wc`, `rg`, `sed`, `nl`, `cat` and `diff`. Optional tests were not run because the frozen suite exercises the known stopped implementation and cannot establish prospective design closure. No helper was used. No current round-3 peer review, current originating closure, current same-origin report or peer prompt was read. No file, source, test, ADR, manifest, archive, bytecode, generated artifact, Git/GWZ state, network resource, service or database was modified.

## 1. Findings

No P0–P3 findings.

## 2. Invariant analysis

### Last-permit successful handoff

1. One active FIFO head holds the deployment’s last shared permit and reaches exact `PUBLICATION_READY`.
2. That state has no publication bit, terminal lease outcome or release. Candidate creation exposes nothing.
3. Generic success and containment completion inspect the delivery operation kind and refuse mutation-free. They cannot create the former early terminal/release state.
4. If migration, close, fence or receiver loss wins before specialized settlement, the permit remains charged and the handoff follows non-success retirement.
5. If `settle_delivery_success` wins, one lifetime-owner mutation validates the exact candidate, lease, owner, task/lifecycle, context, registration, binding/generation, barriers, value digest and FIFO head.
6. That single commit records publication, removes/folds the head and following neutral span, advances `delivered_through`, records terminal `SUCCEEDED`, removes active ownership and releases once.
7. Exposure occurs only after the complete commit. A later migration may observe count zero only alongside the settled head/cursor and terminal publication facts.
8. Exact replay reads the settlement tombstone without another exposure, cursor change or release. A different candidate, value, head, lease, owner, task or generation refuses without mutation.

The original split-settlement sequence therefore has no legal first step: no generic entry can terminalize or release the delivery before FIFO settlement.

### Every precommit non-success

Direct refusal, authority expiry, local fence, cancellation, receiving-task disappearance, cleanup failure, close and migration all use the same two-phase delivery rule:

1. `begin_delivery_non_success` leaves `delivered_through` unchanged, marks the head failed, moves the registration to `RETIRING_REFETCH`, invalidates every queued successor and releases each queued permit exactly once.
2. It revokes remaining worker/iterator authority and transfers the active handoff to its preallocated containment owner, but does not terminalize or release that active handoff.
3. `DeliveryStopObservation` can be issued only after the worker command, iterator frame and all finite trusted cleanup cannot resume.
4. Stop observation marks quiescence without releasing.
5. Specialized final settlement records terminal `REFUSED`, removes retained active ownership, releases ancestry and the one shared charge, records `RETIRED` and returns `RefetchRequired`.
6. Exact replay of either phase changes nothing. Conflicting success/non-success or a different cause refuses.
7. Because a handoff had begun, this route cannot claim `CANCELLED_CONFIRMED`; generic completion cannot consume its intermediate state.

Thus queued permits and the active permit have distinct exact release points, and close/migration cannot cross the zero-count barrier while worker or iterator execution can resume.

### Neutral success and close/migration races

For one charged exact current neutral candidate:

1. Lookup succeeds only in its live refresh-operation record.
2. The commit revalidates candidate, lease, operation, registration, admission, pinned inputs, binding/generation, queue, authority, migration state and `previous == produced_through`.
3. One atomic mutation consumes the candidate, advances the produced cursor, updates or immediately folds the appropriate neutral span, evicts at most one replay entry, appends the new replay entry, records terminal `SUCCEEDED` and releases once.
4. It creates no batch, envelope, buffer permit or publication.
5. A close/migration win before commit makes the known candidate unusable and applies its explicit terminal-or-containment disposition. A commit win leaves an already terminal, released operation and a bounded replay record.
6. Exact candidate/receipt replay while retained observes the committed terminal/release facts without another release. After eviction, both identities are simply unavailable.

The trace ends at operation count zero, buffer count zero and publication count zero without a live owner or an unstated second completion call.

### Neutral errors, eviction and retirement interaction

A presentation-only mismatch that leaves the recorded operation valid returns `RefreshCommitRefused` with candidate, owner, lease and charge unchanged. A current candidate invalidated by cursor divergence, registration retirement, overflow, close, fence, migration or trusted-classification failure has exactly two routes:

- already-quiescent work atomically removes commit eligibility, records terminal `REFUSED`, releases once and returns `RefetchRequired`;
- possibly resumable work loses commit authority, transfers to containment and returns `RefreshContainmentPending`; exact worker stop then authorizes the sole terminal `REFUSED` release.

Overflow additionally retires the registration, invalidates queued successors and, if a head is active, begins its separate §8 retirement without releasing the head. No `RefetchRequired` is exposed for the current refresh until that refresh lease is terminal and released. Removing its current candidate field makes later opaque presentation unavailable rather than a second terminalization attempt.

For more than `R` committed neutral candidates, storage remains at most `C` replay entries. The oldest candidate and receipt, a foreign-registration pair, a former-retired-registration pair and counterfeits all receive identical `RefreshRecordUnavailable` with no state mutation. The live current candidate remains distinguishable only while backed by its charged operation; an in-window committed pair remains distinguishable only through the replay ring. No history-dependent result survives eviction.

### Preservation of the five stopped roots

- **Worker exit:** effect reservation precedes invocation; reentrancy refuses; `BaseException`, cancellation and receiver loss revoke unused ordinals and transfer one owner before another effect can begin. Worker stop remains distinct from return, lease terminal state and A7 truth.
- **Failed FIFO:** unpublished head failure never advances delivery or permits a successor to cross. Registration retirement invalidates successors and requires a complete new A6 baseline.
- **Participant lifecycle:** construction before activation remains `UNJOINED`; exact open performs join; final leave requires local close and absence of every retained permit, handoff, worker, containment and A7 obligation; frozen attempt membership does not mutate.
- **Neutral refresh:** sealed trusted classification, separate produced/delivered cursors, no neutral batch/permit, causal gap boundaries and finite capacity remain intact.
- **Phase proof:** proof remains exact to coordinator, attempt, current phase serial, request and successor; DRAINING proof stales on pre-effect migration entry, and no pre-effect edge exists after `EFFECT_BEGUN`.

The correction also preserves the single lifetime mutation owner, task-bound claim-free public context, no executable `Plan` seam, pinned result roles and parameters, parent-owned commands, one outer permit, unchanged A7 truth and explicit design-versus-production limits.

## 3. Risks and next action

This GO establishes only that the prospective correction-2 text closes the reviewed design counterexamples without a new blocker. It does not close any finding in the stopped 71-file source or prove real executor stop evidence, async/thread cancellation, lock ordering, PostgreSQL/SQLite behavior, durable crash recovery, cross-process or physical fencing, resolver/provenance, activation, credentials, external capture, packaging or public W3 Surface.

The next action is for the lane owner to file this report verbatim and merge it with the independent Consistency re-verdict and required originating closure reports on the same exact tuple. Only the complete required GO set may accept the replacement design. Such acceptance would remain design-only; implementation requires a separate exact execution brief and explicit source authority.
