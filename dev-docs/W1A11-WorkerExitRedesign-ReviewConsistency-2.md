# W1A11-WorkerExitRedesign — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/W1A11-WorkerExitRedesign.md` at SHA-256 `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`; operator-authorized correction 1/2 design candidate, not accepted or implementation authority; 2026-10-04.  
**Baseline:** approved filesystem-SHA exception, read directly from `/Volumes/projects/limbo/datascad/garns-v9-6`; 100-entry `dev-docs/W1A11-WorkerExitRedesign-MANIFEST-2.sha256` at SHA-256 `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`. The stopped source remains immutable evidence at 71-entry `W1A11-ContractAmendment-MANIFEST-3.sha256` SHA-256 `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`; no Git revision or source acceptance is claimed.  
**Date:** 2026-10-04  
**Axis:** Consistency — internal coherence, agreement with the controlling graph, exact supersession, and satisfiable future evidence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block. Both are bounded corrections inside the selected architecture; no new architectural root was found. I pre-commit to GO on a revision that resolves `P2-1` and `P2-2` as specified without introducing a new blocker.

---

## Prior-finding closure table

| Round-1 ID | Disposition claimed | Verified on corrected design | Status |
|---|---|---|---|
| `Consistency-1 P2-1` | Explicitly supersede the accepted deployment edge grammar and define the deployment-state × attempt-phase product. | §§2 and 11 now name overlay §3.1 and §8.2 steps 6–8, enumerate the closed product, stale a DRAINING proof at phase transition, and forbid the pre-effect edge after `EFFECT_BEGUN`. | **CLOSED prospectively.** |
| `Consistency-1 P2-2` | Replace the singular command record with a bounded operation-owned ledger and retained per-command tombstones. | §§3–6 define schedule bound `M`, monotonically unique command serials, one active command, separate worker/authorization/effect/exit state, C1 tombstones during C2, guarded next-slot dispatch, and one outer permit. | **CLOSED prospectively.** |
| `Consistency-1 P2-3` | Commit a body failure before cleanup; make cleanup-only failure primary and later cleanup failures diagnostic. | §§5.2–5.3 now impose that exact ordering and bound diagnostics by the finite cleanup schedule. | **CLOSED prospectively.** |
| `Consistency-1 P2-4` | Bound/coalesce neutral lineage and replay with deterministic eviction and bounded settlement work. | `Q`, `C`, `R`, coalesced spans and storage/work ceilings are present, but neutral completion loses its lease-terminal rule and the required post-eviction candidate outcome cannot be implemented without the forbidden unbounded side table. | **OPEN as current `P2-1` and `P2-2`.** |
| `Safety-1 P2-1` | Add trusted exact receiving-task lifecycle observation and transitions for every prepublication state. | §§3, 5 and 7 bind a provider-issued task/lifecycle serial, invalidate original authority, remove queued work or contain every later prepublication state, and permit containment-owned completion without receiver resumption. | **CLOSED prospectively.** |
| `Safety-1 P2-2` | Bound neutral spans/receipts, define eviction/staleness and bound cleanup work. | Capacity and coalescing are explicit, but the neutral branch does not terminalize its refresh lease and the outside-window candidate distinction is incompatible with the stated storage and opaque-identity rules. | **OPEN as current `P2-1` and `P2-2`.** |

## Changed-range analysis

The revision-1 archive remains at design SHA-256 `62f86ff0ab6ff4beb8fba9c9e5ec9102581de0c5ac211c46e57ca09e117b9d57`; its 88-entry verification map was checked from the product root. The corrected design grew from 737 to 937 lines. Inspection of the complete unified diff and both complete documents showed material changes only in the correction dispositions: explicit migration supersession/product grammar, the multi-command ledger, pre-cleanup primary failure ordering, receiving-task disappearance, and bounded neutral lineage/replay, plus corresponding finding maps, tests and ownership descriptions.

Both current blockers are inside the neutral-lineage correction range:

- `P2-1` is a changed-range regression: revision 1 explicitly said a neutral commit “completes/releases only the refresh lease”; correction 1 removed that terminal disposition while rewriting the branch.
- `P2-2` arises from the new replay-window design: it simultaneously promises a distinct post-eviction candidate result and forbids the state needed to recognize such a candidate.

Both are **bounded**, text-fixable roots within the chosen single-registry architecture. Neither changes the mutation owner, accepted public surface, compatibility model, platform assumption or deployment architecture. No new architectural root was found, so this correction-1/2 review does not trigger the architecture cap or authorize a hidden restart.

## 0. Evidence base

At both START and END:

- `W1A11-WorkerExitRedesign-MANIFEST-2.sha256` matched `bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`; all 100/100 entries verified.
- The design remained at `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`.
- The controlling DRAFT-2 remained at `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`.
- The canonical Consistency prompt remained at `2f75f439c262b5d1fbbcb3a0540c3c365aa7ebfac1fb696724738be593142a23`.
- RemInputs-1 verified 13/13.
- The archived revision-1 product-root verification map verified 88/88.
- Original Inputs verified 19/19.
- The stopped source manifest verified 71/71.
- ReadOnly verified 111/111.
- ProductGuard verified 614/614.

I read completely:

- `../AGENTS_GWZ.md`, product `AGENTS.md`, the review-loop skill and its canonical template.
- The 937-line corrected design, DRAFT-2, complete Brief, RemPlan-1, both complete prior design round-1 reports, the complete originating design closure, and archived revision-1 DRAFT.
- The complete accepted W2 base and lifetime overlay, W1 and W2 acceptance records, `PRODUCT_LAYOUT.md`, ADRs A1–A16 and the ADR index.
- Parent implementation-plan §§15–16.
- The stopped amendment and STOP record; execution brief, both stopped-object remediation plans and restart verification; final `ReviewCode-3`/`ReviewState-3`; `FreshCodeClosure-2`, `OriginStateClosure-2`, and `OriginCodeClosure-2`.
- The exact Inputs/RemInputs/manifests and the relevant stopped candidate/registration state in `snapshot_reference.py` and `buffer_reference.py`, as evidence only.

Principal line-level comparisons included:

- Corrected design §§2–7, lines 53–485: supersession, command ledger, worker exit, task disappearance, cleanup, replay and publication.
- §8, lines 487–549: failed-head retirement/refetch and permit conservation.
- §9, lines 551–614: activation-bracketed membership.
- §10, lines 616–725: neutral capacity, replay, eviction and required future tests.
- §11, lines 727–825: migration product, phase/request proof and old-admission invalidation.
- §§12–14, lines 827–937: finding mapping, proposed cohesive ownership, deferrals and review gate.
- Accepted overlay §§3.1–5.1, lines 138–359; §§8.2–9, lines 537–674; A6 lines 10–21; A7 lines 11–26; A11 lines 18–37; and proposed A16 lines 64–86.
- Revision-1 neutral grammar lines 507–578, including its explicit refresh-lease completion at lines 534–538.
- Existing sealed candidate shape at `snapshot_reference.py:18–49,74–99,128–160`, confirming an empty candidate identity whose semantic fields live only in an issuer-private record.

Inspection used only permitted `shasum`, `wc`, `rg`, `sed`, `nl`, `cat` and `diff` commands. Optional tests were not run: this is a prospective design review, and the known stopped source cannot establish design closure. No current round-2 peer report, same-origin closure-2 report, current originating closure report or peer prompt was read. No helper was used. No file, source, test, ADR, manifest, bytecode, generated artifact, Git/GWZ state, service, database or network state was modified.

## 1. Findings

### [P2-1] The corrected neutral branch no longer terminalizes or releases its refresh operation

**Classification:** New bounded changed-range regression; not architectural.

**Location:** `W1A11-WorkerExitRedesign.md:657–681`, especially the neutral mutation at lines 670–676; whole-operation charge rules at lines 430–451; accepted overlay §9 at `W2-AdmissionLifetimeRedesign.md:622–648`. The removed controlling wording is visible at archived revision 1 lines 534–538.

**Root cause:** Correction 1 replaced the neutral-lineage paragraph and deleted its exact operation disposition. Revision 1 required neutral commit to consume the candidate, advance the cursor, create no buffer permit, return the receipt, and “complete/release only the refresh lease.” The corrected text still defines the first four actions but says nothing about lease state, owner, terminal outcome or release. A changed commit has an explicit lease-to-buffer-permit exchange; the neutral commit has no corresponding conservation edge.

**Violated invariant:** Every finite refresh owns one operation lease and shared generation charge until exactly one terminal completion or an explicit exchange. Advancing `produced_through` without a batch must not leave an ownerless or indefinitely charged operation, and exact replay must not release it twice.

**Reproduction/state sequence:**

1. Acquire one refresh operation lease; the local ancestry and deployment generation count are charged.
2. Produce an exact sealed neutral candidate for `(0,1]`.
3. Call `commit_refresh(candidate)`.
4. The corrected branch consumes the candidate, advances `produced_through`, creates no buffer permit and returns `NeutralRefreshReceipt`.
5. No specified transition changes the refresh lease to a terminal state or releases its charge.

If the implementation retains the lease, close and migration can remain blocked after successful neutral progress. If it silently releases in `commit_refresh`, it implements behavior no longer stated by the exact design. If it requires a later generic completion, cancellation or loss between cursor commit and that call leaves committed progress paired with a live operation, while neutral replay has no specified authority to finish that lease.

**Impact:** The future reference model cannot derive exact count/owner expectations for the mandatory neutral traces. A legal neutral refresh can leak the operation/generation permit or rely on an unstated second completion protocol, contradicting whole-operation conservation and the claimed zero-permit outcome.

**Required correction:** Restore an exact atomic neutral terminal edge: the same mutation that consumes the candidate and advances the cursor must record the refresh lease’s exact successful terminal outcome and release its ancestry/generation charge once, while creating no buffer permit. State how exact candidate/receipt replay observes that tombstone without another release. Give every `RefetchRequired` return from `commit_refresh` an equally explicit operation disposition.

**Closure test:** Start with one charged refresh and no buffer permits; commit a neutral candidate and assert cursor advancement, terminal refresh state, zero remaining operation charge, zero buffer permit, zero publication and one receipt. Replay the exact candidate and receipt, then race close/migration immediately before and after the commit; counts and terminal outcome must remain exact-once.

### [P2-2] Post-eviction candidate behavior requires the forbidden unbounded candidate history

**Classification:** New bounded consistency root inside the neutral replay correction; not architectural.

**Location:** Empty opaque identity rule at `W1A11-WorkerExitRedesign.md:95–98`; replay grammar and no-side-table rule at lines 628–644; issued-candidate lookup and eviction behavior at lines 657–685; provenance refusals and mandatory outside-window replay tests at lines 708–725. Existing candidate evidence confirms that `RefreshSnapshotCandidate` is an empty sealed identity and its `previous`/registration fields exist only in an issuer-private record (`snapshot_reference.py:18–49,74–99,128–160`).

**Root cause:** The design limits the replay ring to `R == C` and expressly forbids any candidate or receipt side table outside those bounds. After eviction, however, it requires presentation of the old candidate to be recognized as a previously issued candidate, recover its `previous`, compare that value with `produced_through`, and return typed `StaleRefreshCandidate`. The empty candidate exposes no cursor, registration, issuer or serial from which that fact can be reconstructed.

**Violated invariant:** The stated finite replay storage must be sufficient to implement every promised replay/provenance result. An evicted opaque identity cannot receive a history-sensitive result after all bounded records naming it have been discarded.

**Reproduction/state sequence:**

1. Establish capacity `C` and replay bound `R == C`.
2. Commit `R + 1` distinct neutral candidates while no changed lineage is retained; each candidate folds immediately, and the final commit evicts the first replay entry.
3. Present the first candidate again.
4. The design requires `StaleRefreshCandidate` because its hidden `previous` differs from current `produced_through`.
5. The replay ring no longer names that candidate, no auxiliary candidate table is permitted, and the empty candidate carries none of the required fields.

Discarding its private record makes it indistinguishable to this registry from an unknown, cross-registration or otherwise unavailable exact candidate. Retaining the record for every evicted candidate makes state grow without the `R == C` bound and recreates the exact unbounded side table correction 1 was meant to remove.

**Impact:** The mandatory inside/outside-window replay test is unsatisfiable as written. An implementation must either violate the storage bound, expose semantic data in an identity that the design requires to be empty, or return a different result than the specified `StaleRefreshCandidate`.

**Required correction:** Define one bounded post-eviction rule that requires no historical recognition. For example, only identities present in the live replay ring receive exact replay; any candidate or receipt absent from that ring returns one uniform typed unavailable/stale outcome without attempting to recover its former cursor or registration. Align unknown, cross-registration and retired-registration behavior with that bounded lookup, or explicitly change the identity representation and account for its provenance implications. Do not retain lifetime-long candidate tombstones.

**Closure test:** With `R == C`, commit substantially more than `R` neutral candidates. For the oldest evicted candidate and receipt, a live in-window candidate and receipt, an exact candidate from another registration, and a counterfeit object, assert the specified deterministic result, no cursor/lineage/count mutation, and storage never exceeding `C` replay entries with no auxiliary candidate history.

## 2. Invariant analysis

The following adversarial attacks held:

- Exact supersession is now coherent. The design quotes and expressly supersedes the accepted overlay deployment table and §8.2 steps 6–8 only for the new pre-effect edge. The closed product preserves post-effect indeterminacy and makes DRAINING proofs stale on entry to `MIGRATING_PRE_EFFECT`.
- The multi-command repair closes the singular-record conflict. C1 and C2 have distinct serials, workers, authorizations, effects, cleanup, exits and tombstones; only one is active and the outer permit is not reacquired.
- Body/effect/cancel primary-error ordering is now determinate. A non-effect body failure commits before cleanup, cleanup-only failure is primary, and later bounded diagnostics cannot replace effect knowledge or ownership.
- Receiving-task disappearance is no longer a liveness hole. Trusted task/lifecycle observation invalidates the original binding and removes queued work or contains running, pending-success, quiescent-success and accepted-before-publication work.
- Worker success remains private through cleanup, exit receipt and exact executor stop. Result acceptance requires the recorded receiving task, original live context and current barriers. Failure/cancellation revokes unused ordinals, transfers to containment and retains the charge through authoritative stop.
- Late completion, duplicate exit and conflicting outcome rules preserve one owner, one primary receipt and one result. Worker quiescence remains independent of A7 commit knowledge.
- Failed FIFO delivery selects one conservative rule: unpublished head failure retires the registration, leaves delivery unchanged, invalidates successors, conserves queued and active charges and resumes only through a complete new A6 snapshot baseline.
- Participant membership is activation-bracketed and quiescence-bound. Pre-join admission refuses, frozen attempt membership does not mutate, leave-pending remains an obligation for its current attempt, and fully left runtimes disappear from later attempts.
- Neutral causality and capacity arithmetic otherwise hold: `Q` bounds queued changed entries, `C == Q + 1` accounts for one active head, spans coalesce per changed-work gap, and normal fold work is bounded. The blockers are terminal conservation and impossible post-eviction recognition, not the produced/delivered ordering itself.
- One lifetime mutation owner remains proposed; worker-authority, snapshot, buffer and migration modules contain identities or subledgers rather than independent competing state owners.
- The design remains honest about its limits. It does not accept the stopped source or claim production worker, backend, lock, database, durability, crash, physical-fence, resolver/provenance, activation, credential or public-surface evidence.

Those successful attacks do not cure `P2-1` or `P2-2`.

## 3. Risks and next action

The frozen 71-file source still contains the known stopped defects and remains unaccepted; neither this report nor a later design GO closes source findings. Production PostgreSQL/SQLite/async/thread behavior, durable crash and cross-process fencing, resolver/provenance proof, public W3 Surface, credentials, activation, external capture and Git remain explicitly deferred and are not findings.

The single next action is one consolidated bounded correction to §10 that restores exact neutral refresh terminal/release semantics and makes outside-window replay implementable within the declared storage bound, followed by a new exact tuple and the required review/closure retracing. The object is currently correction 1/2. No new architectural root was found, so the redesign cap does not require STOP; no acceptance or implementation authority follows from that classification.
