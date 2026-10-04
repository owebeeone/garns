# W1/A11 admission-lifetime contract amendment — execution brief

**Status:** authorized narrow contract build; independent review required  
**Date:** 2026-10-04  
**Owner:** manager; one contract builder, two peer-blind reviewers

## Authority and limits

The operator's “go” authorizes the previously recommended narrow W1/A11
amendment: internal contracts, additive decision documentation and deterministic
reference tests. It does not authorize the actual W2 planner, SQL lowering,
async runtime, database adapters, live engine, provisioning, activation, public
API freeze, dependency installation, network access, Git landing or workspace
reconfiguration. External-write capture remains deferred. Use gpt-5.6-sol for
the builder and both reviewers. There is one convergent implementation, not
competing whole-product builds.

The accepted composed W2 design controls the amendment. This brief is an
execution boundary, not a competing architecture. If a design requirement
cannot be represented within this boundary, report the gap; do not silently
weaken it or implement an operational subsystem to hide the gap.

## Exact controlling inputs

All paths below are relative to the product root. Read parent AGENTS_GWZ.md,
product AGENTS.md, PRODUCT_LAYOUT.md and the accepted documents before acting.

| Input | SHA-256 |
|---|---|
| W1-ACCEPTANCE.md | 524175276f7de2fa44b11d0308aaef9d3ad7e1a869ab17cc0cd24b87dc60316d |
| W2-QueryPlanningDesign.md | 0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e |
| W2-AdmissionLifetimeRedesign.md | 01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26 |
| W2-AdmissionLifetimeRedesign-ACCEPTANCE.md | 9d5c76a86c14229d2f37023a61692f1fb845d4c75a30d1af6b9eb68c68910334 |
| W1A11-ContractAmendment-Baseline.sha256 | a11f6339a909bf5d04e20c6e5b2dc54bed2f1c0e7accfd49d78c172daac971cf |

The first four live under dev-docs/. The 120-file baseline is an immutable
mirrored archive in dev-docs/W1A11-ContractAmendment-Baseline/. Its aggregate
manifest verifies from the product root. Historical nested manifests verify
from inside that archive, where their original relative paths and bytes are
preserved. Authorized source edits necessarily supersede the live old W1/source
tuple: never rewrite its manifests, or claim they still describe amended live
source. Review the new current tuple separately. Historical acceptance is not
erased or retroactively broadened.

W1A11-ContractAmendment-ReadOnly.sha256 pins the unchanged baseline paths
outside the write allowlist. The manager owns it and the input manifest.

## Exclusive builder ownership

Existing writable paths (all other existing paths are read-only):

- src/garns/backends/contracts/semantic.py
- src/garns/backends/contracts/protocols.py
- src/garns/backends/contracts/values.py
- src/garns/backends/contracts/state.py
- src/garns/backends/contracts/authority.py
- src/garns/backends/contracts/model.py
- src/garns/backends/contracts/__init__.py
- tests/contracts/test_contracts.py
- docs/adr/README.md — additive A16 link/status explanation only

New writable paths:

- src/garns/backends/contracts/admission.py
- src/garns/backends/contracts/lifetime.py
- src/garns/backends/contracts/lifetime_reference.py
- src/garns/backends/contracts/worker_authority.py
- tests/contracts/test_result_roles.py
- tests/contracts/test_admission_contracts.py
- tests/contracts/test_lifetime_contracts.py
- tests/contracts/test_worker_authority.py
- tests/contracts/test_generation_contracts.py
- docs/adr/A16-admission-lifetime.md
- dev-docs/W1A11-ContractAmendment.md

No unlisted writes. Ask the manager before adding a path, even for cohesion.
Do not launch helpers. Use apply_patch. Keep responsibilities cohesive rather
than one giant model file; a file approaching 500 lines warrants a split check,
and above 1,000 requires an explicit documented exception. The manager owns
briefs, reports, review prompts, manifests, acceptance and checkpoint. Original
A1–A15 bytes and accepted W2 documents remain immutable. Product grammar,
unenforced, existing compiler/runtime, operation contracts and pyproject remain
unchanged. Existing W1 Code P3 wrong-method terminal diagnostic stays a W3
follow-up, not an opportunistic repair in this package.

## Required contract amendment

### M1 — lossless result roles

Add a closed, exact ResultField role: VISIBLE, STRUCTURAL_KEY or NESTED_OWNER,
preserving the independent key flag. Nested owners have the exact structured
NestedResult list marker, not a scalar surrogate; the child shape links exactly
once to its owner. Reserved $key aliases never become visible author fields.
Validate duplicate/orphan owners, role/type mismatches and reserved-name abuse.
Preserve all existing SemanticType dimensions. Implement contract round-trips
or equivalent lossless validation for all five accepted vectors: ordinary
collection, optional/windowed total, hidden grouped keys, distinct visible keys,
and rooted nested children. No assembler or SQL compiler is implemented here.

### M2 — admission and finite operation ownership

Introduce exact empty, sealed, non-copyable/non-serializable admitted handles
and operation leases. Private issuer records retain plans, binding, authority,
generation and ownership; caller handles contain no plan, claims or registry
back-reference. Separate reusable admission from each finite execution unit.
Define OperationIdentity, operation kinds, closed lease/admission states and
the verifier's acquire/guarded-step/owner-transfer/completion boundary from
accepted W2. Executable backend protocols take admitted handles/leases rather
than raw Plan. No raw-plan compatibility overload, caller-replaceable verifier,
or old handshake fallback remains in the amended contract fixtures.

The reference verifier must drive actual state and callback effects, including
wrong binding/runtime/owner, counterfeit handles, expired authority, duplicate
completion and revoked generations. Plan access is trusted lexically closed
consumption; no raw plan, root, plan-bearing wrapper or closure escapes the
guard. The contract must distinguish admission/provenance verification (future
W2 canonical resolver implementation) from reference fixture setup. Do not
invent production provenance or claim an opaque fixture proves recompilation.

### M3 — ownership, containment and close

Represent immutable resource ancestry and local OPEN/DRAINING/FENCED/CLOSED
separately from deployment generation state. Acquisition charges every owning
ancestor before queueing; owner transfer is compare-and-transfer, not charge
duplication. Close fences/drains only its descendants; unrelated peers stay
current. Parent close cannot forget a retained descendant. Cancellation/finally
is not quiescence. Contained, potentially resumable work retains charges until
authoritative terminal completion. Add retained read operation identities to
close outcomes separately from A7 unresolved transaction identities. Preserve
the existing legal NONQUIESCENT-with-zero-transactions state and commit truth.
One lease spans all finite work through publication, not just point validation.

### M4 — private worker authorization, not task impersonation

Public TrustedContext remains bound to its issuing task. Extend A11 with a
private empty command-authorization handle created only by valid dispatch on
that task. Its registry record binds original context, exact runtime/operation/
lease/command/worker/binding and finite effect ordinals. Worker checks use
issuer-owned live context, clock/epoch, exact ownership/fences and one-shot
ordinal consumption immediately before effect; they never transfer public
context ownership or trust copied claims. Revocation, invalidation, expiry,
wrong worker/command/runtime/generation and reuse refuse with zero new effects.
Already-begun effects remain contained; A7 truth is unchanged. Reference tests
use distinct task and worker identities and callback counters. No actual worker,
provider, cross-process authentication or lock/thread proof is claimed.

### M5 — generation, buffered delivery and activation prerequisites

Define the shared generation permit/coordinator and plan_admission_lifetime_v1
capability requirement, including refusal of legacy/missing handshake. Define
finite snapshot-registration, refresh and iterator-handoff units; idle
subscriptions have no immortal execution lease. Buffered envelopes carry
immutable provenance/cursors/rows but no plan/lease. Queue permit accounting
must represent refresh-to-buffer and dequeue-to-handoff ownership exchanges.

The reference model must exercise the accepted pre-zero queue drain barrier:
mark migration-invalidating, discard queued permits once, block/discard late
refresh enqueue, retain a dequeue winner's active handoff, then permit migration
effects only after the authoritative global count reaches zero. No-effect
reopen uses a new admission epoch and never resurrects invalid buffers; unknown
post-effect outcome remains MIGRATION_INDETERMINATE. Local close is not a
deployment-global retirement. Include two-participant reference schedules.

Represent one-time activation states and the required authoritative physical
legacy-access fence, ACTIVE_UNUSED no-ever-open proof, and irreversible ACTIVE
protocol epoch after first open. This package defines contracts/proof inputs
and deterministic state validation, not an operational coordinator, credentials,
database locks or activation tool. No reset/deactivation/protocol-retirement
escape is introduced. Actual PostgreSQL/SQLite cross-process proof remains a
later release gate. A reference callback asserting a proof is not real evidence.

## Documentation and verification

Write additive A16 and W1A11-ContractAmendment.md with an explicit supersession
map for A2/A3/A6/A8/A11/A12, required method/type inventory, boundaries,
reference-model evidence versus deferred production evidence, and test links.
Names remain provisional pending W3 Surface review. Do not self-accept.

Retain existing attack coverage; update obsolete bare-plan/nested-owner fixtures
to the new contract rather than deleting attacks. Cover malformed exact enum
members, identity replay, terminal idempotency/conflict, no-transaction read
close, ownership transfer, isolation of local close, authority between steps,
worker revocation/reuse, publication fencing, queue races and migration timeout.
Tests must run real model transitions/callbacks, not echo expected answers.

Use existing offline interpreters, PYTHONDONTWRITEBYTECODE=1 and -B. Cached
Lark 1.3.1 is at /Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb;
place src and this directory on PYTHONPATH. Do not accidentally use cached
Lark 0.7.8. Run focused contracts and full unittest discovery on each:

- /Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11
- /Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12
- /opt/homebrew/bin/python3.13
- /opt/homebrew/bin/python3.14

Commands: -B -m unittest discover -s tests/contracts -t . and
-B -m unittest discover -s tests -t .; also -B tools/check_product.py.
Do not filter inherited SQLite ResourceWarnings. Do not run tools/check.py in
the live tree: it writes the out-of-scope gate-report.json. The manager checks
inherited evidence hashes and records limits separately. Test passing is not
reviewer closure or backend support evidence.

Stop writing before reporting. Return complete path list, exact commands,
counts/results, implementation limits and any unmet obligations; no claims of
GO or closed findings. The manager reproduces gates and pins the complete
current contracts/tests/ADR tuple plus this brief, amendment and immutable
inputs before dispatching independent Code and State reviewers.

## Review and acceptance gate

Review-loop applies to this new contract-amendment object. Prior W1 and W2 stop
histories remain unchanged. Initial remediation count is zero; at most two
architectural correction rounds. All P0/P1/P2 findings block; P3 follow-ups are
explicit. One builder owns consolidated corrections. Reports are filed verbatim;
originating reviewers verify closure, with fresh independent reviews after
material interface changes. Public Surface review is still required at W3.

Accept only the exact frozen amendment tuple after GO/GO, verified ownership,
full Python 3.11–3.14 tests, product checks and preservation of the archived
accepted tuples. Acceptance means contracts/reference tests only. The next
planner/backend/runtime build requires a separate execution brief and authority.
