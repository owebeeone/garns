# W1/A11 amendment — consolidated remediation 1

**Status:** manager disposition; sole builder correction authorized  
**Date:** 2026-10-04  
**Object:** same narrow internal contract amendment; architecture remediation 1 of at most 2

## Exact evidence and verdict merge

Initial complete47 manifest SHA-256:
76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8.
Its exact files plus manifest are preserved under
W1A11-ContractAmendment-Revision1/. Verify the original manifest from inside
that directory after live corrections; do not rewrite it or demand its old
source hashes match amended live source.

Both initial peer-blind reports were filed verbatim:

- ReviewCode.md: NO-GO, 9 P2s; SHA-256
  7d65489d20a6261de6cfe09ff4d88e25adfc8351f6c94b35470f95229efd49dd.
- ReviewState.md: NO-GO, 8 P2s; SHA-256
  e36f4a7acbb75d7915aacf1e333f6c7a781e30d9a42c43efeeadd2bffed92789.
- ReviewState-Supplement.md: same initial tuple, NO-GO; expanded State P2-4
  revocation vector and one independent bounded State-Supp-P2-1; SHA-256
  062299ff3cca6d2c767b05ea3cb3b2f2bd75f7657a5aa188557dbe029257e879.

All filenames use the W1A11-ContractAmendment prefix under dev-docs/. The
supplement followed both completed independent reports, with no source change;
it is not a remediation round or rewritten initial testimony. It confirms the
manager's extra probes, not an unreviewed manager patch.

Accept all 18 blocking IDs for correction, consolidated into 13 root groups.
No dispute, waiver or claimed closure. Blind convergence covers parameters,
publication, buffer provenance, privileged authority and activation proof.
The same builder owns one consolidated patch. Reviewers classify multiple
roots as architectural, so remediation count becomes1 and fresh full dual
review is required. Prior W1/W2 accepted stop histories remain unchanged.

## Disposition and closure map

| Root | Every mapped finding ID | Required correction and closure test |
|---|---|---|
| R1 | Code P2-1 | Replace arbitrary Plan-taking callables with issuer-owned registered exact closed consumers and closed step products. Ordinary callables/property/global/cache/wrapper/closure attacks refuse before seeing Plan or running effects. Do not substitute a return-value walk for lexical containment. |
| R2 | Code P2-2; State P2-8 | Pin detached parameters once in the lease. Remove unbound duplicate execute/snapshot/subscribe parameters or compare them before any consumer; closed consumers use registry-owned values only. Substitution at every executable seam produces zero effects/publication and unchanged charges. |
| R3 | Code P2-3; State P2-4, including supplement | Implement closed step/lease ordering and one publication linearization point. Reject direct ACQUIRED publication, repetition, backward/post-publication work and alternate refresh enqueue bypass. Revalidate original authority, owner, admission/registry/coordinator epochs, binding/generation and local fences before visibility. Test revoke/expiry/invalidation/epoch/binding/fence changes, exact-once handoff and explicit graceful old-generation drain. Preserve containment/charges rather than erase uncertain work. |
| R4 | Code P2-4 | Admissions and leases bind coordinator admission epoch. No-effect reopen invalidates old handles AND old leases; only newly admitted units can execute/publish. Test old refusal/new success and unchanged invalid buffers. |
| R5 | Code P2-5; State P2-3 | Bind subscription registration, refresh result and buffer record to authoritative admitted identity, plan digest, parameters, generation, registration and cursor/advancement lineage. Compare every field at refresh-to-buffer and buffer-to-handoff exchange. Wrong/cross/stale/copied/already-delivered envelopes refuse before changing permit counts. Envelopes may contain no Plan, root or lease even through an identity wrapper. |
| R6 | Code P2-6 | Store exact command and worker authorization in the atomic queued-owner record; dispatch and dequeue bind the same tuple. Unrecorded/wrong commands and bypassing queue ownership never issue usable effects. Test both issuing-task dispatch and distinct worker consumption, replay/revocation and mismatched owner. |
| R7 | Code P2-7; State P2-7 | Remove non-read privileged kinds from read admission OR define exact exhaustive capability requirements. Worker issuance derives/checks the registry-owned requirement, never caller-chosen QUERY. Query-only contexts produce neither privileged leases nor effect ordinals. If migration remains in this grammar, distinguish metadata/data requirements; no lowest-common-denominator default. |
| R8 | Code P2-8 | Require drain/fence installation before close outcome/finalization and use the closed local transition grammar. OPEN finalization refuses without mutation. After close begins new acquisition through that ancestry refuses; unrelated peers remain CURRENT. |
| R9 | Code P2-9; State P2-5 | Add exact binding/epoch/fence-bound activation negative recovery and unused-withdrawal proof inputs, including durable-record outcome, restored old access and no-ever-open as applicable. None, stale/mismatched/incomplete evidence cannot exit indeterminate/unused. Preserve used epochs/evidence against reuse; ACTIVE has no outgoing activation edge. These are proof shapes/reference fixtures, not actual physical proof. |
| R10 | State P2-1 | Make generation permits sealed exact issuer identities, with epoch/ownership in private records; release accepts only the owning registry/issued record. Forged, equal-value, cross-coordinator or replay releases preserve counts and cannot enable migration while a lease remains live. |
| R11 | State P2-2 | Attribute queued buffer ownership to local ancestry. Graceful/fenced close must invalidate/release selected buffers exactly once or remain nonterminal; CLOSED means no queued valid buffer or active/contained handoff. Test queue/subscription/runtime levels, repeated close and unaffected peer buffers. |
| R12 | State P2-6 | Define authoritative migration recovery for requested-next success, full rollback/no effect with a new old-binding epoch, and binding non-reuse. Pin old/requested bindings before effects; mismatched/absent proof cannot publish/reopen/retire. Keep ACTIVE protocol epoch mandatory through all recoveries and RETIRED binding. |
| R13 | State-Supp-P2-1 | Validate the full owner/state transfer before mutation; commit owner and state together. Enumerate states versus queued flag. Every refusal preserves owner/state/completion/ancestry/global counts; the old owner remains usable and the proposed owner rejected. Legal transfers charge once. |

Correct the original counterexamples and adjacent alternate paths, not only
one assertion each. Tests must execute real reference state/effect transitions
and demonstrate zero-effect refusals and conservation. Do not claim production
thread/lock/provenance/physical-fence correctness. Preserve accepted W1 commit
truth and deferred wrong-method P3; no unrelated source/grammar/runtime change.

## Implementation boundary and cohesive ownership

The original exact allowlist plus generation_reference.py remains authorized.
To keep the correction cohesive, the builder may also create these narrowly
scoped internal files if needed:

- src/garns/backends/contracts/consumers.py — sealed exact consumer identities
  and closed reference step-product/parameter contract; no real SQL lowering.
- src/garns/backends/contracts/buffer_reference.py — private registration,
  buffer provenance and local queue permit accounting; no actual live engine.
- src/garns/backends/contracts/recovery.py — typed activation/migration proof
  inputs and closed recovery outcomes; no operator tool or database proof.

This additive ownership extension does not authorize another API/design object
or operational subsystem. Ask before any other path. Keep files cohesive below
500 where practical; record exceptions and do not split by line packing. Update
only additive A16/amendment and already-allowed tests/exports for corrected
contract shape. Original A1–A15 and accepted W2 base/overlay stay immutable.
No helpers, dependencies/network, generated evidence, services, Git/GWZ or
tools/check.py in the live tree. No self-acceptance or self-closure.

Names remain internal/provisional; W3 Surface and final release gates remain.
This correction realizes the already accepted design, not a new public API
freeze. Do not widen provenance or privilege just to make a fixture pass.

## Verification and next gate

After the single consolidated patch, run focused/full/product on all existing
Python3.11–3.14, using the brief's cached Lark1.3.1, bytecode disabled and no
warning filters. Use AST parsing, not py_compile. Reproduce all mapped vectors,
including State supplement. Verify input/control/baseline/ReadOnly/ProductGuard
bytes; old initial current manifest verifies from Revision1, not live source.

STOP WRITES, then return full path/command/result/limit testimony. Manager
files it verbatim, independently reproduces gates and pins MANIFEST-2 for the
complete current contract/ADR/tests and controlling amendment/remediation.
No finding is closed by the builder or green tests.

Fresh peer-blind Code/State reviewers assess the entire revised object and
each original counterexample; original reviewers separately verify focused
closure where possible. All P0/P1/P2 must be independently closed on the same
tuple before acceptance. This is correction1, one architecture allowance
remains. A further architectural issue after correction2 stops for the operator;
do not silently create a replacement object or authorize a third architecture
patch. No actual planner/backend/runtime work launches from this plan.
