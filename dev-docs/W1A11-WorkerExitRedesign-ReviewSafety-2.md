# W1A11-WorkerExitRedesign — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; operator-authorized correction 1/2 design candidate, not accepted and not implementation authority, dated 2026-10-04.  
**Baseline:** Approved no-Git filesystem-SHA exception. The 100-entry `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-2.sha256` remained at SHA-256 `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`. Sources and documents were read directly from the filesystem. The controlling DRAFT remained at SHA-256 `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`.  
**Date:** 2026-10-04  
**Axis:** Safety — degraded paths, irreversible transitions, retained ownership, stuck states, bounded resource behavior and fail-closed adversity. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks. It is a new bounded contract root, not a new architectural root. I pre-commit to GO on a revision that resolves `P2-1` as specified without introducing another blocker.

---

## Prior-finding closure table

| Round-1 ID | Disposition claimed | Verified on corrected design | Status |
|---|---|---|---|
| `Consistency-1 P2-1` — migration edge conflicts with retained accepted grammar | Explicitly supersede accepted overlay §3.1 and §8.2 steps 6–8; define one deployment-state × attempt-phase product | §§2 and 11 (`:68`, `:727-825`) now name the exact supersession, enumerate the closed product, invalidate DRAINING proofs on phase change, and forbid pre-effect reopen after `EFFECT_BEGUN` | **CLOSED ON DESIGN; SOURCE REMAINS OPEN** |
| `Consistency-1 P2-2` — singular command record cannot represent sequential commands | Add a finite operation-owned command ledger, one active serial and retained per-command tombstones | §§3–7 (`:100-122`, `:197-216`, `:243-250`, `:413-428`, `:479`) define bounded `M`, distinct command records, guarded C1→C2 dispatch, cross-command isolation and one outer release | **CLOSED ON DESIGN; SOURCE REMAINS OPEN** |
| `Consistency-1 P2-3` — body failure can lose primary status to cleanup | Commit non-effect body failure before cleanup; cleanup-only failure is primary; later failures are bounded diagnostics | §§5.2–5.3 (`:307-314`, `:382-409`) now give one ordered wrapper schedule and the required body/effect/cleanup/cancel regressions | **CLOSED ON DESIGN; SOURCE REMAINS OPEN** |
| `Consistency-1 P2-4` — neutral lineage/replay bypasses the live bound | Derive finite `Q`, `C` and `R`, coalesce spans, bound replay and settlement work | §10 (`:618-725`) defines `Q`, `C = Q + 1`, `R = C`, at most `2C` lineage records, deterministic eviction and bounded retirement | **CLOSED ON DESIGN; SOURCE REMAINS OPEN** |
| `Safety-1 P2-1` — vanished receiving task strands success/ownership | Add trusted exact task-lifecycle observation and containment transitions through prepublication | §§3, 5.2 and 7 (`:134-144`, `:333-365`, `:480`) invalidate the exact context binding, remove or contain every relevant state and allow containment completion without receiver resumption | **CLOSED ON DESIGN; SOURCE REMAINS OPEN** |
| `Safety-1 P2-2` — zero-permit neutral traffic creates unbounded state/work | Coalesce neutral gaps and bound receipt replay/storage and per-mutation work | §10 (`:618-725`) closes the delayed-head sequence with bounded spans/ring state, typed stale/unavailable outcomes and capacity assertions | **CLOSED ON DESIGN; SOURCE REMAINS OPEN** |

## Changed-range analysis

I compared the corrected design with the preserved revision-1 design at `dev-docs/W1A11-WorkerExitRedesign-Revision1/W1A11-WorkerExitRedesign.md`. The changed ranges implement the six filed dispositions: explicit migration supersession, the multi-command ledger, pre-cleanup primary failure recording, receiver-lifecycle observation, bounded neutral lineage/replay, and their finding/test maps. They also correct A16’s authority status and preserve design-only limits.

The blocking finding below is in the otherwise unchanged interaction between §6’s generic final-publication rule and §8’s FIFO settlement rule. It is therefore a newly discovered round-2 root, not a regression introduced by one of the six correction hunks.

`P2-1` is **bounded, not architectural**. The selected architecture already requires one lifetime-registry mutation owner and explicitly says buffer, handoff, operation and generation-count changes share that owner. The defect is that two clauses assign terminalization and permit release to incompatible points. Correcting the precondition and defining one atomic transition does not require a new owner, compatibility model, subsystem or public surface. The object remains at correction 1/2; a correction would consume correction 2/2, not restart the counter or create a hidden replacement object.

## 0. Evidence base

I read completely:

- `../AGENTS_GWZ.md`, product `AGENTS.md`, the complete review-loop `SKILL.md` and canonical reviewer template.
- The 937-line corrected redesign, DRAFT-2, operator brief, RemPlan-1, both complete prior full design reports and the originating design closure.
- The accepted composed W2 base and lifetime overlay, W1/W2 acceptance records, `PRODUCT_LAYOUT.md`, ADRs A1–A16 and the ADR index.
- Parent implementation-plan §§15–16 governing the filesystem-SHA exception and bounded review loop.
- The stopped amendment, both remediation plans, STOP decision, final `ReviewCode-3` and `ReviewState-3`, `FreshCodeClosure-2`, `OriginStateClosure-2` and `OriginCodeClosure-2`.
- The stopped reference shapes relevant to publication and FIFO settlement, especially `lifetime_reference.py:232-266`, `:360-387`, `:457-501`, `:545-589` and `buffer_reference.py:245-295`. They were treated only as evidence of the stopped failure, not as implementation authority.

Principal design attacks covered:

- ownership/identity and command-ledger grammar at `W1A11-WorkerExitRedesign.md:76-280`;
- success, failure, cancellation, task disappearance and cleanup at `:281-460`;
- mandatory worker schedules at `:462-485`;
- FIFO retirement/refetch and settlement at `:487-549`;
- participant lifecycle at `:551-614`;
- neutral lineage/capacity/replay at `:616-725`;
- migration product/proof grammar at `:727-825`;
- finding disposition, ownership and production limits at `:827-937`.

Exact supersession claims were compared with accepted overlay §3.1 (`:138-188`), ownership/publication clauses (`:249-269`), worker authority (`:315-359`), migration ordering (`:537-613`) and delivery lifecycle (`:615-674`), plus A6, A7, A8 and A11.

Integrity evidence at both START and END:

- revision-2 manifest matched `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`; 100/100 entries verified;
- object matched `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`;
- DRAFT-2 matched `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`;
- RemInputs-1 matched `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`; 13/13 verified;
- archived revision-1 verification map matched `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`; 88/88 verified from the product root;
- Inputs matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; 19/19 verified;
- stopped source MANIFEST-3 matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; 71/71 verified;
- ReadOnly matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; 111/111 verified;
- ProductGuard matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; 614/614 verified;
- the Safety prompt remained at `da47d050f7aae92224bbfb9d2547ab496ea9185e7fbaf1712259d4d828939924`.

Inspection used only permitted read-only `shasum`, `wc`, `rg`, `sed`, `nl`, `cat` and `diff` operations. No optional test was run because the existing tests exercise the known stopped source and cannot settle this prospective ordering contradiction. No current round-2 peer, same-origin closure, original-reviewer closure report or peer prompt was read. No file, bytecode, generated output, source, test, manifest, Git/GWZ state, network, service or database was modified; no helper was used.

## 1. Findings

### [P2-1] Final publication and FIFO settlement both claim terminalization and the same permit release

**Location:** `W1A11-WorkerExitRedesign.md:430-442` and `:487-530`, especially `:505-512`; retained accepted atomic-publication requirement at `W2-AdmissionLifetimeRedesign.md:259-264` and delivery requirements at `:650-656`.

**Root cause:** Section 6 says the final publication barrier atomically records publication and terminal `SUCCEEDED`, releases ancestry charges and the shared operation permit exactly once, and only then exposes the value. Section 8 defines a separate `settle_delivery_success` operation that requires both the publication bit and an already-terminal `SUCCEEDED`, then says its mutation removes the FIFO head, advances `delivered_through` and releases the handoff operation permit. The assertion that one lifetime-registry mutation owns all ledgers does not provide a legal order: settlement cannot precede terminal success because terminal success is its precondition, while following §6’s barrier releases the same permit before FIFO settlement and asks settlement to release it again.

**Violated invariant:** For an iterator handoff, caller-visible publication, FIFO head removal/cursor advancement, terminal lease state and the single shared-permit release must have one linearization point. Migration or close must not observe the permit released while publication remains unsettled, and no path may release it twice.

**Reproduction/state sequence:**

1. One registration has a single exact active FIFO head and no queued successor. Its handoff lease owns the last deployment permit.
2. The receiving task reaches the final publication barrier with all authority, generation and cursor checks current.
3. Per §6, that barrier atomically records publication and terminal `SUCCEEDED`, releases the last permit, and exposes the value.
4. Before the separately described `settle_delivery_success` advances `delivered_through` and removes the head, a migration observes the authoritative permit count at zero and crosses its pre-effect barrier.
5. Settlement now either refuses against the retired/fenced old registration, leaving a caller-visible value whose delivery cursor/head never settled, or applies and releases an already-released permit a second time.
6. Reversing the calls is not legal: §8 requires terminal `SUCCEEDED` before successful settlement.

The same split makes exact replay underspecified: §6’s repeated publication is idempotent for the committed receipt, but §8 separately owns head removal and release, so a crash-free retry cannot tell from the text whether it is replaying one atomic outcome or completing an outstanding second mutation.

**Impact:** The design permits false zero-count quiescence and migration/close cutover before delivery lineage is complete, or a double release/count underflow. It can also expose a value while retaining a stale active head and old delivered cursor. This defeats the exact-once permit, FIFO truth and no-cutover-before-terminal-ownership guarantees that the redesign is meant to establish.

**Required correction:** Define one exact handoff publication/settlement transition. The clean bounded correction is for `settle_delivery_success` to be the final publication linearization point: from a nonterminal publication-ready handoff, it must atomically validate the exact receipt/owner/barriers, record publication, fold the head and following neutral span, advance `delivered_through`, set terminal `SUCCEEDED`, release ancestry/shared charges once, and only afterward expose the value. It must not require a previously committed terminal outcome. Alternatively, fold those same registration mutations into §6’s generic barrier and make any later settlement a read-only replay that cannot release. Non-success settlement must likewise own retirement plus terminalization/release rather than consume an outcome committed by an earlier releasing path. State explicitly that generic completion cannot bypass these specialized handoff settlements.

**Closure test:** With one exact active head and no other permits, pause at every conceptual point around final barrier, terminal state, cursor/head settlement, permit release and outward exposure. Race migration, local close, fence and receiver loss at each pause. Assert there is no reachable state with released permit plus unsettled head/cursor, and no outward value before all four facts commit. Replay the exact success and assert no second cursor movement or release; conflicting success refuses mutation-free. Repeat every non-success path and prove retirement, unchanged delivered cursor, queued-successor invalidation, active quiescence and one release occur through its single atomic settlement.

## 2. Invariant analysis

The following attacks held:

- Effect reservation precedes invocation; nested, reentrant and concurrent reservations refuse; `BaseException` and running cancellation revoke unused ordinals and transfer to containment before another effect can begin.
- The finite command schedule and ledger retain distinct C1/C2 workers, authorizations, ordinals, exits and tombstones under one outer permit. Prior-command replay cannot mutate a later command.
- Body/effect failures commit before cleanup; cleanup-only failure is primary; later cleanup/cancellation diagnostics are bounded and cannot change ownership, effect knowledge or A7 truth.
- Worker success remains private until executor-issued stop observation and exact receiving-task acceptance. Wrong worker/task/receipt/tuple attacks are mutation-free.
- Trusted receiving-task disappearance invalidates the original operation authority and removes or contains queued, running, pending-success, quiescent-success and accepted-before-publication work. The containment owner can finish without the vanished task resuming.
- Worker quiescence, outer terminal state and A7 transaction truth remain independent. Late worker return cannot manufacture database knowledge or restore authority.
- Failed FIFO non-success follows one conservative rule: registration retirement/refetch, unchanged delivery cursor, invalidated successors, retained active charge through quiescence and complete new-snapshot recovery.
- Participant membership is activation-bracketed, exact-token-based and quiescence-bound. Frozen attempt membership does not mutate, while fully left runtimes disappear from later attempts.
- Neutral classification is trusted, sealed and lease-bound. `Q`, `C` and `R` bound changed entries, coalesced spans, replay records and lock-held retirement work; neutral progress cannot overtake changed delivery.
- Migration proof binds exact product phase, phase serial, phase request and successor. A DRAINING proof is stale after pre-effect migration entry, and `EFFECT_BEGUN` permanently disables the new pre-effect return edge.
- Plan/claims containment, pinned parameters, parent-owned derived work, exact task/worker providers and the single mutation-owner proposal remain intact.
- The document remains honest that deterministic reference transitions do not prove production locks, threads, database durability, physical fencing or crash recovery.

Those successful attacks do not resolve `P2-1`.

## 3. Risks and next action

Real async/thread workers, PostgreSQL/SQLite adapters, durable crash behavior, cross-process and physical fencing, database provenance, activation, credentials, public W3 Surface, external capture and Git remain explicitly deferred and are not findings. The frozen 71-file source remains stopped and unaccepted; this verdict neither demands that it implement the redesign nor closes any source finding.

The single next action is bounded correction 2/2: unify handoff publication, FIFO settlement, terminal state and the one permit release into an exact atomic transition; add the success/non-success/cutover regression above; then freeze a new exact tuple for the required re-verdicts. This finding does not authorize an architectural restart, implementation work or a hidden third correction.
