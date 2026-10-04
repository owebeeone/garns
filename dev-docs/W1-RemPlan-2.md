# Garns W1 consolidated remediation plan — round 2

**Status:** five accepted P2 findings; one final architecture correction  
**Date:** 2026-10-03  
**Remediation round:** 2 of at most 2 architectural rounds  
**Owner:** manager

Fresh Code and State reviewers independently re-ran and verified all original
counterexamples on the second tuple. They nevertheless report NO-GO: Code
has one new architectural P2, State has two architectural and two bounded P2s.
Their full reports are preserved verbatim. No W1 acceptance or W2 launch occurs.

| Finding | Disposition and required correction | Closure test |
|---|---|---|
| Round-2 Code P2-1 | Accept: freeze one subscription delivery call graph. A runtime/request-bound iterator must perform live authority validation itself; remove the parallel bypass. Renewal closes/replaces old authority-bound iteration, never silently rebinds a stale resource. | Actual async-for fake: expire, advance epoch, invalidate exact context, use wrong owner/child task between yields. Refuse before read/delivery; no authority-free alternate protocol method. |
| Round-2 State P2-1 | Accept: runtime-owned clock, invalidation epoch and request/task ownership sources. Remove raw time/epoch from ordinary protected operations; callers cannot select freshness or impersonate ownership through value strings. Test providers are injected only at trusted setup. | Advance injected runtime clock/epoch, then exercise every protected operation before adapter invocation; operation signatures cannot accept stale time/epoch overrides. |
| Round-2 State P2-2 | Accept: exhaustive migration outcomes tied to the request. Data-changing success requires same-scope/new-generation publication with genuine nonempty effects, transaction identity and request/payload-digest linkage. Metadata-only success requires its no-data/no-observable-shape proof. Refusal/indeterminate cannot masquerade as successful accounting. | Enumerate class/outcome combinations; missing/empty/wrong-scope/wrong-generation/wrong-identity/wrong-digest publications refuse. Both backend fakes return one atomic typed result or typed refusal. |
| Round-2 State P2-3 | Accept: exhaustive phase/evidence relation; commit-requested cancellation cannot infer abort from rollback confirmation. Durable reconciliation is separately identity-bound. | Full phase × evidence matrix; invalid pairs refuse, uncertain commit remains indeterminate, original rollback-loss traces remain correct. |
| Round-2 State P2-4 | Accept: capture actual task identity or genuine runtime-owned identity, compare by identity/provenance, forbid owner replacement and child-task retention. | Equal strings/hostile equality objects and separate real tasks cannot enter during or after rightful owner's call; nested/concurrent use still refuse. |

Same sole architecture owner, same exclusive paths: `docs/adr/**`,
`src/garns/backends/contracts/**`, `tests/contracts/**`. One consolidated patch,
no competing contract owner. This remains W1 pure contracts/reference models
and conforming fakes; no actual runtime/backend/database services, external
capture, compiler algebra, dependency installation, Git mutations or manager
record edits. Cohesive boundaries remain appropriate under split-files.

Read complete round-2 reports, do not infer details solely from this table.
Keep all previous findings' regressions, run existing Python 3.11–3.14 full
and focused suites plus product/integrity checks, then stop writes and return
the complete report for manager filing. Builder claims are not closure.

Shared authority/delivery/migration interfaces change, so the manager will
pin a third tuple and launch fresh peer-blind Code/State review round 3. A
further architectural root or unresolved architecture after this final
correction stops the lane for operator redesign-or-accept: no silent third
architectural patch. Bounded non-architectural corrections are governed by the
skill's narrow exception and cannot be used to disguise architecture work.
