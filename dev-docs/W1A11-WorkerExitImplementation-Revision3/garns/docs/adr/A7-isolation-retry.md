# A7 — Isolation, retry and commit knowledge

**Status: PROPOSED FOR REVIEW.** Default governed writes are serializable on
PostgreSQL and serialized transactions on SQLite. The runtime, never a driver
callback, owns retry of the **entire** transaction function. It retries only
serialization/deadlock failures known aborted, before the configured attempt
and deadline bounds, with the same qualified client transaction identity and
an explicitly retry-safe/idempotent operation. Otherwise return typed retry or
terminal failure.

Terminal database knowledge grammar is `KNOWN_ABORTED`, `KNOWN_COMMITTED` or
`INDETERMINATE`. A closed phase/evidence grammar separates queued, statement,
writes-applied, rollback-requested and commit-requested from authoritative
not-started, rollback-confirmed or durable abort evidence. Cancellation timing
is never database evidence. Failed, timed-out or acknowledgement-lost rollback
remains indeterminate. Cancellation or connection loss after commit request is
indeterminate until A4 reconciliation.
The complete phase/evidence Cartesian relation is closed in the contract:
not-started pairs only with queued, rollback-confirmed only with
rollback-requested, and commit-requested accepts only unresolved evidence.
Incompatible pairs refuse as invalid state; durable abort/commit evidence enters
only through identity-bound reconciliation.
Absence of a durable row is not abort while the original operation may still
succeed. Expiry can stop new effects but cannot authorize retry, rollback, or a
new transaction; known-commit reconciliation may perform only idempotent
cleanup already authorized by the original context.

Closure: W3/W4 fault-cut before/during/after commit and W5 concurrency tests.
