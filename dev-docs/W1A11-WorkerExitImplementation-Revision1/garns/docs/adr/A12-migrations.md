# A12 — Migration locks, generations and effects

**Status: PROPOSED FOR REVIEW.** Depend on A4, A7, A14. One qualified
deployment advisory lock with finite wait serializes migration. The migration
records expected previous generation/digests and atomically publishes the new
generation with its ledger/revision boundary. Runtime open and every borrowed
connection validate compatibility; mixed binaries outside an explicit window
refuse. Generation changes terminate stale replay with typed refetch/generation
mismatch before continuation.

Three exhaustive classes apply: (1) metadata-only success carries a proof
digest and proves no bound row,
observable value or retained result shape changes, then publishes a generation
transition, otherwise refuses; (2) DML/backfill atomically records every data
effect in the governed ledger/revision transaction, otherwise refuses before
effect; (3) DDL conversion, cascade or supported trigger-induced row change has
the same atomic accounting or refusal. “DDL” never means effects are invisible.

Success outcomes are coupled to the request. Metadata-only admits no data
publication. Backfill/DDL success requires nonempty typed effects, the exact
requested next binding, same scope/generation revision, transaction identity
`migration:<request-digest>` and matching payload digest. Refused and
indeterminate are distinct non-success outcomes and cannot assert accounting.

Online/mixed-version operations are unsupported unless a later reviewed class
defines both-reader compatibility. External pending capture is deferred.
Closure: W4 crash/lock/classification tests and real effect accounting; W5/W7
generation/replay boundary tests.
