# W1 A11 amendment final consolidated remediation

Status: manager authorization for correction2 of at most2; not acceptance.
Date: 2026-10-04.
Object: same narrow internal contracts/reference-model amendment.

## Verdict merge and immutable evidence

Complete59 MANIFEST-2 SHA7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b
is preserved with all its exact files under W1A11-ContractAmendment-Revision2/.
Verify that manifest INSIDE Revision2 after authorized source corrections.
Revision1 and accepted Baseline remain immutable; do not rewrite historical
manifests to imply current source acceptance.

All four reports are filed verbatim under dev-docs/W1A11-ContractAmendment-:

- ReviewCode-2.md, NO-GO3P2,
  dfacc89f2541b8895437d3f2d51335d6811d5316e5869f3b508df58fc8bc8349.
- ReviewState-2.md, NO-GO6P2,
  07318ac54c3fe4cb7b79dd62159b0538996bcee2f1faeb46695677a940d98118.
- OriginCodeClosure-1.md, NO-GO3residuals,
  56f2fa995e66bdf815ec33f430b4ccae3797c8070bacee42ab4a07c2501a3023.
- OriginStateClosure-1.md, NO-GO1newP2,
  e673d2a5ad92e2804103fd4d88d03e4a70c42fd626a19dc64227dccb9a3d843e.

Fresh axes independently converge on arbitrary callback/step transaction
and multi-envelope cursor defects. Origin Code independently confirms the
callback leak. Findings vary in how they classify residual versus new roots;
all blocking counterexamples remain binding, with no waiver or self-closure.
Accept all13 current blocking IDs, consolidated into10 correction groups below.
The previously mapped18 IDs and expanded StateP2-4 remain regression obligations,
not silently replaced by this table. Origin tests close narrower original
sequences but do not override a fresh review's adjacent open counterexample.

Quota interrupted three agents without verdict; operator restored quota and
requested continuation. All resumed on unchanged manifest2. It does not count
as a round. This one consolidated architecture patch consumes correction2;
no additional architectural correction is authorized. No replacement object
or broadened production implementation is silently launched.

## Every finding disposition and closure test

Report namespaces below: Code2/State2=fresh review2; OriginCode1/OriginState1=
originating closure1.

| Group | Every current mapped blocking ID | Accepted correction and causal closure |
|---|---|---|
| F1 | Code2P2-1; State2P2-6; OriginCode1P2-1residual | Remove ordinary caller callbacks entirely from the raw-plan/uncommitted-step path. Fixed issuer-owned consumption returns only closed products after validate-and-commit. No external code runs while Plan/admission state or an uncommitted rank is exposed. Rank/state/publication must have one atomic compare-and-commit with no reentrant overwrite. Test original frame and raised-traceback Plan escape, same/later-step recursion, exceptions/retry, and reentrant fence/revoke/epoch/completion attacks. All refused attempts have zero effects/publication and conserved charges; a winning publication is committed before any outward observer and cannot be relabeled unpublished. Do not solve this by walking returned objects or deleting only one local while its callers retain Plan. |
| F2 | Code2P2-2; State2P2-1 | Separate produced-through frontier from delivered-through cursor and exact FIFO/head ownership. This package selects ordered delivery, not a new coalescing semantic. Two sequential ranges accepted into one registration must dequeue in order; later-before-earlier refuses mutation-free. Keep one active head handoff or equivalent exact ordered completion ownership so completing deliveries out of order cannot advance a cursor falsely. Invalidation/close/migration releases queued permits once and retains active handoffs. Test two ranges, copy/cross-registration/replay, duplicate completion, rejection, invalidation between ranges, and count0 only after all terminal work. |
| F3 | Code2P2-3 | Retain successful activation's physical fence identity/evidence and compare same fence during ACTIVE_UNUSED withdrawal. Wrong deployment/binding/epoch/fence each preserves all fields. Exact same-fence withdrawal works once; first open remains irreversible and protocol epoch survives lifecycle/migration/nonreuse. No actual physical proof is claimed. |
| F4 | State2P2-2 | Bind drain to an exact issuer-private migration-attempt identity and frozen registered participant set. Each participant installs one exact pre-zero queue barrier/acknowledgement for that attempt, even if its queue is empty. CURRENT/MIGRATING/stale/cross-participant/duplicate/after-reopen barriers refuse without state/count mutation. Migration and no-effect reopen refuse until all required acknowledgements exist; count0 alone is insufficient. Registering/changing participant topology during drain must refuse or have an explicit conservative rule. Test two participants, skipped acknowledgements, dequeue winner, late enqueue, multiple buffers and exact-once release. Keep local close distinct from deployment drain. |
| F5 | State2P2-3 | Add sealed exact issuer-private initial-snapshot/refresh candidate identity with owning lease/operation, frozen rows, watermark, registration/cursor lineage and advancement. Trusted fixed guarded production of a candidate precedes publication; caller-supplied rows/cursor are not a replacement candidate. Reference fixture production must be explicitly named/trusted and not claimed real DB provenance. Initial registration atomically consumes one exact candidate and publishes rows/S/registration; refresh consumes exact rows/H candidate once. Test no-fetch/no-watermark shortcut, fabricated/cross-lease/copied/reused/stale candidates and candidate after authority/epoch/fence changes, zero publication and conserved counts. No actual SQL/backend/runtime is authorized. |
| F6 | State2P2-4 | Remove public independent NESTED_FETCH/TOTAL_FETCH lease acquisition. Child/nested/total guarded commands remain under one parent operation, owner, context, binding and permit; no independent publication or terminal completion. Support multiple child/total commands without backward rank or duplicate-command replay, using exact finite command identities/ordinals where needed. Parent containment/terminal outcome prevents further child work. Test direct child/total acquisition0permits, multiple derived commands1parentcharge, fence/parent completion, no independently published derived result. |
| F7 | State2P2-5 | Require exact requested generation old+1, not merely greater, in migration and recovery proof validation. Equal/lower/skipped request refuses before state/effect mutation; pinned exact successor survives effect/publication/recovery. Test successor-only plus missing/mismatched proofs, preserving existing3indeterminate outcomes. |
| F8 | OriginState1State-Closure-P2-1 | Add exact pre-effect no-effect proof tied to qualifieddeployment, oldbinding, activeprotocol epoch, coordinator-owned current drain attempt, no-effect outcome and released-exclusive-request evidence. None/wrong/stale/cross-coordinator/cross-attempt/replay proof cannot reopen, incrementepoch, clearoldbinding or reopen queues. Require F4 acknowledgements before valid reopen. Valid proof advances admissionepoch once and preserves oldhandle/lease invalidation; old invalidated envelopes never resurrect. Test another drain on samebinding/epoch rejects previousproof; preserve post-effect recovery. |
| F9 | OriginCode1P2-6residual | Authenticate actual assigned worker using the issuer's trusted current-task/worker source at dequeue and immediately before each effect, separately from validating original public context. Merely presenting the worker object as an argument is not proof. Issuingtask/thirdtask exacttuple impersonation yields zero effects, unchanged QUEUED owner/state and unconsumed ordinals; true assignedworker consumes once. Public context remains issuing-taskbound; no context impersonation or caller-selected freshness. |
| F10 | OriginCode1P2-3residual/newboundedroute | Include targetqueue exactancestry/localstate/QueueState in initial registration publication barrier, not only parent subscription ancestry. DRAINING/FENCED/CLOSED/MIGRATION_INVALIDATING destination refuses before registering/publishing and preserves charges/fences. Test closedqueue with still-open parent, wrongqueue and queue changed after candidate production. Integrate with F1/F5 rather than separate bypass. |

All groups accept the report's required correction and tests; no contested
finding or silent omission. Original CodeP2-1/3/5/6/9, StateP2-3/4/5 and
originalR12 related tests must retain stronger adjacent counterexamples, not
claim closure solely because the original shortest sequence now refuses.

## Sole builder ownership and cohesion

Same5.6Sol builder owns one consolidated patch, no helpers. Existing exact
execution-brief/ownership-extension/RemPlan1 source/tests/ADR allowlist remains.
Manager additionally authorizes these two optional cohesive internal modules:

- src/garns/backends/contracts/snapshot_reference.py: sealed initial/refresh
  candidate identities, private reference evidence/fixture production and
  consumption, no real snapshot/database implementation.
- src/garns/backends/contracts/migration_reference.py: sealed migration attempt,
  participant/barrier acknowledgement contract shapes/private reference records;
  no operator/service/actual cross-process coordinator.

Keep consumers/buffers/recovery/worker/generation coherent. Revisit the
611-line registry exception under split-files guidance; split by genuine
ownership, not line packing. If no safe cohesive split exists, record exact
reason/revisit point rather than claiming under500. Do not introduce cyclic
mutation ownership, helper agents, another competing design or dependencies.
Ask the manager before any additional path. Existing authority.py is already
allowed; use the trusted task hook without weakening public authority.

Original A1–A15, accepted W2 pair, operations.py, grammar, product runtime,
compiler/lowerer/generator, accepted archives,614protectedfiles and111readonly
inputs remain immutable. A16/amendment may update additive current shape and
explicit supersession. No tools/check.py, bytecode-producing compile steps,
network/install/services/DBs/Git/GWZ/publicAPI/activation implementation.

## Verification and final review gate

Run focused/full/product on all existing3.11–3.14 with cachedLark1.3.1,
bytecode disabled/no warning filters, ast.parse rather than py_compile.
Preserve original attack suites and all18initial/13currentfinding regressions.
Check inputs/control/Baseline120/ReadOnly111/ProductGuard614, RemInputs1,
new RemInputs2. Manifest2 verifies inside Revision2 after source amendment;
manifest1 inside Revision1; accepted historicalnestedmanifests insideBaseline.
Return STOPWRITES plus complete path/command/result/limits testimony; no
self-closure or acceptance.

Manager independently reproduces gates and pins complete MANIFEST-3. Fresh
peer-blind Code/State reviews plus originating closure checks reattack all
counterexamples on same exact tuple. Any newly found architectural blocker
after this final correction triggers STOP for operator redesign-or-accept,
not a hidden third architecture patch or automatic replacement object.
Bounded-only further correction must follow review-loop rules and explicit
classification. No downstream actual planner/backend/runtime launch follows
from this remediation plan.

