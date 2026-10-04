# W1A11-WorkerExitRedesign — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`; operator-authorized correction 2/2 design candidate, not accepted or implementation authority, dated 2026-10-04.  
**Baseline:** Revision 2 was read from `dev-docs/W1A11-WorkerExitRedesign-Revision2/W1A11-WorkerExitRedesign.md` at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`. DRAFT-3 and RemPlan-2 matched SHA-256 `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae` and `6f6ef5e31e7e2c488804a684337ad6f49db3ef7915d93a8a21eb5d8f78a1876e`. The 115-entry correction manifest remained at SHA-256 `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`. Sources were read directly from the filesystem under the approved no-Git filesystem-SHA exception.  
**Date:** 2026-10-04  
**Axis:** Same-origin focused Safety preservation check of `Safety-1 P2-1` and `Safety-1 P2-2`, including correction-2 changed-range inspection for new Safety roots. Independent, adversarial, read-only. The final full review pair runs independently; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — both original Safety findings remain closed prospectively on correction 2/2, and the changed range introduces no new Safety root. This focused preservation verdict is neither final design acceptance nor source acceptance.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| `Safety-1 P2-1` | Preserve the provider-issued exact receiving-task lifecycle observation and fail-closed transition from every queued through prepublication state. For iterator delivery, route receiver loss through specialized two-phase containment while retaining the active charge until authoritative worker-plus-iterator stop. | Re-traced the original vanished-receiver sequence through `SUCCESS_PENDING`, `QUIESCENT_SUCCESS`, `RESULT_ACCEPTED` and delivery `PUBLICATION_READY`. The task observation still invalidates the original context and operation binding. Non-delivery work completes under the containment owner; delivery begins retirement without publication or release, waits for exact worker-plus-iterator stop, then specialized final settlement releases once without receiver resumption. | **PRESERVED CLOSED** |
| `Safety-1 P2-2` | Preserve capacity-derived `Q`, `C` and `R`, coalesced neutral spans and bounded settlement work while adding atomic refresh terminalization/release and uniform unavailable behavior for opaque identities absent from bounded authoritative records. | Re-traced the delayed changed head followed by substantially more than `C` neutral commits. The gap retains one span, replay remains at most `R == C`, evicted identities leave no history, and current uncommitted candidates exist only in charged refresh-operation records. Each neutral commit terminalizes/releases atomically; replay never releases again. | **PRESERVED CLOSED** |

## Changed-range analysis

I compared the complete correction-2 object with the archived Revision-2 design. The 652-line unified diff is confined to the three RemPlan-2 dispositions and their ownership, regression and authority mappings.

The delivery range adds an internal operation-kind split, `PUBLICATION_READY`, a specialized single successful settlement barrier, and two-phase non-success retirement. Successful iterator handoff now commits publication, FIFO head/cursor settlement, terminal `SUCCEEDED` and the single ancestry/generation release in one lifetime-owner mutation before exposure. Generic success and containment completion structurally refuse delivery operations. Non-success invalidates queued successors but retains the active handoff charge until exact worker-plus-iterator stop and specialized final settlement.

This range touches the original receiver-loss closure but preserves its essential invariant. Receiver loss at delivery `PUBLICATION_READY` closes output, invalidates the original binding, prevents successful settlement, transfers the handoff to containment and retains the charge until authoritative quiescence. It does not restore dependence on the vanished task.

The neutral range adds one current candidate field per charged refresh operation, atomic neutral terminal success/release, explicit known-candidate containment or terminal dispositions, and one uniform `RefreshRecordUnavailable` result for every opaque candidate or receipt absent from the current operation record and `R == C` replay ring. It removes the Revision-2 history-sensitive post-eviction lookup and explicitly prohibits evicted identity history or auxiliary tables.

These are bounded transition and lookup corrections within the existing lifetime-registry ownership architecture. They add no mutable owner, public surface, compatibility model, platform assumption or uncharged lifetime history. No change falls outside RemPlan-2’s three dispositions except status, finding mapping and regression text. No new root-cause candidate was found, so there is no new architectural-root counter increment and no bounded Safety finding.

## 0. Evidence base

I read completely:

- `../AGENTS_GWZ.md`, product `AGENTS.md`, the complete review-loop `SKILL.md` and canonical reviewer template.
- The complete 1,121-line correction-2 design, DRAFT-3 and RemPlan-2.
- Both complete prior full Revision-2 reports: Consistency at SHA-256 `740e14350efe532cce940c655ef4a03b76f9ffd46f96df353ef06503149d0dec` and Safety at SHA-256 `6d3785cdcddeb3b0e1589e28da3ceba5ece4d328707fe4c8449b665658d5f3ff`.
- My complete prior focused report, `W1A11-WorkerExitRedesign-OriginSafetyClosure-2.md`, at SHA-256 `c6c50b5b9b684d779f8e22c197866ef12b789374eed53ab43d0256cce191d81e`.
- The archived Revision-2 design and the complete Revision-2-to-current unified diff.

I did not read any current round-3 review or closure report, current round-3 reviewer prompt, or other current testimony.

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-3.sha256` matched `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737`; 115/115 verified.
- `W1A11-WorkerExitRedesign-RemInputs-2.sha256` matched `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993`; 25/25 verified.
- The Revision-2 archive map matched `4d1cbcc6626b6f41d6a0b04e08919d25177fed779f57338db79f36d05f88234c`; 100/100 verified.
- The Revision-1 archive map matched `50550d3e44adeea13c63240d4a28cd96444f5543c83cdbee5e5b000abccb81e8`; 88/88 verified.
- `W1A11-WorkerExitRedesign-RemInputs-1.sha256` matched `59896d17afe746021c9ec4cac87d67b48d35d437a3481f5177175a77c89d347c`; 13/13 verified.
- `W1A11-WorkerExitRedesign-Inputs.sha256` matched `46b37274e604832925f72bf722576aed79345e339e09053a9951aa68fa728a52`; 19/19 verified.
- The stopped source manifest matched `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; 71/71 verified.
- ReadOnly matched `185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d`; 111/111 verified.
- ProductGuard matched `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`; 614/614 verified.

The object, DRAFT-3, RemPlan-2, both prior Review-2 reports, prior focused closure and archived Revision-2 object retained their exact hashes at the end boundary. The historical live MANIFEST-2 was not checked against changed design bytes; its 100-entry Revision-2 archive map was used.

Inspection used only read-only `pwd`, `rg`, `sed`, `nl`, `diff`, `wc` and `shasum` operations. No tests were run because this is a prospective design review and the stopped source cannot establish these corrected state transitions. No file, source, test, manifest, bytecode, Git/GWZ state, network, service or database was modified or invoked. No helper was used.

## 2. Invariant analysis

The original `Safety-1 P2-1` sequence remains closed:

1. Dispatch binds the exact receiving task and monotonically unique lifecycle serial.
2. Worker success remains private through `SUCCESS_PENDING`, exact executor stop and `QUIESCENT_SUCCESS`.
3. If the receiver terminates, the trusted provider’s exact observation atomically invalidates the original context record and operation binding.
4. `SUCCESS_PENDING` closes the result, transfers to containment and waits for exact stop. `QUIESCENT_SUCCESS` closes the result and moves directly to `QUIESCENT_CONTAINED`.
5. After `RESULT_ACCEPTED`, receiver loss closes assembly/output without reopening the command or publishing.
6. A non-delivery containment owner terminalizes and releases once. No replacement task acquires result authority.

Correction 2 preserves that path for iterator delivery. At `PUBLICATION_READY`, no publication bit or release has occurred. Receiver loss wins by invalidating the binding and directing the handoff into `begin_delivery_non_success`. That first phase leaves `delivered_through` unchanged, invalidates queued successors once, revokes remaining worker/iterator authority, transfers the active handoff to the preallocated containment owner and retains its charge. Only an executor-issued observation proving both worker-command and iterator-frame stop can make it quiescent; specialized final settlement then records `REFUSED`, removes retained ownership and releases once. The vanished task is not needed for either phase.

The success-versus-loss race also closes. Successful settlement revalidates the exact current receiving task, lifecycle serial, original context and barriers in its sole final commit. If receiver loss commits first, success validation cannot cross the invalidated binding and the non-success path owns the handoff. If successful settlement commits first, publication, FIFO settlement, terminal success and release are already one indivisible result; the later lifecycle observation is an idempotent no-op and cannot relabel it. No interleaving exposes a value after receiver-loss containment or releases before an unsettled FIFO head. These rules appear at corrected design lines 140–150, 350–394, 444–471, 503–509 and 518–642.

Wrong task, context or lifecycle serial, copied observation, stale observation from task reuse and conflicting outcome remain mutation-free. Exact duplicate observation remains idempotent. Effect knowledge and A7 truth remain independent.

The original `Safety-1 P2-2` delayed-head sequence remains bounded:

1. Hold one changed head active so `delivered_through` cannot advance.
2. Sequentially commit substantially more than `C` neutral refreshes behind it.
3. Every neutral commit extends the same gap’s one `NEUTRAL_SPAN`; no per-neutral lineage node, batch, buffer permit or publication is created.
4. The same mutation consumes the current candidate, advances the produced cursor, updates the span, evicts at most one replay entry, appends one replay record, records refresh terminal `SUCCEEDED` and releases its charged operation once.
5. The replay ring remains at most `R == C`. Exact in-window candidate or receipt replay reads terminal/release facts without cursor movement or another release.
6. After eviction, candidate and receipt identities are absent from both bounded lookup locations and uniformly return `RefreshRecordUnavailable`. No former cursor, registration or classification is recovered, and no tombstone or side history survives.
7. When the changed head succeeds, the specialized settlement folds only that head and its one following span. Failure, overflow, close or migration discards at most `2C` lineage records and `C` replay entries in the bounded registration mutation.

Uncommitted candidates do not recreate the original free side queue. Each lives only in an already-charged refresh-operation record, at most one per live refresh lease, with `A <= L_refresh`. It is removed on commit, exchange or terminal containment. Registration retirement does not scan or copy those identities into history; each charged operation observes the retirement marker and performs constant-work terminalization or containment. Thus additional current state consumes retained operation capacity rather than bypassing capacity as the original zero-permit sequence did.

The uniform absent-identity rule is fail-closed. An evicted, cross-registration, cross-registry, retired, unknown or counterfeit opaque identity cannot select or complete a lease and produces no state mutation. A known current candidate under wrong presentation authority retains its exact owner and charge for the original authority; a candidate made unusable by close, fence, migration, overflow or retirement either terminalizes/releases when quiescent or transfers to containment until exact stop. These rules appear at corrected design lines 711–895.

The correction-2 handoff changes also preserve the neutral frontier invariant. The successful handoff barrier folds the immediately following neutral span in the same commit that records publication, removes the head, advances delivery, terminalizes and releases. Generic completion cannot release first. Non-success leaves delivery unchanged and retains the active handoff charge through quiescence. Neutral produced progress therefore cannot be mistaken for delivery or authorize a migration/close zero-count barrier while the head remains unsettled.

## 3. Risks and next action

Real task-provider integration, executor stop delivery, async/thread scheduling, lock ordering, database adapters, durability, crash recovery, cross-process fencing, physical provenance and production atomicity remain deferred implementation evidence. They are not findings against this prospective design. The mandatory causal and property traces remain requirements for a later separately authorized contract/reference build.

The stopped 71-file source remains open and unaccepted. The single next action is to file this report verbatim and complete the required correction-2 focused re-verdicts, final full review pair and other originating closures on the exact 115-entry tuple. Only the combined required gate may accept the replacement design. This focused GO does not self-accept the design, close source findings or authorize implementation.
