# A1 — PostgreSQL driver and pool

**Status: PROPOSED FOR REVIEW.** Select Psycopg 3 `AsyncConnection` with the
separately packaged `psycopg_pool.AsyncConnectionPool`. Pin compatible minor
ranges in W4/release locking, test upgrades before widening, and use the local
C/system-libpq install for production policy; binary wheels are acceptable for
hermetic tests. Both projects are LGPL-3.0-only.

Current upstream documentation supports Python 3.10--3.15 and PostgreSQL
10--18, so Garns' Python >=3.11 and verified PostgreSQL 15--18 ranges fit. A
subsequent stable PostgreSQL major is **supported only after** Garns adds it to
the real-server matrix; “no upper bound” is a maintenance policy, not advance
verification. Register Garns codecs/configuration on every new connection and
validate them on borrow. Never expose Psycopg objects through A2.

Psycopg cancellation requests server cancellation but explicitly warns task
cancellation does not prove the operation did not complete. Garns therefore
keeps A7's indeterminate commit state. Pool `configure`, `check`, and `reset`
hooks establish namespace/codecs, validate, then sanitize; reset failure,
protocol activity, open transaction, deadline, or cancellation discards the
connection. Pool open/acquire/close use explicit finite deadlines.

Alternatives: asyncpg has native asyncio, rich codecs, reset and tested server
15--18 compatibility, but a PostgreSQL-specific API and Apache-2.0 license do
not outweigh Psycopg's libpq behavior and DB-API lineage here. psycopg2 and
thread-wrapped sync drivers fail the native-async requirement.

Closure: W4 pins versions, codec vectors, prepared-state policy, cancellation
fault cuts, reset/discard and 15--18 server execution; W7 tests the then-current
stable versions. Official sources (researched 2026-10-03):
[supported systems](https://www.psycopg.org/psycopg3/docs/basic/install.html),
[async cancellation](https://www.psycopg.org/psycopg3/docs/advanced/async.html),
[async pool API](https://www.psycopg.org/psycopg3/docs/api/pool.html),
[upstream license](https://github.com/psycopg/psycopg/blob/master/LICENSE.txt),
and [asyncpg comparison documentation](https://magicstack.github.io/asyncpg/current/).
