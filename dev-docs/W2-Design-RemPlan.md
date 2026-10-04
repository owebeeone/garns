# W2 design — consolidated remediation 1

Status: authorized design-only correction, not acceptance or implementation.

The initial object is preserved byte-for-byte in W2-QueryPlanningDesign-Initial.md
(SHA-256 a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18).
Both complete initial reviews are filed verbatim. NO-GO/NO-GO;
five P2 findings, no P0/P1/P3. No findings self-close.

## Dispositions and closure

| Finding | Disposition | Required correction and original-counterexample closure |
| --- | --- | --- |
| Consistency P2-1 | Accept, bounded | Specify hidden structural identity/group keys, exact W1 types/names, visible-vs-structural assembly, and five exact design vectors (ordinary, optional/windowed, hidden grouped, distinct, nested). Use the accepted W1 contract only if its semantics support the convention; otherwise explicitly identify a reviewed amendment prerequisite, never mutate or silently redefine W1. |
| Consistency P2-2 | Accept, bounded | Close every canonical leaf/value schema, Order/TieBreak/default/authority forms, exact types/enums/order/uniqueness and registries; choose a single path representation with precise existing-expression projection/reconstruction. Demonstrate reachable-schema exhaustive closure and semantic-vs-source-spelling golden vectors. |
| Consistency P2-3 | Accept, bounded | Specify deterministic backend-neutral per-function fingerprints including same-result semantics, dialect exclusion and separate dialect implementation version gate. Supply golden fingerprints for every current pure entry and concrete mutation vectors. |
| Safety P2-1 | Accept, architectural | Close semantic provenance before execution: choose exactly one trusted compiler/runtime admission or rebuild-and-compare mechanism binding the entire plan/envelope and recursive closure to read identity/origin. Specify owner, cache invalidation and interface/ownership implications without widening source writes. Canonical same-origin altered scope/authority/archive/member/identity/predicate/result/subplan roots must refuse before lowering/adapter; trusted exact roots succeed; relabeling refuses. |
| Safety P2-2 | Accept, bounded | Fix a versioned, concrete resource profile covering payload/preparse depth and nodes, expressions, subplans, results, functions, params/defaults, string/identifier bytes, fanout and total work. Specify counting, admission/refusal precedence, parser bounding and compatibility. Exact-boundary, plus-one, breadth/depth/combined, shared-DAG, malformed UTF-8/duplicate-key and mixed-version vectors must be falsifiable. |

One sole drafter applies one consolidated document correction. Exclusive writable
path remains dev-docs/W2-QueryPlanningDesign.md; all other paths are read-only.
No source/test/grammar/backend/runtime/worker/ADR mutation, dependency installation,
database/service operation, Git/GWZ mutation or implementation launch.

Preserve parent scope, query/question split, unenforced, unchanged grammar,
expression reuse, explicit physical mapping and governed-write-only release.
Do not redesign unrelated code or silently fix the W1 P3 assigned to W3.
Review implementation feasibility and dependency qualifications while closing
the findings; do not claim future tests have run.

This is remediation 1 of at most 2 architecture remediations for this object.
Safety classified semantic provenance as architectural. Fresh peer-blind
Consistency/Safety reviewers must review the newly pinned full design and retrace
all five original counterexamples. Per parent plan §15, fresh reviewers replace
prior proofs after material changes; originating reviewers must additionally
verify their original findings where required by the review-loop closure rule.
No new current-round peer report is shared during review.

The initial manifests remain historical evidence; the revised object receives
a new numbered manifest and complete verbatim drafter testimony. Source/control
and accepted W1 manifest entries must remain byte-identical.
