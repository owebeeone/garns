# W2 admission-lifetime redesign — consolidated remediation 1

**Status:** manager-authorized design-only correction; not acceptance
**Date:** 2026-10-04
**Object:** stopped base plus replacement overlay; replacement architecture correction count 1 of at most 2. The stopped base's exhausted history remains unchanged.

Initial overlay SHA ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638 is preserved byte-identically in W2-AdmissionLifetimeRedesign-Initial.md. Initial manifest1 SHA 9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5 is historical and will no longer validate the mutable overlay path after correction; its original content is preserved separately, not rehashed or relabeled.

## Same-tuple reports and merge

All three reports are filed VERBATIM and reviewed by manager:
- Consistency-1 SHA df48a9438348e83526fc4d698fa3c293dbdf70f9b9767d1b2e8da54f97817399: NO-GO, two architecture P2 and one bounded P2.
- Safety-1 SHA 201a53f3b9e51b7b642d2241ae75aa803b6c02bb45f74337d0e39e0f8f7b3d0e: NO-GO, two architecture P2.
- OriginSafetyClosure-1 SHA 928c441e82fc85f20ac2569c35634d76160ce418c5d871b08e9035016006d93d: original stopped lifetime P2 closed; new local/global drain P2 blocks.

| Merged ID | Source findings | Disposition and exact correction |
|---|---|---|
| M1 | C-P2-1 worker authority | Accept. Define an issuer-private, exact-command/effect-bound worker authorization handshake with immediate pre-effect expiry/invalidation checks, no context transfer/caller claims, success and hostile vectors. Keep task-bound public TrustedContext unchanged; explicitly require a separately reviewed A11/W1 authority-extension amendment before enabling this path. No A11 or contract changes now. |
| M2 | C-P2-2, S-P2-1, Origin-P2-1 local/global drain | Accept one shared root. Separate local runtime/pool/connection/subscription states and resource attribution from deployment generation states. Local close fences only descendant work; unrelated peers remain CURRENT. Only serialized migration enters DRAINING_OLD; retained local containment remains visible to global migration. Define closed state/terminal/reopen rules and two-runtime vectors. |
| M3 | C-P2-3 queued-buffer ordering | Accept bounded contradiction. Put one authoritative queue invalidation/release barrier after stopping refreshes and before zero-permit wait, account concurrent/late enqueue and active handoffs, make post-cutover cleanup/registration retirement non-duplicative. Align all sections/vectors. |
| M4 | S-P2-2 already-open legacy peers | Accept architecture root. Define a finite-wait stop-the-world activation prerequisite owned by deployment operator, authoritative legacy inventory/drain/physical fencing, a durable activation fact, refuse if absence/fencing cannot be proved, no cooperative handshake-only census, precise restart/rollback/new-deployment cases. Name future activation implementation/review ownership, never claim it done. |

There are four merged roots, three architectural and one bounded. They consume ONE consolidated architectural remediation round, not one round per finding. No disputes/P3 were reported.

## Sole writer and controls

The SAME sole drafter writes ONLY dev-docs/W2-AdmissionLifetimeRedesign.md with apply_patch. Read full reports, this plan, preserved initial overlay, unchanged brief/base/STOP and full A11/authority plus relevant controls. Do not write reports, snapshots, manifests, checkpoint, contracts, source/tests, ADRs, grammar, services, dependencies, Git or GWZ. No helpers and no build.

Preserve original whole-operation lifetime closure and every old closed counterexample. Explain exact supersession changes, dependency amendments and closed state/lock/linearization rules rather than hand-waving future implementation. No expansion into actual deployment tooling or cryptographic authentication. Return complete concise testimony, design hash and unchanged recursive checks, then STOP writes.

For correction START/END verify immutable replacement Inputs11, stopped manifest13, source48/control13/W1 26. Historical mutable-path manifest1 is not a current recursive check after overlay changes. Manager pins corrected overlay/testimony, this plan, all initial reports and initial snapshot plus unchanged Inputs11 in new manifest2.

Material authority/lifecycle/activation changes require FRESH numbered full Consistency/Safety reviews. Original fresh reviewers must verify their exact counterexamples; the originating stopped Safety reviewer must retain its original lifetime closure and verify its local-close finding. Current peer reports remain blind during the fresh round. No acceptance absent same-tuple GO/GO and verified origin closure.

