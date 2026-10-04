# A6 — Subscription snapshot, buffering and replay

**Status: PROPOSED FOR REVIEW.** Depend on A4, A15. Opening, reconnect and
overflow refetch start one repeatable consistent read transaction: read the
durable high-water cursor `S`, evaluate rows in that same snapshot, register
interest before releasing the snapshot, then scan durable revisions after `S`.
Registration and the post-registration scan close every race; notifications
only reduce latency.

Every refresh similarly reads rows and durable high-water `H` in one snapshot.
The delivery says rows are state **at H**, triggered by earliest routed `R`,
and atomically advances through all revisions `(previous,H]`. It never labels
current rows as state at R when later commits are visible. Neutral refreshes
advance the internal cursor without emitting a batch. If a backend cannot
produce the exact `(rows,H)` pair, generation changes, or cursor is below the
retained floor, it returns typed `RefetchRequired`; it never silently drops.

Queue capacity is the question's authored `live bounded N` (subject only to a
stricter deployment ceiling). Full queue atomically marks overflow, stops
incremental delivery, and requires the same handshake. Duplicate wakeups and
revision ranges coalesce by cursor.

Closure: W5 tests commits at every snapshot/register/refresh boundary, rapid
commits, overflow, neutral movement and restart.
