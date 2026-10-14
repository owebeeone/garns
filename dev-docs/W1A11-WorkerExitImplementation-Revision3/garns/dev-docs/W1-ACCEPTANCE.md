# Garns v9-6 architecture acceptance

**Status:** accepted at the exact 26-file manifest below after Code and State
reported GO; this accepts W1 architecture and pure contracts only.  
**Date:** 2026-10-03  
**Owner:** manager

The approved registry and shutdown redesign closes the two stopped-W1 defects
without weakening the in-process trust boundary. The manager accepts A1–A15,
the internal async backend contracts and their pure reference models at this
exact integrated tuple. PostgreSQL, a real async runtime and workers are not
implemented or accepted here. External-write capture remains deferred.

## Exact accepted files and testimony

The accepted object is every entry in
`W1-RegistryContainmentRedesign-MANIFEST-3.sha256`, SHA-256
`95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`.
The controlling builder report is
`W1-RegistryContainmentRedesign-DRAFT-3.md`, SHA-256
`458aeea7dd184a96af413d2550b6dffb54ced623a6a4cd406468e94f461c6128`.

Both final reports are preserved verbatim and judge the same accepted object:

- [Code GO](W1-RegistryContainmentRedesign-ReviewCode-3.md), SHA-256
  `a0d724fad47932e9430cfcc839a56bed7d8ea9eedc836d16aa61eeab0b97b37d`.
- [State GO](W1-RegistryContainmentRedesign-ReviewState-3.md), SHA-256
  `0eca04cec79cd59c4a543772f5b608a0ac21c054d9bb35cf7f356018ce0cb36c`.

No P0/P1/P2 remains open. Initial replacement findings also have separate
originating-reviewer closure testimony in
`W1-RegistryContainmentRedesign-OriginCodeClosure.md` and
`W1-RegistryContainmentRedesign-OriginStateClosure.md`. The last State P2 was
closed by its originating round-2 reviewer on the final tuple.

This additive manager record accepts the reviewed ADRs even though their
source headers still say PROPOSED FOR REVIEW. Those headers remain byte-exact
to the reviewed manifest; they do not override this acceptance. Public names
and API examples are still provisional until W3 and its Surface review.

## Accepted corrections and preserved decisions

Caller-held contexts are empty exact-instance identity handles. Detached
claims and genuine task ownership remain solely in the trusted runtime
registry. Ordinary handle attributes, copying and serialization cannot reveal
claims or create authority; arbitrary host-memory secrecy is not promised.

Commit-requested identities cannot disappear through pre-commit completion.
Matching terminal resolution is required; indeterminate knowledge retains the
identity. Duplicate active admission and terminal identity reuse refuse before
mutation. Invalid outcome knowledge and malformed cancellation/reconciliation
inputs refuse before manufacturing terminal truth.

Shutdown distinguishes quiescent close with no pending identities (CLOSED),
quiescent close awaiting transaction knowledge (UNRESOLVED), and a worker that
has not stopped (NONQUIESCENT, with zero or more pending identities). Final
transaction knowledge does not imply worker quiescence, or vice versa.

The frozen internal decisions include the Psycopg 3 async/pool direction,
driver-neutral backend contracts, supported secondary SQLite, governed-only
atomic effects and ledger/revision coupling, replay, migration, namespace,
roles, retention and in-process provider-neutral authority. These are binding
implementation requirements, not evidence that a driver or backend ships.
Python >=3.11 and PostgreSQL 15–18 plus later stable majors with verification
remain the accepted support direction. The grammar, query/question split,
standalone unenforced flag and authored physical bindings are unchanged.

## History and verification

The original W1 stop and its two architectural remediation rounds remain
historical facts in `W1-STOP.md`; that stopped tuple is not retroactively
accepted. The user explicitly authorized a replacement design in
`W1-RegistryContainmentRedesign-Brief.md`. That object used two consolidated
remediations: the first completed the close-state algebra; the second was
bounded recovery-input validation, not another architecture redesign. Final
reviewers found no new architectural root cause. This accepted replacement
supersedes the stopped tuple for downstream dependencies only.

Manager verification is filed in
[final verification](W1-RegistryContainmentRedesign-Verification-3.md).
All 148 full tests passed independently on each existing Python 3.11–3.14;
both reviewers reproduced 45 focused contract tests. All five product checks
and five inherited evidence entries passed. The complete manifest matched
after tests and at each review boundary. No warning filter was applied in the
final builder/manager runs; inherited SQLite ResourceWarnings remain recorded.

Review followed the accepted plan's SHA-pinned pre-initial-commit exception.
No clean Git checkpoint, Git landing, installation, database/service operation,
real worker behavior, restart proof or database fault-cut proof is claimed.
W0 and controlling plan/amendment/decision records remain unchanged.

## Nonblocking follow-up and next phase

Code P3-1 remains explicitly deferred to W3 reference-model integration:
after a known commit is retained, the terminal idempotency fast path can
accept the wrong finish_without_commit method call without changing truth.
W3 must enforce that method's known-abort precondition before the fast return,
test wrong-method refusal without mutating the committed record, preserve
repeated resolve idempotency, and obtain originating Code closure. This is a
diagnostic follow-up, not an open W1 correctness blocker or a separate package.

The next planned phase is W2: backend-neutral plan nodes, exhaustive visitors,
capability validation and SQLite lowering parity. W2 must consume this exact
accepted tuple and preserve inherited semantics. Preparing/launching that
builder is a separate next action; no W2 builder is launched by this acceptance.
W6/P6 external capture is deferred, not PASS, and is not a release dependency.
W3 Surface and final P12 implementation review remain mandatory.
