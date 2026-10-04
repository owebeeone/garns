# A4 — Durable revision publication

**Status: PROPOSED FOR REVIEW.** Depend on A7, A12. Identity is
`(world, deployment, client_transaction_id)` and revision order is scoped to
that bound world/deployment and generation.

Each governed transaction writes its durable transaction row, all bound-data
effects, complete typed ledger entries, and one revision in the same database
transaction. A per-scope durable publication row is locked; the next revision
is assigned there immediately before commit. Thus revision order is serialized
publication/commit order, never request order or a sequence allocated before
commit. Rollback allocates no revision. Multi-instance publishers use the same
database lock and uniqueness constraints. A post-commit wakeup is only a hint;
routers scan durable revisions after their cursor.

The transaction row stores a canonical payload digest. Repeating the same
identity/digest returns its original revision without advancing; reusing the
identity for another payload refuses. Identity outcomes survive generation
changes and ledger compaction for reconciliation. Lost acknowledgement
reconciles by qualified transaction identity. A missing
row while commit can be in flight is `NOT_FOUND_NOT_FINAL`, not abort. Only a
durable committed row or authoritative abort/tombstone closes reconciliation.

Alternative rejected: ordinary sequences (allocation can oppose commit order).
Closure: W4 proves atomicity/uniqueness; W5 forces reverse-commit, rollback-gap,
restart and two-instance traces.
