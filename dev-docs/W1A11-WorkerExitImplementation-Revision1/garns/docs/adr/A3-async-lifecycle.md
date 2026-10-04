# A3 — Async runtime lifecycle

**Status: PROPOSED FOR REVIEW.** Depend on A2, A6, A7, A11. Database-facing
public work is async-only. Runtime, transaction and subscription resources are
explicitly opened and idempotently closed. The actual runtime task object
captured at creation owns a transaction handle and is compared by identity;
concurrent use, child-task retention and nesting refuse before effect. v9-6 has
no savepoint/nested transaction public contract.

Cancellation while queued has authoritative not-started evidence. During a
statement or after writes it requests bounded interruption and rollback, but
remains indeterminate unless rollback/abort is authoritatively confirmed.
After commit request it remains indeterminate unless durability is known.
Graceful close drains within its deadline. Failure to quiesce returns typed
unresolved identities and retains containment/reconciliation ownership; it
does not claim `CLOSED`, thread termination, or rollback.

Alternatives rejected: sync facade, implicit finalizers, shared transaction
handles. Closure: W3 Surface review chooses public names and proves ownership,
deadlines, cancellation and resource release with SQLite; W4 repeats against
PostgreSQL.
