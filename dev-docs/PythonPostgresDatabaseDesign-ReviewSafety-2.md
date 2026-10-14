# Python PostgreSQL Database Design: Safety Review 2

## Verdict

**GO, design scope only.** Both prior Safety findings close on this revision. No new reproducible Safety defect was established.

This verdict does not accept an implementation, freeze public names, authorize deployment activation, or establish PostgreSQL support. Separate Surface review and the declared implementation gates remain required.

## Object and Evidence

- Repository: `garns`, workspace `garns-wz`.
- Required and observed HEAD: `f1adc67a4d9c9fbe6b1177e23f10f5eef186cb31`.
- Controlling object: `dev-docs/PythonPostgresDatabaseDesign.md` at that commit.
- Companion object: `dev-docs/PythonPostgresApiWalkthrough.md` at that commit.
- Axis: Safety.
- Reviewer role: independent replacement reviewer, adversarial and read-only.

At both START and END:

| Verification | Result |
|---|---|
| `git rev-parse HEAD` | Exact required SHA |
| `shasum -a 256 -c dev-docs/PythonPostgresDatabaseDesign-Inputs.sha256` | All 18 entries passed |

Both target documents were inspected through pinned `git show`. Every manifest entry was read as authoritative working-tree content, without substituting historical Git versions. Acceptance records were applied only within their stated scopes: accepted W1 contracts, the composed W2 base/overlay, and accepted worker-exit reference evidence.

Process instructions, the review-loop skill, prior `ReviewSafety-1`, `RemPlan-1`, the new vectors file, and the target-document correction diff were inspected. No other current-round report or prompt was accessed.

Only permitted inspection commands were used. No files, Git state, services or databases were changed. No tests, builds or network operations were performed. Vector bytes and recorded digests were inspected, not independently recomputed.

References below use repository-relative paths and document sections.

## Prior-Finding Closure

As the replacement Safety reviewer, I independently retraced both original counterexamples.

| Prior ID | Root classification | Correction and retrace | Status |
|---|---|---|---|
| P2-1: missing indeterminate-migration recovery surface | Bounded lifecycle/interface omission | Design §§3,7 and walkthrough “Close and evolve” define privileged `recover_migration`, discoverable request/attempt references, availability while ordinary admission is fenced, retained ownership across close/restart, and exact recovery outcomes. Retraces below no longer reach an unnamed recovery route. | Closed at design level |
| P2-2: undefined transaction-wide deadline | Bounded configuration/ownership omission | Design §3 supplies `operation_seconds=120`, starts it before acquisition, includes caller idle time and every transaction call, prohibits renewal, and requires supervised expiry. The original indefinite-lock timeline is no longer permitted. | Closed at design level |

### P2-1 Recovery Retraces

1. **Cancellation before effects:** Recovery requires the accepted exact no-effect phase proof and barrier acknowledgements before reopening the old binding under a new admission epoch. Cancellation alone cannot reopen it.
2. **Accounted migration interrupted after effects:** The durable attempt descriptor survives. Recovery requires exact generation, transaction identity/payload digest and complete effects, together with authoritative outcome evidence. Missing evidence leaves `INDETERMINATE`; it does not authorize another attempt.
3. **Metadata-only publication with acknowledgement loss:** Recovery reads the atomic generation/proof record, not a data revision. Matching the exact descriptor yields `SUCCESSOR_CONFIRMED` without repeating SQL.
4. **Accounted publication with acknowledgement loss:** Exact durable publication and accounting evidence establish successor success; SQL is not replayed.
5. **Wrong request, stale attempt/epoch, absent table or inspection-only evidence:** These cannot clear the fence. Invalid references yield refusal without state change.
6. **Provisioner closed or restarted while uncertain:** A newly opened privileged Provisioner can recover without ordinary data admission. Close neither destroys the descriptor nor establishes rollback.

These are textual state-machine retraces, not executable crash-recovery evidence. Backend proof construction remains deferred to its implementation gate.

### P2-2 Deadline Retrace

Using defaults, acquisition occupies t=0..10, apply t=20..40, and caller idle time extends to t=119. Commit begun at t=119 remains bounded by t=120, rather than obtaining a fresh 30-second window.

If the caller remains idle beyond t=120, supervised expiry revokes new effect/commit authorization and starts bounded cleanup. Before commit request, only confirmed abort establishes `KNOWN_ABORTED`. After commit request, expiry cannot turn uncertainty into abort. Cleanup may extend to t=130 but cannot erase retained obligations merely because its budget expires.

## Changed-Range Analysis

| Changed surface | Safety attack and result |
|---|---|
| Design §3; walkthrough configuration/write sections | Challenged deadline renewal, idle-owner expiry and late commit. The shared absolute deadline and supervised revocation select one finite ownership boundary. |
| Design §4.1 | Challenged missing/unknown version, incomplete mapping, hostile identifiers, constraint removal and name collisions. Closed fields, IR-derived requirements and complete-name validation require refusal before DDL. |
| Design §6; walkthrough batch execution | Challenged mutation append, changed retry intent, regenerated defaults/stamps, implicit insert identity and competing identity owners. The immutable pre-effect batch, retained normalized bytes/provenance and serialized identity lookup prohibit those paths. |
| Design §7; walkthrough migration recovery | Challenged fenced recovery admission, restart, stale proof reuse and acknowledgement loss. Recovery is privileged, request-bound and non-reexecuting; incomplete evidence preserves the fence. |
| New vectors file | Inspected separate omitted, SQL-null and JSON-null encodings; exact integer/decimal/opaque atoms; ordered mutation batches; and explicit minimal binding bytes. These are encoding examples, not database or lifecycle proof. |

The new batch interface is a material public-surface change, so fresh replacement review was appropriate. It does not silently amend the accepted internal backend protocol: the design retains separate integration ownership and amendment gates.

No new architectural or bounded Safety root was established. `RemPlan-1` records one architectural correction used; this report neither resets that count nor requests another correction.

## Findings

**None.** No open P0, P1, P2 or P3 Safety finding remains on the reviewed design tuple.

## Invariant Analysis

| Attack area | Evidence and conclusion |
|---|---|
| Async ownership | Design §§1,3 preserves accepted task ownership and whole-operation lifetime authority. Child-task sharing, nesting, driver escape and graph-completion-as-commit evidence are not permitted. |
| Cancellation and close | Design §§3,6 and walkthrough close semantics retain the separation between worker quiescence and transaction truth. Repeated close cannot manufacture `CLOSED`. |
| Uncertain commit | Lost acknowledgement remains indeterminate. Reconciliation follows containment on an independent connection; missing rows cannot establish abort or authorize retry. |
| Retry and idempotency | Design §6 fixes ordered intent before effects, retains original payload/provenance, excludes regenerated stamps from caller intent and forbids uncertain-commit retry. Different intent under the same identity refuses. |
| Schema and induced effects | Design §§4.1,5,7 requires authored mapping, IR-derived constraints, drift checks and atomic accounting for cascades. Unsupported accounting or migration classes refuse before effect. |
| Roles and namespace | Separate privilege custody, catalog validation, qualified identifiers, session reset/discard and unsupported role/RLS refusal constrain bypass paths. Administrator/trusted-host compromise remains explicitly outside the threat model. |
| JSONB fidelity | Design §4 rejects duplicate keys, nonfinite values, invalid Unicode/NUL and numeric-range violations. Exact number parsing avoids float loss; bytes `b"null"` remain distinct from SQL NULL and omission. |
| Resource limits | Input, depth, member and canonical-expansion ceilings are stated. Canonical output cannot first be allocated without its bound check. Transaction phases cannot extend the aggregate deadline. |
| Cross-generation admission | Storage names/codecs/bounds participate in binding identity. Runtime revalidation, accepted generation permits and deployment-wide drain prevent stale-generation execution from being relabeled. |
| Fail-closed capabilities | Unsupported codecs, operators, exact SQLite decimal operations and unproved live/question support refuse. Exact-value activation remains gated on its additive artifact/result amendment. |
| Activation and retirement | Design §7 preserves operator-owned physical fencing and refuses the pending `CURRENT × NONE → RETIRED` capability. Recovery and resource close supply no protocol-reset shortcut. |

## Final Assessment

The exact HEAD and all 18 pinned authority entries remained unchanged at both review boundaries. The two original Safety counterexamples are closed by explicit interface and ownership rules, not by assertions that deferred implementations already work.

**GO for the reviewed design tuple only.** Production enforcement, real-server fault cuts, numeric boundary execution, cross-process fencing and cold Surface acceptance remain required at their declared gates.
