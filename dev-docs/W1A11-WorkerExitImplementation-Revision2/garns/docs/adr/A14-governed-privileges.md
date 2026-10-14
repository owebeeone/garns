# A14 — Governed privilege and effect boundary

**Status: PROPOSED FOR REVIEW.** Depend on A11--A13. Govern-only applies to
every runtime instance. Supported application credentials cannot perform raw
bound-table DML or schema changes outside Garns' trusted host path. Runtime and
migration roles are separate; credential custody and host trust are operational
requirements. Garns does not claim protection from an administrator or a
compromised trusted host.

At open/borrow and before schema work, inspect current role, ownership, grants,
RLS policies/force status, inheritance and required function privileges.
Supported governed mutations must have a deterministic authorization path;
unsupported RLS/role states refuse before effect. `TRUNCATE`, unmanaged DML,
replication-role bypass and arbitrary trigger installation are not governed
operations. Garns schema operations cover every instance and classify all
induced cascades/triggers/conversions under A12 atomically or refuse.

External-writer matrices and capture tamper controls are deferred with A5; no
capture seam is implied. Closure: W4 role/RLS/induced-effect matrix and W7
deployment audit documentation.
