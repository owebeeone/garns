# W1/A11 worker-exit redesign — consolidated bounded correction 2

**Status:** authorized design correction 2/2; not acceptance or source authority
**Date:** 2026-10-04
**Owner:** manager

## Exact current verdict merge

Design revision2: `c8e7ac802cb1499a84339874f9b1ceec0ccc523a675933b4bf9dea3d4c05cdb1`.
Complete100 MANIFEST-2:
`bc97828a15fc0a2d728a956695d1b38c41c8f63822fb070af9e4deb0ae64e653`.
DRAFT-2: `444665615580336641162399ec1d9e1ba7be4ce45ae619c922cae0e9ac44dd85`.

Fresh Consistency-2: NO-GO two P2s, report SHA
`740e14350efe532cce940c655ef4a03b76f9ffd46f96df353ef06503149d0dec`.
Fresh Safety-2: NO-GO one P2, report SHA
`6d3785cdcddeb3b0e1589e28da3ceba5ece4d328707fe4c8449b665658d5f3ff`.

Both reviewers independently classify their three roots as bounded, not new
architectural roots. Both pre-commit to GO only if their original sequences
are corrected without a new blocker. There is no blind convergence on the
same root this round. Consistency identifies the neutral terminal regression
and impossible evicted-identity lookup; Safety identifies split publication/
settlement. Same-origin round1 design closures and originating stopped
Code/State prospective closures report GO, but those narrower verdicts do not
override the full blockers. Neutral capacity is not yet fully closed according
to fresh Consistency; retain that explicit partial-closure distinction.

## One patch; all IDs accepted, none disputed/deferred

| ID | One chosen bounded disposition | Exact prospective closure |
|---|---|---|
| Consistency-2 P2-1 | Restore atomic neutral refresh terminalization/release: candidate consumption, cursor/span/ring mutation, exact successful lease terminal state and one ancestry/generation release are one transition, without a delivery publication/batch/buffer permit. In-window replay reads the same bounded committed outcome and never releases. Every known active-candidate RefetchRequired/error path has an explicit lease disposition: refuse/release only when quiescent, otherwise retain containment until exact stop. Unknown/cross opaque identities refuse mutation-free and cannot authorize arbitrary lease completion. | Start one charged refresh, neutral commit => terminal refresh/count0/buffer0/publication0; exact replay no changes; close/migration immediately before/after commit and overflow/retired paths conserve owner/count exactly once. |
| Consistency-2 P2-2 | Select uniform typed unavailable behavior when an opaque candidate/receipt is absent from the bounded authoritative records. No history-sensitive stale-cursor recovery after eviction; no semantic fields in empty handles; no lifetime-long tombstones. Explicitly distinguish a current issued unconsumed candidate in its bounded operation-owned record from an in-window committed replay. Align retired/cross/unknown/counterfeit lookup behavior without inventing historical registration provenance. Enumerate/account every finite retained record; no auxiliary unbounded lookup table. | Commit far more than R; old evicted candidate/receipt, live in-window pair, cross-registration pair and counterfeit receive specified deterministic lookup outcomes, no mutations, no more than bounded active-candidate and C replay state. |
| Safety-2 P2-1 | Choose specialized handoff settlement AS the final publication barrier. From a nonterminal publication-ready exact handoff, one lifetime-owner mutation validates authority/owner/generation/FIFO/candidate, records publication, removes head/folds its neutral span, advances delivered frontier, sets terminal success, releases ancestry/shared charge once, THEN exposes the value. It cannot require prior terminal success or a committed publication bit. Generic completion/publication cannot bypass this transition. Non-success settlement initiates retirement/queued invalidation without active release while nonquiescent; its quiescent final settlement atomically records terminal non-success, removes retained active ownership and releases once. A previously releasing generic outcome is not its input. | Last-permit handoff with pauses before/after the SINGLE commit: race migration/close/fence/receiver loss. Never permit count0 with unsettled head/cursor or expose value before all facts commit. Exact replay no cursor/release; conflicts mutation-free. Every non-success keeps delivery unchanged, queues invalidated once and active charge retained through exact stop, then terminalizes through specialized settlement exactly once. |

Read each full report, not just this table. Reconcile §§2, 5--8, 10, 12--14
and every replay/terminal/receipt claim; do not append a note while leaving
earlier incompatible preconditions controlling. Provisional private method/
receipt names may change only to remove the mapped ambiguity, not to freeze
public API or introduce a new subsystem/owner.

Preserve all earlier six design IDs and five stopped roots, initial18 and
stopped correction1 13 regressions plus expanded revocation. Preserve single
owner, finite command ledger, receiver-loss observation, primary failure order,
task-bound claim-free context, no Plan/callback seam, pinned result roles/
parameters, parent commands/one permit, unchanged A7 and migration product.

## Sole owner and guards

Only the same drafter may edit `dev-docs/W1A11-WorkerExitRedesign.md`.
No source/test/ADR/accepted docs/report/checkpoint/old testimony/manifest writes,
no helpers, Git/GWZ/network/services/install/database/generators or actual build.
Return complete stop-writing testimony for manager to file as DRAFT-3.

At START and END: new RemInputs, Revision2 derived archive map100,
Revision1 archive map88, RemInputs1 thirteen, original Inputs19, frozen
source71, ReadOnly111 and ProductGuard614. Original manifest2 must not be
checked against changed live design. Revision2 holds original design, DRAFT2,
and manifest2. VERIFY-from-product-root rebases only design/DRAFT2 paths; all
other original98 inputs remain frozen. Its SHA is
`4d1cbcc6626b6f41d6a0b04e08919d25177fed779f57338db79f36d05f88234c`.

## Final gate and cap

Delivery of this consolidated edit consumes correction2/2. No counter reset.
These remedies preserve the selected architecture and reviewer-classified
bounded transition/lookup fixes, so continue the same fresh Consistency2 and
Safety2 agents for peer-blind focused re-verdicts plus their changed-range
attacks. Recheck relevant original design/source counterexamples at the final
tuple. If the edit materially changes architecture despite the plan, use
fresh full dual; if any new architectural root appears after this correction,
STOP and ask the operator, never silently start a third patch.

Only exact required GO/GO and originating closure permit design-only acceptance.
Source remains stopped/open. Later contract/reference implementation needs a
separate exact brief and explicit authority; this plan does not launch it.

