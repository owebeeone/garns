# GARNs worker exit redesign brief

Status: operator-authorized narrow replacement design; not implementation or
acceptance. Date: 2026-10-04. Manager owns this brief and review records.

The operator explicitly approved: “yes - do a narrow worker-exit redesign -
proceed”. This opens a new design object following the stopped W1/A11 amendment.
It does not erase that object's two architecture corrections or accept its
71-file candidate. The required output is a precise additive design resolving
worker-exit ownership and carrying the four bounded defects in the stop record.
Source remains frozen while this design is drafted and reviewed.

## Controlling inputs and immutable boundary

Read ../AGENTS_GWZ.md, product AGENTS.md, CurrentProgramCheckpoint,
PRODUCT_LAYOUT, the complete review-loop skill/template and split-files skill.
Read the complete accepted W2 base/overlay, W1/W2 acceptances, A1–A16 and
current contract sources/tests. Read the stopped amendment, execution brief,
two remediation plans, final Code/State reports, both current NO-GO closure
reports and the manager stop/evidence records. Current source is evidence of
the failure, not permission to implement fixes. New Inputs.sha256 pins the
brief and controlling evidence. MANIFEST-3 remains exact SHA-256
23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424.

The sole drafter may create/edit only:
dev-docs/W1A11-WorkerExitRedesign.md.
No helpers or competing drafts. Use operator-selected gpt-5.6-sol.
Use apply_patch. All other files are read-only to the drafter. The manager
alone files complete testimony, prompts, manifests, reports and acceptance.
Do not modify source/tests/ADRs, accepted documents, stopped documents/reports,
historical archives, manifests or grammar. No network/dependencies/services,
DB access, Git/GWZ mutation, activation, public naming freeze, generated output
or tools/check.py. Existing reference tests may run with -B and bytecode disabled;
test passing cannot count as redesign implementation or finding closure.

## Required design outcome

Specify one implementable internal ownership/state grammar, not a menu of
alternatives and not another production runtime. Add exact proposed types,
method signatures, issuer-private records, validation/commit ordering,
caller/worker/runtime/containment identity and task trust, closed edges, terminal
truth, idempotency/conflict rules and fault schedules. Include precise additive
supersession of only the relevant accepted W2 clauses/current amendment claims.
The accepted result roles, no-raw-Plan boundary, pinned parameters, parent-owned
derived commands, task-bound public context and original A7 commit truth remain.

| Required root | All stopped finding IDs | Design and mandatory future regression |
|---|---|---|
| Worker exit | ReviewState-3 P2-1 | Exact worker-to-runtime result handoff and worker-to-containment failure/cancellation transfer bound to original live lease/operation/command/authorization/worker. Exception and cancellation revoke unused ordinals before another effect can begin, retain counts and have an authoritative quiescence owner. Define success versus begun/uncertain effect, result publication and authoritative completion; no caller-supplied worker/task/claims proof. Cover wrong tuple/current worker, reentrancy, nested effect attempt, exception, cancellation/dequeue race, close/revoke/generation race, repeated/conflicting handoff, and callback failure during cleanup. |
| Failed FIFO delivery | ReviewCode-3 P2-1; ReviewState-3 P2-2; FreshCodeClosure-2 P2-1, retaining Code2 P2-2/State2 P2-1 | Select one fail-closed rule for unpublished head: exact retry or explicit registration retirement/refetch. Only committed successful caller-visible head advances delivery. Non-success never invents cursor progress; successors cannot cross a gap. Conserve active and queued permits and terminal idempotency. |
| Participant lifecycle | ReviewCode-3 P2-2 | Exact activation-bracketed join and quiescent final leave; no preactivation admission survives activation. Retained work and unresolved close obligations prevent membership loss. Frozen attempt participants cannot mutate; a closed idle runtime must not become a permanent future obligation. Include join/leave before activation, during drain, after migration and after local close. |
| Neutral refresh | ReviewState-3 P2-3 | Trusted sealed neutral result consumes once and advances internal progress without outward batch/envelope/permit. Define how neutral cursor ranges interact with prior queued/active deliveries and the next changed refresh; do not conflate produced and delivered progress or permit overtaking. Cover zero/one/multiple queued ranges, all provenance/barrier failures and replay. |
| Phase-exact migration proof | OriginStateClosure-2 State-Closure-P2-1 residual, retaining OriginStateClosure-1 State-Closure-P2-1 | Bind evidence to exact current attempt phase/serial and requested successor. Proof issued before begin_migration cannot authorize later exclusive-request release. Cover current phase success, stale same-attempt phase, wrong request, replay/cross-coordinator/cross-attempt, barriers and old admission/queue invalidation. |

Every row must receive an exact disposition and a design-level trace of its
original counterexample, plus the implementation regression that will prove
closure later. Preserve all initial18 and correction1 13 finding regressions,
including expanded revocation. Do not call source findings closed because the
design specifies their eventual correction. Both fresh full review tables'
narrow F8 GO claims do not override the filed cross-phase NO-GO.

## Cohesion and future implementation handoff

Plan responsibilities by lifecycle/data ownership, not by packing below a line
limit. The stopped lifetime_reference.py is 796 lines with a recorded atomic
registry exception. Do not split it now; explain whether worker exit belongs
in the existing registry/worker issuer or a genuine new boundary with one
mutation owner. Identify proposed future source/test/ADR paths without treating
that proposal as a write allowlist. Avoid independent mutation owners and cyclic
state changes across helpers. Pure type/record separation is not by itself a
concurrency proof. Explicitly distinguish atomic deterministic reference steps
from deferred real async/thread/DB/cross-process ordering and durability.

Public names remain provisional for W3 Surface review. External-write capture,
actual planner/lowering, PostgreSQL/SQLite runtime/backends, production worker,
durable recovery, physical fencing, credentials and deployment activation stay
deferred. The design must not require those subsystems to pretend its model
shapes are safe. Existing W1 terminal diagnostic P3 remains for W3.

## Review and acceptance

After drafting, STOP WRITES and return complete standalone testimony with path,
key decisions, unchanged guards, read/test commands and limits. Do not self-GO.
Manager pins the design plus full controlling tuple under the parent plan's
filesystem-SHA exception; no commit authority is inferred.

Fresh peer-blind Consistency/Safety design review is mandatory. The originating
State reviewer, if context survives, separately checks prospective worker-exit
counterexample closure; missing originating contexts are recorded and require
independent retracing, not fabricated continuity. New object correction count
starts at zero only under the explicit operator directive above; at most two
architecture correction rounds. Any third architectural root requires STOP.

Design acceptance requires exact GO/GO and all five root obligations specified
without conflicting with unchanged contracts. It accepts the replacement
design only, not the stopped implementation, closed source findings, production
support or activation. A later narrowly scoped contract/reference build needs
its own exact execution brief and explicit implementation authority.
