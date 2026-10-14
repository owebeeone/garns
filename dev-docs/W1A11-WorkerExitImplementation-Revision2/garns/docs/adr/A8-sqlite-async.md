# A8 — Supported SQLite async adapter

**Status: PROPOSED FOR REVIEW.** Depend on A2, A3, A7. SQLite is a supported
secondary runtime. One dedicated worker thread owns each SQLite connection and
executes a serialized command queue; application-loop coroutines only enqueue
and await results. No synchronous database call runs on the event-loop thread.

Cancellation removes queued work when it has not begun. Every begun command is
inside an explicitly controlled transaction. Interruption and rollback are
requested; reuse requires confirmed quiescence. Shutdown atomically closes a
commit-authorization fence before waiting: work that had not requested commit
cannot request it after the fence even if its blocked thread later resumes. A
commit already requested remains durably reconcilable under A7. Pre-commit work
may leave containment only with matching authoritative abort evidence. Once
commit is requested, only a matching terminal `KNOWN_COMMITTED` or
`KNOWN_ABORTED` outcome clears the fence; `INDETERMINATE`, acknowledgement loss,
wrong transaction identity or wrong revision scope leaves it unresolved. The
terminal outcome remains recorded so repeated identical resolution is
idempotent and a conflicting resolution refuses.

Python threads cannot be killed. If the worker misses the deadline, close
returns typed `NONQUIESCENT`, retains worker/connection containment, and does
not report terminal closure. That state carries zero or more still-unresolved
transaction identities: worker quiescence and transaction knowledge are
independent. A quiescent worker returns `UNRESOLVED` when any begun identity
lacks a terminal outcome, and `CLOSED` only when none does. Final transaction
outcomes are never relabeled unresolved merely because a worker is still
running. Pooling is bounded worker ownership, not cross-thread sharing.

A qualified transaction identity is admitted as new worker work exactly once.
Admission refuses while that identity is active and after it is terminal;
publication-level idempotency may return a cached result but never authorizes a
fresh worker command. Identities with equal client components in different
qualified scopes remain distinct.

Supported SQLite is >=3.35 with JSON1 enabled: the inherited lowering uses
window functions and `json_each`, and inherited supported migration lowering
uses `ALTER TABLE DROP COLUMN` introduced in 3.35. Open-time capability probes
refuse older or JSON-disabled libraries before effects. The initial observed
CPython 3.13/3.14 environment supplies SQLite 3.51.2; that observation is not a
release matrix. W3 tests the oldest admitted 3.35 line plus the current bundled
SQLite, and W7 renews the range.

Alternatives rejected: `async def` over direct sqlite3 calls and test-only
status. An external adapter dependency is unnecessary initially; W3 may propose
one only through review. Closure: W3 responsiveness, ownership, cancellation,
shutdown and release evidence across supported SQLite versions.
