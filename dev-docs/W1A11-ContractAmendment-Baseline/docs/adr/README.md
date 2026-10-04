# Garns v9-6 W1 architecture decisions

**Status: PROPOSED FOR REVIEW.** None of A1--A15 is self-accepted. This tuple
freezes internal dependency and lifecycle shape only; all public names and
examples remain provisional pending W3 Surface review.

The decisions preserve the qualified compiler IR, explicit `WorldIR` storage
binding, shared query/question result planning, question-only footprints,
bounded live questions, and committed-only revision/ledger/batch laws. W2 owns
the actual relational node algebra; W1 deliberately defines no second
expression IR and exposes no SQLite SQL.

| ADR | Decision | Direct dependants |
|---|---|---|
| [A1](A1-postgresql-driver.md) | Psycopg 3 async + `psycopg_pool` | W3, W4 |
| [A2](A2-backend-contract.md) | driver-neutral async backend boundary | W2, W4 |
| [A3](A3-async-lifecycle.md) | async-only lifecycle and ownership | W3, W5 |
| [A4](A4-revision-publication.md) | commit-ordered scoped publication | W4, W5 |
| [A5](A5-external-capture.md) | external capture deferred | W7 |
| [A6](A6-subscription-snapshot.md) | exact snapshot watermark and bounded replay | W3, W5 |
| [A7](A7-isolation-retry.md) | whole-transaction retry and three-way commit | W3--W5 |
| [A8](A8-sqlite-async.md) | serialized worker + evidence-bound commit fence | W3, W7 |
| [A9](A9-configuration.md) | typed precedence, redaction and deadlines | W3, W4 |
| [A10](A10-postgresql-provisioning.md) | isolated 15--18 service matrix | W4--W7 |
| [A11](A11-trusted-context.md) | registry-only authority behind empty identity handle | W3, W7 |
| [A12](A12-migrations.md) | locks, generations, effect accounting | W4, W7 |
| [A13](A13-namespace.md) | authored, fully qualified PostgreSQL namespace | W4, W7 |
| [A14](A14-governed-privileges.md) | governed role/effect boundary | W4, W7 |
| [A15](A15-retention.md) | retained floors and crash-safe compaction | W5, W7 |

## Target capability matrix

This is a requirement matrix, not shipped evidence. “Common” must execute with
equal semantic results; “refuse” means a typed pre-effect refusal.

| Capability | SQLite supported secondary | PostgreSQL primary |
|---|---:|---:|
| qualified static query / question initial result | common | common |
| question footprint routing and neutral suppression | common | common |
| governed atomic mutation + ledger + revision | common | common |
| async API / cancellation / reconciliation grammar | common | common |
| bounded live, replay, overflow/refetch | common | common |
| retained-floor compaction | explicit configured subset or refuse | required |
| migration metadata-only / accounted data effects | explicit classified subset | explicit classified subset |
| PostgreSQL catalog/schema, roles, RLS | refuse as not applicable | required |
| external-write capture | refuse: deferred | refuse: deferred |

No matrix cell is proven by these declarations. SQLite release evidence belongs
to W3/W7 and real PostgreSQL evidence to W4--W7.

## Defaults, alternatives and consequences

| ADR | Default | Principal rejected alternative | Main consequence |
|---|---|---|---|
| A1 | Psycopg async/pool, compatible minor pin | asyncpg; sync wrapper | two LGPL packages; libpq lifecycle must be tested |
| A2 | required capability-checked protocols | optional methods / portable SQL | W2 must add exhaustive plan algebra |
| A3 | explicit async resources, one owner | sync facade / implicit finalizers | callers close resources and handle typed cancellation |
| A4 | per-scope locked commit publication | pre-commit sequence | publication row is a write contention point |
| A5 | refuse external capture | speculative trigger/WAL seam | external writes invalidate live/history guarantees |
| A6 | bounded queue, coalesced exact watermark | current-row-as-old-revision / drop | overflow costs a refetch |
| A7 | serializable, bounded whole-function retry | statement retry | callers declare retry safety and handle indeterminate |
| A8 | one serialized worker per connection | loop-thread sqlite3 / test-only | bounded worker resources and interrupt cleanup |
| A9 | min pool 1, max 10, finite materialized deadlines | implicit/unbounded config | deployments must supply missing secrets and limits |
| A10 | fresh digest-pinned services per run | shared local cluster | slower CI, independently reproducible evidence |
| A11 | runtime-local immutable capability | claim-shaped dictionaries / provider SDK | trusted host owns authentication and renewal |
| A12 | offline serialized classified migration | implicit online mixed versions | unsupported evolution refuses before effect |
| A13 | full qualification, safe path | ambient `search_path` | more verbose SQL, deterministic binding |
| A14 | split runtime/migration roles, fail closed | same credential with unmanaged DML | operational credential custody is mandatory |
| A15 | no auto-compaction until bounded policy | silent cursor translation / eager deletion | storage grows until monitored policy is enabled |

## Lifecycle diagrams

```text
pool/runtime: NEW -> OPEN -> DRAINING -> CLOSED (quiescent, no pending identities)
                    |          |
                    +-> FAILED +-> NONQUIESCENT(ids may be empty) -> retain worker
                               +-> UNRESOLVED(ids nonempty) -> reconcile -> CLOSED

transaction: OWNED -> ACTIVE -> COMMIT_REQUESTED -> KNOWN_COMMITTED
                         |              |         -> INDETERMINATE -> RECONCILE
                         +-> ROLLBACK -> KNOWN_ABORTED                 |-> committed
                                                                 or |-> aborted
                                                                 or |-> unresolved

subscription: OPENING -> SNAPSHOT(cursor S) -> STREAMING(cursor >= S)
                                  ^                 |
                                  +-- REFETCH <-----+ overflow/expired/generation
                                      |-> STREAMING(new S) or terminal refusal

delivery: SUBSCRIPTION -> bind(context) -> AUTHORITY_BOUND_ITERATOR
                                    each next: validate -> await read -> validate -> return
                                    renew: close old -> bind new context

borrow: ACQUIRED -> ACTIVE -> QUIESCING -> SANITIZED -> RETURNED
                                      |              failure/timeout -> DISCARDED
```

All acquire, statement, commit, cleanup, migration-lock and shutdown edges have
finite `DeadlinePolicy` bounds. Cleanup is shielded only up to its cleanup
deadline. A nonquiescent PostgreSQL connection is discarded; a non-killable
SQLite worker returns typed `NONQUIESCENT`, with zero or more unresolved
identities, and remains contained and owned until quiescence. A quiescent
worker with pending transaction knowledge returns `UNRESOLVED`. Forced close
never claims a running thread was killed, relabels a final transaction
uncertain, or claims a pending transaction rolled back.
