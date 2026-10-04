# A15 — Replay retention and compaction

**Status: PROPOSED FOR REVIEW.** Depend on A4, A6, A12. Per qualified scope and
generation, durable consumer checkpoints and active snapshot leases define the
minimum protected revision. A single lease-elected compactor computes a
candidate floor, atomically advances the durable retained floor, then deletes
only ledger/revision payload strictly below it in idempotent bounded chunks.
Crash before floor advance deletes nothing; crash after it may leave extra old
rows but cannot make the advertised floor lie.

Default retention is no automatic compaction until an operator configures both
age/size policy and resource bounds; this is bounded operationally by explicit
storage monitoring, not an infinite correctness promise. A cursor at/above the
floor replays; below it returns `RefetchRequired(CURSOR_EXPIRED, floor)` and
uses A6's snapshot handshake. Generation mismatch also refetches; no cursor is
silently translated. Consumer expiry removes protection only after its finite
lease; expiry grants no mutation or reconciliation authority.

Closure: W5 fast/slow consumers, crash cuts and compaction races; W7 documents
capacity defaults and monitoring.
