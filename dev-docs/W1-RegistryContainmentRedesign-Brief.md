# Garns W1 registry and containment redesign brief

**Status:** operator-authorized redesign, not acceptance  
**Date:** 2026-10-03  
**Owner:** manager

The operator approved the recommended correction after the recorded W1 stop:
keep identity claims inside the runtime registry, preserve unresolved commits
during shutdown, then independently re-review before moving on. This is the
explicit redesign decision required by the review-loop cap, not a silent third
architecture remediation or permission to weaken the accepted trust contract.
The previous W1 object's two architecture rounds and NO-GO history remain.

## Baseline and controlling inputs

The stopped full W1 tuple has 26 files in `W1-MANIFEST-3.sha256`, SHA-256
`3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13`.
Its controlling builder report is `W1-DRAFT-3.md`, SHA-256
`6bd4e15a36204307fe4a8ea06b75eb9f3eb1a9bb2291988389450644f6552566`.
Every manifest entry matched before this redesign was authorized.

Read workspace/product instructions, `CurrentProgramCheckpoint.md`,
`W1-STOP.md`, complete final `W1-ReviewCode-3.md` and
`W1-ReviewState-3.md`, the W1 execution brief and all controlling accepted
plan/amendment/operator records it names. Existing A1–A15 and retained compiler
semantics remain controlling. External capture, cryptographic/provider
integration, W2 algebra, actual backend/worker/runtime implementation, public
API freeze and database proofs remain deferred.

## Exclusive correction boundary

The sole architecture owner may edit only:

- `src/garns/backends/contracts/authority.py`;
- `src/garns/backends/contracts/state.py`;
- `tests/contracts/test_contracts.py`;
- `docs/adr/A11-trusted-context.md`, `docs/adr/A8-sqlite-async.md` and
  `docs/adr/README.md`, only to describe this redesign.

Other owned W1 files and all historical manager records remain read-only.
Report any necessary ownership expansion before editing it. No Git/GWZ
mutations, installations, database/service operations, real backend or thread
implementation, grammar or dependency changes are authorized.

## Required redesign and closure

| Final finding | Disposition | Required design and regression |
|---|---|---|
| Code-3 P2-1, initial Code P2-5 | Accept; redesign representation without weakening opacity | Caller-held context is an identity-only handle with no claim fields, issuer/registry back-reference, serialization payload or diagnostic route to claims. Issuer-owned registry stores a detached normalized claim snapshot and genuine task ownership, indexed by exact live handle identity. Validation retrieves claims only from trusted registry state. |
| State-3 P2-1, initial State P2-7 | Accept; enforce existing containment design | Commit-requested identities cannot disappear through `finish_without_commit`. Final resolution consumes an identity-matching known-committed/known-aborted outcome; indeterminate stays contained. Wrong identity or wrong-scope revision refuses without changing containment. |

Context tests seed canaries in every identity/scope/capability/validity field.
Ordinary attribute access, instance slots, dataclass helpers, copy/deepcopy,
repr/diagnostic output and serialization/reduction protocols on every
handle-reachable value must not reveal claims or create authority. A distinct
lookalike, reconstruction or context from another issuer must still refuse.
Re-running an initializer, if exposed, cannot rebind genuine issued authority.

The issuer is trusted host-owned setup; this is not a Python process sandbox
or a claim of secrecy against arbitrary code inspecting the entire host's
memory. The caller-held handle must neither contain nor lead through ordinary
instance attributes to claims. Runtime clock/epoch/task validation, capability
and scope barriers, invalidation, immutable claims and post-await delivery
validation must remain intact. Do not replace claims with a new exposed bag or
an inspectable issuer back-reference.

Worker tests cover no-commit authoritative abort completion, commit-requested
unsafe finish refusal, indeterminate retention, matching committed and aborted
resolution, mismatched qualified identities/revisions, acknowledgement loss
and repeated shutdown/reconciliation. Terminal close requires quiescence and
final outcome for every begun identity; inability to quiesce must not invent
abort or lose containment. These are pure reference-model proofs, not restart
durability or real worker evidence.

Preserve all existing regression tests. Run focused and full suites on existing
Python 3.11–3.14 with `-B`, `PYTHONDONTWRITEBYTECODE=1` and cached Lark; run
product/integrity checks. No downloads. Return full draft testimony including
exact changed inventory, commands/results, original counterexample attacks
and limitations, then stop source writes for manager pinning.

## Review and acceptance

The review-loop skill governs this explicitly authorized replacement design
object. Initial remediation count is zero for this bounded object, with the
ordinary maximum of two architecture remediation rounds; historical W1 counts
are not erased. Shared representation changes require fresh peer-blind Code
and State reviewers. Both inspect the exact complete integrated W1 manifest,
not only the six-file correction, and independently verify the two final
counterexamples and survival of previous closures.

Reports are filed verbatim; all P0/P1/P2 findings block. No finding is closed
by the builder, and no weakening of the controlling promises or new scope is
permitted. Manager acceptance requires GO/GO on one exact tuple, with explicit
replacement of the stopped W1 tuple. Public Surface review remains W3 work.
No W2 builder launches under this authorization.
