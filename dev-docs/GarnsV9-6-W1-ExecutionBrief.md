# Garns v9-6 W1 architecture execution brief

**Status:** launch-ready after recorded scope-review GO/GO  
**Date:** 2026-10-03  
**Owner:** manager  
**Delivery:** one architecture owner, then independent review

W1 defines implementation-ready contracts for the governed-write, async
runtime. It does not implement the PostgreSQL backend or public runtime, and
does not start W2. The operator has authorized moving to this next phase.

## Inputs and precedence

Read workspace/product instructions and these complete documents:

1. `GarnsV9-6-PostgresAsyncImplementationPlan.md` at SHA-256
   `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`.
2. `GarnsV9-6-ProviderNeutralSeamAmendment.md` at SHA-256
   `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01`
   and its acceptance synthesis.
3. `GarnsV9-6-OperatorDecisions-D6a-D7-D8.md` at SHA-256
   `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f`.
4. `GarnsV9-6-OperatorDecisions-D4-D6b.md` at SHA-256
   `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce`.
5. `GarnsV9-6-GovernedWritesScopeAmendment.md` at SHA-256
   `d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe`
   and `GarnsV9-6-GovernedWritesScopeAmendment-Acceptance.md`.
6. `W0-ACCEPTANCE.md`, `../docs/PRODUCT_LAYOUT.md`, existing compiler IR,
   storage bindings, lowering, engine/live semantics and inherited tests.

Historical documents stay unchanged. Later operator records control their
explicit choices; the accepted scope amendment controls external-capture
deferral. D1–D8 are closed for W1. No deferred external-capture implementation,
named authentication provider or speculative capture-interface freeze is needed.

## Exclusive write boundary

The W1 owner alone may write:

- `docs/adr/**`;
- `src/garns/backends/contracts/**`;
- `tests/contracts/**` for matching contract tests.

The manager owns this brief, review reports, acceptance and checkpoint records
in `dev-docs/`. The W1 owner returns its draft report for manager filing; it
does not edit manager documents. Other source, grammar, corpus, generated
evidence, dependency metadata and the v9-5 input are read-only.

Do not perform Git/GWZ mutations, installations, production database operations
or destructive cleanup. Official-document browsing and read-only environment
checks are allowed. If additional writable support tooling or service
provisioning is necessary, report the precise need to the manager rather than
silently expand ownership.

## Required draft package

Produce A1–A15 as concrete architecture decisions, all initially **proposed for
review**, with an ADR index, exact dependent packages, alternatives considered,
consequences, defaults and executable closure obligations. A5 records deferral;
A14 covers the governed privilege and effect-coverage boundary.

Include:

- A1: select native async PostgreSQL driver and pool using current primary
  documentation; account for Python >=3.11, PostgreSQL >=15, codecs, licensing,
  cancellation, connection reset and dependency/version strategy.
- A2/A3: driver-neutral plan/parameter/result boundary, backend capability
  model, async connection/runtime/transaction/subscription contracts, and
  stable error/refusal outcomes. Do not implement a second expression IR in
  W1 or leak existing SQLite SQL into the shared contract.
- A4/A6/A15: a concrete governed revision publication and snapshot/replay
  algorithm, including multi-instance ownership, commit-safe ordering,
  overflow/refetch, retained floors and compaction. A pre-commit sequence ID
  alone is not a cursor. Specify how each delivered state relates to its
  revision when subsequent commits occur before refresh.
- A7: isolation, whole-transaction retry ownership, idempotency and the
  known-aborted/known-committed/indeterminate outcome grammar. Absence of a
  durable transaction row is not by itself proof that an in-flight commit
  cannot still succeed. Define reconciliation permissions without turning
  expiry into authority for new effects.
- A8: supported non-blocking SQLite adapter, lifecycle and cancellation;
  a coroutine wrapping synchronous event-loop I/O is not sufficient.
- A9/A10/A12/A13/A14: configuration/defaults/redaction, executable isolated
  PostgreSQL provisioning strategy, versions 15–18 and subsequent stable
  majors, migration locks/generations, namespace qualification and sanitation,
  and supported governed database roles and induced effects.
- A11: concrete in-process context issuance/ownership/immutability/validity
  grammar; normalized claims only, no external token or cryptographic work,
  no authority from structural resemblance or caller overrides.
- A declared SQLite/PostgreSQL capability matrix grounded in inherited IR
  and semantic tests. It describes target requirements, not shipped evidence.
- Transaction, cancellation/reconciliation, subscription/replay and pool
  lifecycle state diagrams, with finite deadlines and terminal outcomes.

Contract source must be lightweight typed definitions, protocols and any pure
validation/state helpers needed to make the contract falsifiable. No driver
imports, runtime/backend implementations or source-path relocations. Public API
names/examples are provisional until the W3 user-facing freeze and its Surface
review; W1 freezes dependency and lifecycle contracts, not an unreviewed public
API naming scheme.

## Verification and handoff

Matching tests must cover async protocol shape, capability refusal, qualified
identities, immutable contract values, state/outcome legality, cancellation
not implying rollback, transaction ownership and the required recovery and
snapshot/replay counterexamples at the pure contract level. Distinguish
reference-model tests from real database proofs reserved for W3–W5/W7.

Run focused contract tests and the inherited unit suite using existing
interpreters/dependencies, without bytecode writes. Preserve W0's grammar and
generated bytes. Report exact commands, counts and any limitations. Do not
claim event-loop responsiveness, PostgreSQL execution or a clean committed tree
from declaration tests.

Local read-only checks found PostgreSQL 17.9 tools and a responding Docker
engine. That is provisioning feasibility, not proof of a provisioned four-major
server matrix. A10 must name the isolation, readiness, ownership, credentials,
cleanup and reproducibility strategy; missing evidence must remain explicit.

Return a complete draft report with file inventory, A1–A15 decisions, test
results, deferred outcomes, unresolved issues and recommended next gate. The
manager pins the exact file tuple and dispatches independent Code and State
reviews under the review-loop skill. No W2 builder launches before same-tuple
GO/GO and a manager acceptance record. Remediation is one consolidated patch
per round, with at most two architectural remediation rounds.
