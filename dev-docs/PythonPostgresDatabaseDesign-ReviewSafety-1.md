# Python PostgreSQL Database Design: Safety Review 1

## Verdict

**NO-GO.** P2-1 and P2-2 remain open. Both are bounded interface-contract defects; neither requires replacing the accepted architecture.

I pre-commit to GO on a revision that resolves {P2-1, P2-2} as specified, provided the revised tuple preserves the other safety invariants checked here.

## Object and Evidence

- Repository: `garns` in workspace `garns-wz`.
- Required and observed HEAD: `b2b8b158b76f0fe6e07eb5f009d6397bb653689b`.
- Controlling draft: `dev-docs/PythonPostgresDatabaseDesign.md` at that commit.
- Companion object: `dev-docs/PythonPostgresApiWalkthrough.md` at that commit.
- Axis: Safety; independent, adversarial, read-only design review.

At START and END, including renewed verification after the formatting reminder:
- `git rev-parse HEAD` returned the required commit.
- `shasum -a 256 -c dev-docs/PythonPostgresDatabaseDesign-Inputs.sha256` passed all 18 entries.

Both target documents were read through `git show` at the required commit. Every manifest entry was read as working-tree authority, including the accepted W2 base/overlay composition, acceptance records, ADRs and backend protocols. Historical draft headers were interpreted only through their applicable acceptance records.

Member `AGENTS.md` and workspace `AGENTS_GWZ.md` were read. The review-loop skill was subsequently located at the operator-specified location and read in full. The previously reported skill-availability limitation is resolved; no substantive findings or verdict changed.

No files, Git state, databases or services were modified. No tests, builds or network operations were performed. No other current-round review or prompt was accessed.

All source references below are relative to the `garns` repository root. Target-document line numbers refer to the pinned commit.

## Findings

### P2-1: Indeterminate Migration Has No Defined Recovery Surface

**Root classification:** Bounded interface/lifecycle contract omission.

**Location:** `dev-docs/PythonPostgresDatabaseDesign.md`, lines 62–66 and 227–234; `dev-docs/PythonPostgresApiWalkthrough.md`, lines 66–76. Controlling recovery invariant: `dev-docs/W2-AdmissionLifetimeRedesign.md`, §8.2; `docs/adr/A16-admission-lifetime.md`, migration-phase recovery contract.

**Violated invariant:** A migration that may have begun effects must retain the deployment fence until authoritative, request-bound recovery establishes the exact successor binding or full rollback/no-effect. The public migration lifecycle needs a reachable recovery half, not merely an execution verb.

**Reproduction/state sequence:**

1. A deployment is active at generation G.
2. `provisioner.migrate(request, context=context)` drains G and begins its classified migration.
3. Cancellation or acknowledgement loss occurs after effects may have begun.
4. The inherited contract requires `MIGRATION_INDETERMINATE`; ordinary old-generation execution and next-generation admission refuse.
5. The proposed Provisioner exposes only `inspect`, `ship`, `migrate` and `aclose`. None is assigned request-bound migration recovery semantics.
6. `runtime.reconcile(identity, ...)` promises transaction commit knowledge, not migration-phase settlement or generation publication. Even a committed migration transaction row does not itself settle the coordinator's exact attempt and successor binding. Metadata-only migration additionally admits no data publication.
7. Reinvoking `migrate` is not defined as recovery and independent migration-node retry is prohibited. Closing retains obligations rather than resolving them.

**Impact:** A permitted migration fault reaches a deployment-wide fenced state for which the proposed interface supplies no defined recovery operation. The operator must invent an unspecified route or bypass the boundary. This is a recovery completeness defect, not a request to implement the backend now.

**Required correction:** Define a privileged migration-recovery operation, or explicitly assign that role to an existing verb. Specify its request/attempt identity, trusted authorization, retained ownership across close/restart, admission while ordinary execution is fenced, and typed outcomes. It must distinguish authoritative successor success, full rollback/no-effect and still-indeterminate knowledge; absence or inspection alone must not reopen a generation.

Update the walkthrough to show this recovery path. Its instruction to request rollback before commit must also identify a callable mechanism when the migration is an opaque awaited operation.

**Closure/regression:** Add design vectors for metadata-only and accounted migrations interrupted before effects, after effects and after durable publication but before acknowledgement. From a fresh privileged recovery session, trace the declared operation to the exact legal coordinator outcome. Wrong request, stale attempt, missing evidence and ordinary runtime reconciliation must not clear the fence or repeat effects.

### P2-2: Whole-Transaction Deadline Has No Materialized Default or Lifetime Boundary

**Root classification:** Bounded configuration/ownership contract omission.

**Location:** `dev-docs/PythonPostgresDatabaseDesign.md`, lines 57–59 and 81–89; `dev-docs/PythonPostgresApiWalkthrough.md`, lines 22–25 and 34–41. Controlling configuration requirement: `docs/adr/A9-configuration.md`, documented finite timeout defaults.

**Violated invariant:** The absolute deadline that bounds a transaction must be materialized from a documented finite default and shared across its lifetime. Per-phase limits cannot substitute for that bound.

**Reproduction/state sequence:**

1. Open with exactly the documented default host configuration.
2. Begin an explicit transaction and perform a mutation that holds a conflicting row lock.
3. Continue issuing mutations that each finish within the 30-second statement limit, with caller waits between them.
4. The text does not specify an overall operation timeout value, its configuration field or derivation, or whether “operation” means the transaction lifetime versus each `begin`/`mutate`/`commit` invocation.
5. A per-invocation interpretation can give every call a finite absolute deadline while continually renewing the effective transaction lifetime. Another implementation can select a transaction-wide deadline at begin. The proposed contract does not select between them.

**Impact:** The documented defaults do not determine when an explicit transaction expires. A transaction can retain locks and ownership across arbitrarily many individually bounded calls under one plausible interpretation, blocking peers and repeatedly defeating migration drain. Implementations can also disagree about late commit eligibility.

The defect is not that the text explicitly allows an infinite timeout; it leaves the required aggregate bound and its ownership boundary undefined.

**Required correction:** Name the overall timeout policy and give its finite default or deterministic derivation. Define the deadline's start point and scope for explicit transactions, reads and migrations. For transactions, state whether acquisition and caller idle time count, and require the same absolute deadline through every mutation and commit, without renewal. Specify expiry behavior using the inherited containment and commit-knowledge rules; cleanup retains its separate budget.

**Closure/regression:** Add a default-configuration timeline spanning acquire, multiple mutations, caller idle time and commit. Show that individually successful phases cannot extend the transaction deadline. Include expiry before commit request and after commit request, proving respectively no new commit authorization and retained indeterminate knowledge until authoritative resolution.

## Invariant Analysis

| Attack area | Result |
|---|---|
| Task ownership and async escape | Child-task, concurrent and nested transaction use refuse. Public driver/verifier escape is prohibited; accepted lease ownership remains controlling. |
| Cancellation and close truth | Cancellation does not imply rollback or quiescence. NONQUIESCENT and UNRESOLVED retain distinct obligations; shutdown cannot delete reconciliation ownership. |
| Retries and idempotency | Only known-aborted serialization/deadlock failures qualify. Same identity/digest returns the original outcome; uncertain commit and missing rows cannot authorize retry. Callback payload encoding is explicitly gated. |
| Migration and generation admission | Deployment-wide drain, accepted barriers and atomic publication block stale-generation effects. Recovery interface incompleteness is P2-1. |
| Roles, namespace and induced effects | Separate privilege custody, qualified identifiers, session validation and unsupported-role/RLS refusal constrain bypasses. Unaccountable cascades refuse before effect. |
| JSONB fidelity | Exact parsing, duplicate-key rejection, JSON null versus SQL NULL, canonical expansion checks and server numeric-range rejection prohibit the tested fidelity failures. |
| Limits | JSON and inherited plan limits constrain parsing/assembly. The transaction-wide deadline ambiguity is P2-2. |
| Cross-generation and capability paths | Binding-v2 changes participate in storage identity; legacy versions are not silently upgraded. Accepted lifetime activation and mixed-path refusal remain controlling. |
| Deferred outcomes | No finding demands Rust, backend implementation, external capture or application-specific schema work. Findings concern interface shape and defaults now. |

These conclusions are design-level only. They do not establish real async execution, database durability, crash recovery, privilege enforcement or PostgreSQL support.

## Final Assessment

The tuple remained unchanged throughout review. No active corruption or credential exposure was demonstrated. Two concrete lifecycle/configuration gaps prevent approval of the proposed complete surface: migration recovery is unnamed, and the aggregate transaction deadline is undefined. Resolve P2-1 and P2-2 without weakening the inherited fail-closed contracts.
