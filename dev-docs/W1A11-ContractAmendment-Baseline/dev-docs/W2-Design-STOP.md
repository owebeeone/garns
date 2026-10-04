# W2 design stop and operator decision

**Status:** STOPPED, design not accepted  
**Date:** 2026-10-03  
**Owner:** manager

The authorized design and review work produced W2-QueryPlanningDesign.md, but
the final full review is Consistency GO / Safety NO-GO. Under the review-loop
skill, two architecture remediations are exhausted. Safety identifies one new
architectural root. No third patch, W1 amendment, implementation or Git landing
is authorized. All owner writes are stopped.

## Exact stopped object and testimony

- Design SHA-256:
  `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`.
- Thirteen-file W2-Design-MANIFEST-3.sha256 SHA-256:
  `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`.
- Final full Consistency report W2-Design-ReviewConsistency-3.md SHA-256:
  `6b1c5d271795c5aa61cacd0275b4eaf2dfdb8d3da8bdb8927fee06b86a280173`.
- Final full Safety report W2-Design-ReviewSafety-3.md SHA-256:
  `ba6ef3ad72b11882130783792a3d5e860b47252ac408447e629c694bdd29db75`.
- Originating round-2 Consistency closure SHA-256:
  `0c0371d190ee56735208a5728bcb13d48af279ca7a863b6674645c392e3d2f24`.
- Originating round-2 Safety closure SHA-256:
  `ef7bc87bc4134d0dccb9481f2b7e49f314dc215fe4b854abc04b78a498ecb426`.

All reports and builder testimonies are filed verbatim. Initial and revision-2
designs remain byte-exact historical objects. All 48 source/test/grammar, 13
control and 26 W1 entries remain unchanged. Manager independently reproduced
the nine function fingerprint goldens in memory; no future implementation
test or database/async proof was run.

## Remaining blocker and verdict merge

Final Safety P2-1: verifier resolution returns a private raw plan without
lifetime-bound ownership of the ensuing operation. A close or migration can
revoke its handle after resolution but before lowering, adapter invocation,
fetch, snapshot watermark or delivery. The resumed operation can still use
old semantics; merely revoking registry entries does not prove quiescence.

Accepted A3 requires drain or typed unresolved/nonquiescent ownership; A8
retains non-killable worker containment; A12 controls connection compatibility
and generation publication. Those contracts remain binding, but the final
design does not explicitly connect admitted operations to their fences.
The manager accepts this finding for operator consideration, not self-closure.

The originating focused Safety reviewer judged migration fencing covered by
A12; the fresh full Safety reviewer found the missing operation-lifetime
connection a blocking architecture defect. Focused GO does not supersede the
fresh full NO-GO. Final Consistency GO cannot compose with Safety NO-GO into
acceptance. All earlier original/bypass/resource counterexamples are verified
closed; one new blocker remains.

## Recommended operator-directed replacement

Authorize a narrow admission-lifetime redesign, not another ordinary patch:
verification should acquire an operation lease binding runtime/epoch/binding/
generation through lowering, adapter work, assembly and publication or typed
containment. Close blocks new leases and cannot claim CLOSED while any lease
remains live. Migration must drain/fence old-generation leases before effects
or new generation publication, otherwise refuse. Cancellation and blocked
SQLite workers retain ownership until authoritative quiescence.

That replacement requires an explicit brief, exact exclusive document scope,
and fresh review against all retained counterexamples. Preserve the stopped
history and two-round cap; do not relabel this object accepted or reset its
counter automatically. Do not accept the correctness risk as a passing gate.

After design acceptance, separately scope/review the W1 amendment for structural
result roles and admitted-operation protocol, then the execution/ownership
brief for runtime registry/backend verification/legacy wiring. These are
prerequisites, not authority to alter W1 or launch W2 today.

External capture stays deferred. Grammar, unenforced, query/question semantics,
provider-neutral in-process trust and one convergent product remain unchanged.

**Next action:** operator decides whether to authorize the narrow replacement
design. No further work on the stopped object before that direction.
