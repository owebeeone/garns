# A10 — PostgreSQL service matrix

**Status: PROPOSED FOR REVIEW.** Depend on A1, A9, A13. No server test is
claimed by W1. W4 creates an executable container composition pinned by image
digest for current maintenance releases of majors 15, 16, 17 and 18. A later
stable major enters supported/verified status only after adding the same job.

Each test worker receives a unique random container/project name, database,
login and authored schema; credentials are generated per run and passed by
secret/environment injection. The harness waits on `pg_isready` and then a SQL
probe, records image/server/driver versions, applies no unlisted extension,
runs migrations/tests, terminates sessions, drops its database/role and removes
its owned containers/volumes. Labels plus a run UUID prove cleanup ownership;
cleanup never targets unlabeled resources. CI always starts empty; local reuse
is forbidden for release evidence. Parallel workers cannot share databases or
schemas. Failure preserves bounded logs with credentials redacted.

Reproducibility artifact: composition, digest lock, bootstrap SQL, readiness
probe and exact test command under `tools/postgres`/`tests/support/postgres`
(the admitted A10 sub-lane, not W1 ownership). Local PostgreSQL 17.9 tools and
a responsive Docker engine show feasibility only. Closure: W4 executes all four
majors; W7 renews against current maintenance/stable releases.
