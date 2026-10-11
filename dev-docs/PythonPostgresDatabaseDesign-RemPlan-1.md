# Python PostgreSQL design remediation 1

**Status:** consolidated correction for independent re-review, not self-closure.
**Baseline:** b2b8b158b76f0fe6e07eb5f009d6397bb653689b.
**Architecture correction count:** 1 of 2.

| Axis / finding | Disposition | Closure vector |
|---|---|---|
| Consistency P2-1 | accept; closed binding-v2 document, version discriminator, codec/constraint/index vocabulary, digest and minimal example | section 4.1 plus binding vector; unknown/missing/version/collision failures must agree before effect |
| Consistency P2-2 | accept; complete mutation intent fixed before begin/effect, tagged atoms and retained payload format | omitted vs NULL vs JSON null, exact numeric bytes, mutation order and duplicate stamp independence |
| Consistency P2-3 | accept; operation_seconds=120 starts before acquire, includes transaction caller idle time, supervised expiry | section-3 t=0..130 trace; no renewal or false abort |
| Safety P2-1 | accept; privileged recover_migration with exact request/attempt, phase-bound backend evidence and retained fence | metadata/accounted pre-effect, post-effect and post-publication ack-loss traces; stale/missing evidence cannot clear fence |
| Safety P2-2 | merged with Consistency P2-3 | same default timeline and post-commit uncertainty trace |

Blind convergence: both axes independently found the missing total deadline.
The correction changes the proposed public transaction surface to accept a
complete batch. It does not change frozen source/ADRs. Therefore fresh reviewers
replace the initial pair and must retrace every prior finding on their axis.
No third reviewer runs concurrently; Surface is a separate later step.

No source, service, role, database or implementation changes were made. The
vector file computes canonical byte/digest examples only; it is not backend
proof. Unsupported exact-value result/artifact paths remain behind the explicit
additive-amendment gate, not a silent change to W2's accepted format.
