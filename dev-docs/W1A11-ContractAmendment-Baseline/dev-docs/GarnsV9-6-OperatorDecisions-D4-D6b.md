# Garns v9-6 operator decisions for SQLite and PostgreSQL support

**Status:** D4 and D6b binding/closed; D5 open  
**Decision date:** 2026-10-03  
**Authority:** operator  
**Recorded by:** manager

This record closes the SQLite support tier and PostgreSQL version range for
W1. These are implementation requirements, not claims that W0 already
implements PostgreSQL or the async runtime.

## Governing reviewed documents

This record adds decisions without changing the accepted, hash-pinned plan
or its provider-neutral seam amendment.

| Document | SHA-256 |
|---|---|
| `GarnsV9-6-PostgresAsyncImplementationPlan.md` | `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512` |
| `GarnsV9-6-ProviderNeutralSeamAmendment.md` | `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01` |

`GarnsV9-6-OperatorDecisions-D6a-D7-D8.md` remains binding and unchanged.
Its historical statement that D4 and D6b are open is superseded by this
record. D5 remains open.

## D4 SQLite support tier

**Decision:** SQLite is a supported secondary runtime, not merely a test or
development backend. PostgreSQL remains the primary production backend.

- SQLite must implement the same public async-facing runtime contract.
  Synchronous SQLite I/O must not run on the application event-loop thread.
- A8 must select and verify the non-blocking adapter mechanism. Test-only
  status is no longer an admissible A8 outcome.
- Support applies to an explicitly documented capability subset. Shared
  semantics must agree across backends; unsupported capabilities must refuse
  explicitly rather than silently degrade.
- SQLite needs release tests, lifecycle and cancellation evidence, and user
  documentation. PostgreSQL-only capabilities do not imply SQLite support.
- The SQLite version range and exact capability matrix remain W1 work;
  this support-tier decision does not invent either.

## D6b PostgreSQL support range

**Decision:** Support PostgreSQL 15, 16, 17, 18 and subsequent stable major
versions. The declared minimum is PostgreSQL 15, with no fixed upper bound.

- The initial real-server release matrix must include majors 15, 16, 17 and
  18, using current maintenance releases for each major.
- Subsequent stable majors must be added to the release matrix and verified
  before compatibility with them is claimed. Forward support is a maintenance
  commitment, not evidence that an unreleased or untested server works.
- A1 must select a driver compatible with this range. A10 must provision the
  matrix; W4–W7 must produce real-server execution and recovery evidence.
- Version-specific capabilities must be explicit and tested. Newer server
  features cannot silently raise the baseline above PostgreSQL 15.
- Missing local servers are provisioning work, not authority to omit a major
  from the claimed support matrix.

## Remaining capture decision

D5 still requires an operator decision naming one first W6 capture branch.
The plan recommends a trigger-maintained durable change table with
notifications used only as wakeups. Logical decoding remains an alternative;
neither branch is selected by this record.

W1 must still accept A1–A15 and close D5 before handing off to W2. Closing
D4 and D6b does not accept the adapter, driver, capture or revision protocols.
