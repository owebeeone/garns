COMPLETE — W1 architecture draft is ready for manager filing and independent review.

Draft tuple aggregate SHA-256:

`5e04e8ece03d3a98d0bef293b3140a74c86cf967ff63fedc2a19359973d05bed`

Computed from sorted SHA-256 output for all 22 files under:

- `docs/adr/**` — ADR index plus A1–A15
- `src/garns/backends/contracts/**` — typed values, protocols and state helpers
- `tests/contracts/**` — pure contract/reference-model tests

Key decisions:

- A1: Psycopg 3 native async connection plus `psycopg_pool`; current upstream documentation covers Garns’ Python and PostgreSQL ranges.
- A2–A3: driver-neutral plans/results and async-only pool, connection, transaction and subscription protocols. No shared SQL or second expression IR.
- A4: revisions are assigned through per-scope durable locked publication, atomically with transaction identity and ledger effects—not by pre-commit sequence.
- A5: external capture is explicitly deferred and refuses before effect; no speculative capture seam.
- A6: every delivered row state is labeled with its actual consistent-snapshot high-water cursor. Later state cannot masquerade as an earlier revision; unavailable continuity returns typed refetch.
- A7: serializable whole-transaction retry, qualified durable identity and known-aborted/known-committed/indeterminate grammar. Cancellation or temporary absence does not prove rollback.
- A8: supported SQLite >=3.35 with JSON1, isolated behind serialized connection-owning workers.
- A9: typed configuration precedence, finite deadlines and redaction.
- A10: executable digest-pinned, per-run isolated PostgreSQL 15–18 container matrix plan; no server execution claimed.
- A11: immutable, runtime-local, request-owned trusted context with explicit expiry/invalidation and reconciliation limits.
- A12: metadata-only, backfill and DDL/cascade migrations are exhaustively classified; data effects must be atomically represented or refused.
- A13: fully qualified authored PostgreSQL namespace and borrow/release sanitation.
- A14: governed-only restrictions apply to every runtime instance; runtime/migration roles and induced effects are fail-closed.
- A15: durable retained floors, consumer leases and crash-safe compaction with typed cursor expiry.

Verification:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="${LARK_ROOT}:src" \
  /opt/homebrew/bin/python3.13 -B -m unittest discover -s tests/contracts -t .
```

25 tests passed.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="${LARK_ROOT}:src" \
  /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .
```

25 tests passed.

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="${LARK_ROOT}:src" \
  /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests -t .
```

128 tests passed: 25 W1 contract tests plus 103 inherited tests. Existing unclosed-SQLite `ResourceWarning`s recurred.

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -B tools/check_product.py
```

All five product checks passed. The inherited evidence manifest verified all five entries. Grammar SHA-256 remains:

`3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`

Limitations and unresolved review items:

- These are pure declaration/reference-model tests, not event-loop responsiveness or database evidence.
- No PostgreSQL service, migration, concurrency or fault-cut test ran.
- Python 3.11 and 3.12 interpreters were unavailable locally; 3.13 and 3.14 were exercised.
- W2 must freeze the exhaustive relational node algebra.
- W3 Surface review must select public names.
- W4 must pin exact compatible driver versions and execute PostgreSQL 15–18.
- All ADRs remain **PROPOSED FOR REVIEW**, not self-accepted.

Recommended next gate: manager pins the exact 22-file tuple and dispatches peer-blind Code and State reviews. No W2 launch before same-tuple GO/GO and manager acceptance.
