# A13 — PostgreSQL namespace

**Status: PROPOSED FOR REVIEW.** Depend on A9. Catalog/database and schema are
authored or immutably deployment-bound. Every DDL, DML, inspection, ledger and
migration object uses separately quoted catalog-valid schema/object components;
no dotted string is accepted as one identifier. PostgreSQL cannot qualify a
table by database across a connection, so configured catalog must equal the
connected database.

`search_path` is pinned to `pg_catalog` plus an empty/private Garns schema as
needed, never used to locate bound objects. Functions/operators are schema-
qualified or selected from the audited `pg_catalog` set. Borrow validates
database, role, transaction idle, search path and session settings; release
resets all mutable state or discards. Temporary objects and caller session SQL
are outside the contract.

Closure: W4 duplicate-schema/metamorphic names and poisoned-session tests.
