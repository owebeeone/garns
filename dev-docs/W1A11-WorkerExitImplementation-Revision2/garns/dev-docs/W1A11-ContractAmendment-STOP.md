# GARNs W1 A11 amendment stop decision

Status: STOPPED, not accepted. Date: 2026-10-04. Owner: manager.

Both completed final reviews report NO-GO on the same frozen 71-file tuple.
The State reviewer independently classified the missing worker-exit ownership
grammar as a new architectural root. Both permitted architecture corrections
have already been used, so the review-loop skill requires an operator
redesign-or-accept decision. No third architecture patch, bounded-only patch,
replacement object or downstream implementation has been launched.

## Exact stopped object and reports

MANIFEST-3 SHA-256:
`23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424`.
Controlling amendment SHA-256:
`f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f`.
DRAFT-3 SHA-256:
`3a6a1a342573b060b1c102318c7502fbcdeddd43438209c51c29899bfae95c2e`.

Reports are filed verbatim; the following hashes pin their testimony:

| Report | Verdict | SHA-256 |
|---|---|---|
| ReviewCode-3.md | NO-GO, two P2 findings | `37a041d8ff5fba5f25fb0f0df236b9cd83e3a86587931c149ce49892a81eac2f` |
| ReviewState-3.md | NO-GO, three P2 findings | `d827e94d3945163573fa2cc37d872e6be8381b7d93e15019f60b12defaa37712` |
| OriginCodeClosure-2.md | GO on its original nine Code findings only | `28bee6fed6274681257e130ff2e59b462c1adcccd531038adc96b065400a4a10` |
| FreshCodeClosure-2.md | NO-GO, bounded delivery residual | `d3ba77a8a89064c2cc6f6392805080374edacd1ad0d9718c366130bad86aa771` |
| OriginStateClosure-2.md | NO-GO, bounded same-attempt cross-phase proof residual | `caea59c3e8787607e2bf8931e94b3d1dd28dfb7b7f481582426b3f5a41667a80` |

All filenames above have the W1A11-ContractAmendment- prefix and live in
dev-docs/. Current full Code/State reviews were procedural replacements after
the operator's session pause; unfinished attempts produced no verdicts. Both
replacements used the original exact canonical prompts, remained peer-blind to
each other and the current closure reports, and verified the tuple at both
ends. This retry did not consume or reset a correction round. Lost originating
agent contexts cannot be claimed intact for a future closure check.

## Merged blocking findings

Every current blocking ID has an accepted disposition below. There are five
distinct roots, all P2; one is architectural. No finding is waived or self-closed.

| Root | All current report IDs | Classification and disposition | Required closure evidence |
|---|---|---|---|
| Worker-exit ownership | ReviewState-3 P2-1 | New architectural root; accepted, STOP for operator-directed redesign. Dispatch/dequeue exists but successful worker-to-runtime and failed worker-to-containment transfers do not. An effect exception leaves later ordinals usable. | Exact tuple-bound success/failure/cancellation transfers; exception immediately contains work and revokes unused ordinals; wrong owner/command/authorization refuses; charge persists until authoritative quiescence; only exact resulting owner can publish/complete. |
| False delivered progress on failed handoff | ReviewCode-3 P2-1; ReviewState-3 P2-2; FreshCodeClosure-2 P2-1, retaining ReviewCode-2 P2-2 and ReviewState-2 P2-1 | Bounded F2 residual; accepted and held for authorized redesign. Both fresh full axes independently converged, as did the pre-pause originating Code closure. | Only exact committed successful delivery advances deliveredThrough. Refused/cancelled/expired/fenced head preserves cursor and prevents later delivery; choose explicit refetch/retirement or exact retry semantics with conserved permits and idempotent terminals. |
| Activation-bracketed participant lifecycle | ReviewCode-3 P2-2 | New bounded omission of accepted join/leave semantics; accepted and held. Participants and admissions can exist before activation, and final runtime close never unregisters membership. | Reject authority crossing activation; exact join/leave pair; retained work prevents unregister; closed idle runtime leaves later migration topology; duplicate/stale/copy/cross-owner leave and join/leave during frozen attempt preserve its participant set. |
| Neutral refresh | ReviewState-3 P2-3 | New bounded omission of A6/accepted overlay; accepted and held. Only enqueue advances producer progress. | Exact trusted sealed neutral candidate advances internal cursor once without batch/envelope/permit; next non-neutral refresh follows legally; fabricated/cross/stale/fenced/repeated neutral candidates preserve state/counts. |
| Proof freshness across migration phase | OriginStateClosure-2 State-Closure-P2-1 residual, retaining OriginStateClosure-1 State-Closure-P2-1 | Bounded F8 residual; accepted and held. A proof from DRAINING is accepted after the same attempt becomes MIGRATING. | Proof binds exact current phase/serial and requested successor where applicable; stale prior-phase proof refuses mutation-free; new exact phase proof reopens once; replay/cross-attempt/wrong successor refuses with counts, queues, binding and epoch unchanged. |

The fresh full closure tables mark F8 closed for their narrower tested
same-phase/cross-attempt vectors. They did not attack the originating reviewer's
same-attempt cross-phase counterexample. That concrete NO-GO, independently
reproduced by the manager, remains binding; an adjacent successful vector does
not supersede it. The initial 18 IDs and all correction1 13 IDs remain regression
obligations, including expanded revocation. Their passing original cases do
not erase the five current defects.

The Code report abbreviates three changed test filenames. The exact current
manifest paths are test_admission_contracts.py, test_generation_contracts.py,
and test_lifetime_contracts.py, alongside test_worker_authority.py. Its report
is preserved unedited; this locating note grants no new write scope.

## Manager verification and independent corroboration

The manager reran focused97/full200/product5 on each Python 3.11–3.14 after
restart, without filtering inherited SQLite ResourceWarnings. AST25 and the
633-file owned/protected inventory matched. All current/guard/input hashes and
historical archived manifests passed. The final current manifest again verified
71/71 after all reports and inline probes. Source bytes did not change.

RestartVerification records independently reproduced false delivery progress
and stale-phase proof acceptance. Additional read-only fixture probes also
reproduced the reported participant and worker failures:

```text
preactivation_handle_acquired acquired 1
close closed members 2
migration_refused deadline_exceeded count 0 required 2 acked 1
effect_failed running 1
later_effect_authorized ['later-effect'] running
worker_result_transfer_refused lease_owner_conflict
no_batch_completion 0 0
```

The last line observes that completing a refresh without a batch leaves
producedThrough at zero, with global count zero. These probes drive real
reference transitions with existing fixture functions; private fields are read
only for observation, not overwritten to manufacture a state. They corroborate
the independent findings rather than replacing reviewer closure.

## Recommendation and operator gate

Recommend a narrow worker-exit ownership redesign, not acceptance of this
candidate. Define the worker-to-runtime success transfer and worker-to-
containment failure/cancellation transfer before changing source. Carry the
four bounded roots into that same explicitly authorized successor effort,
preserving all prior frozen tuples and stop history. A new brief must define
its scope and gate; no authority is inferred merely by writing this recommendation.
Fresh independent dual review and retracing every original counterexample are
required before any acceptance.

The earlier accepted W1 architecture and composed W2 design remain accepted
at their own historical tuples. This stop concerns the new W1/A11 amendment,
not retroactive rejection or a production incident. PostgreSQL/backend, shared
planner/lowering, async runtime, activation, external capture, dependencies,
public API freeze and Git/GWZ operations remain unlaunched. Source writes stay
stopped pending the operator's decision.
