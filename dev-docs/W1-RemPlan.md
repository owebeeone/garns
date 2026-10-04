# Garns W1 consolidated remediation plan

**Status:** accepted findings, one correction package authorized  
**Date:** 2026-10-03  
**Remediation round:** 1 of at most 2 architectural rounds  
**Owner:** manager

The initial pinned W1 draft received Code NO-GO (six P2) and State NO-GO
(seven P2). Reports are preserved verbatim. Both axes independently found
cancellation-as-abort and missing read/snapshot authority; that blind
convergence increases confidence in those roots. All findings are accepted.

## Finding dispositions and closure tests

| Finding | Disposition and correction | Required regression or closure |
|---|---|---|
| Code P2-1 | Accept: complete required governed mutation, schema inspection, migration lock/apply, generation and ledger/revision protocols with typed input/outcome and capability refusal. | Enumerate every operation, verify async I/O, and run both-backend conforming fakes which refuse unsupported calls before adapter invocation. |
| Code P2-2 | Accept: lossless immutable semantic type descriptors and named/owned nested result fields, faithfully mapped from inherited TypeRef. | Builtin/optional/list/nominal/closed-set/carrier/nested round trips and dimension-erasure mutants. |
| Code P2-3 | Accept: immutable plan-root boundary and qualified world/binding/generation origin, without designing the W2 expression algebra. | Mutable roots/payloads rejected or detached; wrong origin refuses before execution; cache identity distinguishes bindings. |
| Code P2-4 | Accept, same root as State P2-5: authority at open/acquire/execute/snapshot and other protected operations, with explicit privileged scope setup. | Missing/copied/expired/invalidated/wrong-owner/wrong-scope/insufficient-capability contexts refuse before adapter call; cross-request connection reuse fails. |
| Code P2-5 | Accept: context serialization/conversion/copy refuses or produces a strictly redacted non-authoritative diagnostic. | Pickle, copy/deepcopy, replace/reconstruction, dataclass conversion and output serializers cannot disclose canaries or mint authority. |
| Code P2-6 | Accept, same root as State P2-1: phase is separate from authoritative database knowledge. | Queued/during-statement/after-write/during-rollback/rollback-loss/timeout/pre/post-commit traces; only authoritative abort proves KNOWN_ABORTED. |
| State P2-1 | Accept: shared cancellation correction above. | Original unacknowledged rollback counterexample remains INDETERMINATE and connection is not reusable. |
| State P2-2 | Accept: qualified identity-to-revision publication with conflict detection. | Same identity/payload, including lost acknowledgement, advances once; conflicting payload refuses. Preserve reconciliation identity across generation/retention boundaries. |
| State P2-3 | Accept: host/runtime-owned genuine-instance provenance, not a copied token field. | copy/deepcopy/replace/reconstruction/serialization creates no independently valid capability; exact issued object alone validates. |
| State P2-4 | Accept: defensive normalization and validation of claims; retain no mutable caller-owned claims. | Mutate source sets/containers and hostile subclasses after issuance; normalized capabilities/scope/identity/validity remain stable; invalid values refuse. |
| State P2-5 | Accept: shared operation-authority correction above. | Conforming fake read and snapshot paths cannot execute without valid request authority at required barriers. |
| State P2-6 | Accept: recursive immutable parameter/result value algebra. | Mutating nested source list/dict/set/custom values cannot change any accepted snapshot/delivery; unsupported values refuse. |
| State P2-7 | Accept: SQLite worker shutdown fence and typed unresolved close outcome, retaining containment/reconciliation ownership. | Block before statement and commit, expire close deadline, then unblock: no newly authorized commit after fence; in-flight commit remains reconcilable, not falsely aborted/closed. |

## Correction boundary

The same sole W1 owner makes one consolidated patch across its existing
`docs/adr/**`, `src/garns/backends/contracts/**` and `tests/contracts/**`
ownership. Manager records and pinned historical inputs remain read-only.
No PostgreSQL driver/backend, SQLite worker implementation, grammar change,
external capture or provider integration is added. Pure reference/state
models and conforming fakes are allowed to make the architecture falsifiable.

As the model now covers different authority, value and state responsibilities,
the split-files skill recommends cohesive modules within the contract package
rather than accumulating unrelated definitions in one file. The builder owns
the precise boundaries; no concurrent writer or repository-wide move exists.

Keep all definitions PROPOSED FOR REVIEW. Rerun focused tests and the inherited
suite; existing Python 3.11/3.12 runtimes are available through
`uv python find --no-python-downloads`. Do not install dependencies or change
the reviewed product outside ownership.

## Re-review and limits

The original W1 manifest, draft and reports stay unchanged. The manager pins
a new manifest and draft report for the corrected object. Because this patch
changes shared protocols and the authority/shutdown architecture, the skill
requires fresh peer-blind Code and State reviewers in numbered round 2, not
mere continuation of old proofs. Prior reports and this merged plan are
legitimate shared inputs; current-round reports stay blind.

Every finding requires independent verification of its original counterexample
and a closure table. Builder self-assessment is not closure. No W2 handoff
occurs without same-tuple GO/GO and manager acceptance. One additional
architectural remediation round remains after this correction; a subsequent
third architectural remediation/root-cause escalation stops for an operator
redesign-or-accept decision rather than silently looping.
