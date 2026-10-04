# W2 admission-lifetime base-plus-overlay design — SAFETY-AXIS REVIEW

**Review object:** composed `dev-docs/W2-QueryPlanningDesign.md` at SHA-256 `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` plus `dev-docs/W2-AdmissionLifetimeRedesign.md` at SHA-256 `ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638`; operator-authorized replacement design, not accepted or implementation authority  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, read directly from the four-entry filesystem manifest `dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256` at SHA-256 `9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5`, under the accepted no-Git exception. Recursive source, control, stopped-design, overlay-input, and accepted-W1 manifests were verified directly; no Git snapshot, commit, or cleanliness claim was used.  
**Date:** 2026-10-04  
**Axis:** Safety — degraded and mixed-version paths, irreversible transitions and preconditions, disclosure scale, reachable stuck states, quiescence claims, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block. Both are new architectural root causes in the replacement object. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified while preserving the other composed-design invariants.

---

## 0. Evidence base

At both START and END:

- `shasum -a 256 dev-docs/W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256` returned exactly `9aa5a728ba15ce2fcb6596fc822fdad4ddc1ed95bf29b257fa23e89399ea3ca5`.
- The six required manifest counts were exactly 4, 11, 13, 48, 13, and 26.
- `shasum -a 256 -c` passed every entry in:
  - `W2-AdmissionLifetimeRedesign-MANIFEST-1.sha256`;
  - `W2-AdmissionLifetimeRedesign-Inputs.sha256`;
  - `W2-Design-MANIFEST-3.sha256`;
  - `W2-DesignSourceInputs.sha256`;
  - `W2-DesignControlInputs.sha256`;
  - `W1-RegistryContainmentRedesign-MANIFEST-3.sha256`.
- No tuple movement occurred.

I read the complete workspace and product instructions, review-loop skill and canonical prompt template, replacement brief and DRAFT testimony, stopped 711-line base design, 578-line overlay, stopped-object record, prior final Consistency and Safety reports, originating closure testimony, accepted parent-plan §§15–16, and the relevant complete accepted contracts and ADRs, including A2, A3, A6, A7, A8, A11 and A12.

The safety trace concentrated on:

- base §§5.3, 6, 8, 10–12, including raw-plan admission, lifecycle revocation, migration ordering, live reuse, future vectors and W1 prerequisites;
- overlay §1.1’s exact supersession map;
- overlay §§2–5’s identities, closed states, acquisition, owner transfer, publication and whole-operation barriers;
- overlay §§6–7’s graceful drain, hard fence, final fence, close and non-killable containment;
- overlay §8’s deployment-wide coordinator and migration transition sequence;
- overlay §9’s snapshot, subscription, buffer-permit and delivery lifecycle;
- overlay §§10–11’s staged protocol enabling and retained counterexamples;
- current W1 `AsyncConnection`, `AsyncPool`, `AsyncBackend`, `CloseOutcome`, worker commit-fence, authority, migration and semantic-plan contracts;
- A3/A8 separation of quiescence from transaction knowledge, A6 snapshot/cursor atomicity, A7 commit knowledge, A11 post-await authority validation, and A12 generation/mixed-version fencing.

I did not read either current replacement-review report or the other current reviewer prompt. No file, test, build, generator, dependency, database, service, Git or GWZ state was modified or invoked.

## 1. Findings

### [P2-1] Ordinary close is coupled to the deployment-wide migration state

**Classification:** new architectural root cause.

**Location:** `W2-AdmissionLifetimeRedesign.md:129-163`, especially the deployment binding states and legal edges; `:271-298`, especially the rule that graceful drain changes “the binding to `DRAINING_OLD`”; and `:300-325`, where runtime, pool, and connection close all install that graceful-drain barrier. The migration-only use of the same state appears at `:352-383`.

**Violated invariant:** closing one connection, pool, or runtime must fence work owned by that lifecycle object without globally changing the qualified deployment’s generation-admission state. Deployment-wide `DRAINING_OLD` must be entered only by an authorized migration/cutover operation with a defined success or no-effect reopening path.

**Reproduction/state sequence:**

1. Two healthy runtimes, `R1` and `R2`, participate in the same qualified deployment and current generation `G`.
2. `R1` closes one connection, its pool, or the runtime normally.
3. Section 7 says that close installs the graceful-drain barrier. Section 6 defines that barrier as changing records to `DRAINING` and the deployment binding to `DRAINING_OLD`.
4. Because the deployment coordinator is keyed by qualified deployment, `R2` can no longer acquire new shared-generation leases even though it is not closing and no migration was requested.
5. The legal binding transitions provide no ordinary-close edge from `DRAINING_OLD` back to `CURRENT`. The only reopening rule is the migration pre-effect refusal path, requiring authoritative proof that no migration effect began and a new admission epoch.
6. Therefore either:
   - an ordinary local close drains the entire deployment and leaves surviving runtimes unable to admit work; or
   - an implementation treats close as local-only, contradicting the specified state transition and leaving the composed contract unable to say which fence publication and acquisition must observe.
7. Applying the same rule to a single connection close widens the blast radius further: normal pool maintenance can disable unrelated connections and runtimes in the deployment.

**Impact:** the text permits a reachable deployment-wide stuck state and turns local resource lifecycle operations into global availability events. Recovery would require pretending an ordinary close was a failed migration or bypassing the stated binding state machine. This is a correctness and recovery defect, not merely an implementation-detail question.

**Required correction:** separate lifecycle scopes explicitly:

- local connection/pool/runtime drain must change only the relevant local admission records and prevent new ownership through that object;
- deployment binding must remain `CURRENT` while other admitted participants operate at the same generation;
- only a migration coordinator may enter `DRAINING_OLD`;
- define how local leases and delivery handoffs are attributed to connection, pool and runtime close, including which enclosing close waits for which descendants;
- give each local close state a complete terminal/reopen policy without mutating the deployment generation state.

The global generation permit must continue to block migration until locally closing operations become terminal, but local close must not itself request global cutover.

**Closure/regression test:** model two runtimes and multiple connections in one deployment. Close one connection, then one pool, then one runtime while the other runtime remains open. Verify that new work through the closed object refuses, its owned operations drain or return typed nonquiescence, the surviving runtime continues to acquire generation-`G` leases, and the deployment binding remains `CURRENT`. Separately start migration and verify that only that operation enters `DRAINING_OLD`, blocks both runtimes, and follows the specified no-effect or cutover transitions.

### [P2-2] The lifetime handshake cannot fence already-open legacy peers

**Classification:** new architectural root cause.

**Location:** `W2-AdmissionLifetimeRedesign.md:334-350`, which requires participating runtimes to join the coordinator at open; `:449-487`, especially the staged `plan_admission_lifetime_v1` handshake and assertion that no stage permits a working legacy path; and base `W2-QueryPlanningDesign.md:467-474`, whose older `plan_admission_v1` open-time negotiation is superseded. A12 requires mixed binaries outside an explicit window to refuse, but the overlay supplies no activation transition for peers opened before the new protocol.

**Violated invariant:** lifetime admission and deployment-wide migration fencing may not be enabled while any process capable of old bare-plan execution can remain attached to the deployment. An open-time check performed only by new binaries does not establish absence or quiescence of already-open old binaries.

**Reproduction/state sequence:**

1. Legacy process `L` opens deployment generation `G` before the lifetime protocol is deployed. It neither joins the new deployment coordinator nor understands `plan_admission_lifetime_v1`.
2. `L` remains running with an existing pool and the old executable plan path.
3. New process `N` starts, negotiates the lifetime handshake with its own new pool, joins the coordinator, and satisfies the overlay’s new implementation checks.
4. Nothing in the design requires an activation epoch, durable participant census, stop-the-world proof, or administrative fence that forces `L` to close before lifetime-dependent W2 work is enabled.
5. Because `L` predates the protocol, the rule that unsupported instances “refuse open/work” cannot cause `L` to refuse: it does not execute that rule.
6. `N` can therefore regard its coordinator’s permit count as deployment-wide while `L` remains invisible and can execute under the old path.
7. A migration initiated through `N` drains the new coordinator to zero and publishes generation `G+1`; `L` may still execute or publish generation-`G` work outside the fence.

**Impact:** the claimed fail-closed mixed-version transition and deployment-wide generation fence do not hold during the exact rollout boundary that introduces them. This permits stale-schema execution and false cutover quiescence, and can pair old-plan work with post-cutover state. “No online/mixed-version schema support” makes the missing activation boundary more important, not deferred.

**Required correction:** define a one-time activation protocol before lifetime-dependent execution is enabled. It must prove that all pre-protocol peers are absent or fenced, for example through a reviewed stop-the-world deployment transition or a durable capability/generation epoch that old peers cannot continue using. The protocol must specify:

- who owns activation;
- how existing pools/connections are enumerated, drained or forcibly invalidated;
- what durable fact proves no legacy peer can execute;
- the finite-wait/refusal outcome when that proof cannot be obtained;
- when the new handshake becomes mandatory;
- how restart and rollback behave before and after activation.

Merely requiring future opens to negotiate is insufficient.

**Closure/regression test:** begin with a simulated legacy peer already open on `G`, then attempt lifetime-protocol activation and migration from a new peer. Activation and all W2 execution must refuse while the legacy peer remains capable of work. After authoritative legacy drain/fencing, activation may publish its durable protocol epoch; thereafter old peers must be unable to reopen or continue, all new peers must join the coordinator, and migration may reach `G+1` only after every registered generation-`G` permit is gone.

## 2. Invariant analysis

The original final Safety counterexample is closed at design level by the composed object. Atomic acquisition creates and charges a unique lease before lowering or dispatch; owner transfer is compare-and-transfer; the shared generation permit survives awaits and worker boundaries; publication revalidates lease, owner, authority, generation and cursor; and non-killable work remains contained. Racing close, force close, migration, reopen or epoch change after acquisition therefore cannot make the operation unowned, falsely closed, or silently publish stale work.

Other attacks that did not produce additional findings:

- **Raw-plan escape:** the overlay replaces verifier resolution with lexical guarded consumption and prohibits plan-bearing results, closures, caches and reusable claim bags. Derived adapter products remain tagged to the lease and generation.
- **Cancellation and non-killable workers:** cancellation after dispatch is not treated as quiescence. Worker ownership transfers to containment, exact operation identities remain reported even without transaction identities, and force close cannot release the generation permit.
- **A7 knowledge separation:** lease completion does not invent commit knowledge, and transaction reconciliation does not prove worker quiescence. Late commit requests are independently fenced.
- **Migration effects and recovery:** no effect begins before exclusive generation ownership; timeout before effects reopens only with authoritative no-effect proof; failure after effects enters `MIGRATION_INDETERMINATE` and refuses ordinary work until authoritative success, rollback/no-effect, or retirement.
- **Snapshot/cursor integrity:** initial snapshot rows, watermark and registration share one lease and generation; refresh and delivery use finite leases; stale envelopes are discarded rather than relabeled.
- **Idle subscriptions and buffers:** idle subscriptions hold no execution lease. Queued buffers carry finite generation permits that are handed off or invalidated before cutover, so an idle consumer need not block migration forever.
- **Authority expiry:** authority is revalidated before each database effect and after delivery awaits, so a long-lived lease does not become an authority grant.
- **Disclosure:** admitted handles and leases expose neither plans nor claims, and buffered deliveries contain result/cursor metadata rather than authority or plan objects. No new disclosure-scale defect was found.
- **Supersession integrity:** the overlay explicitly replaces the base’s raw-plan return, point revocation, premature close, migration publication, pipeline and live-reuse clauses while preserving the logical algebra, resource profile, result-role prerequisite and retained counterexamples.
- **W1 prerequisite honesty:** current W1 bytes still accept bare `Plan` and cannot report nontransaction operation identities. The overlay correctly treats the combined result/lifetime amendment as separately reviewed and mandatory before execution rather than claiming it already exists.

The two findings arise outside those successful closures: P2-1 conflates local lifecycle draining with global cutover state, while P2-2 leaves the protocol’s initial deployment boundary unable to establish that its supposedly exhaustive participant set is actually exhaustive.

## 3. Risks and next action

Implementation-only proof remains deferred: real advisory locks, interprocess SQLite locking, driver cancellation, crash recovery, thread behavior, database effects and supported-version operation still require their later gates. Those deferrals do not cure the two missing protocol transitions above.

The single next action is one consolidated design correction that separates local close from deployment migration state and adds an explicit legacy-peer activation fence, followed by focused Safety re-verdict on P2-1 and P2-2 against a newly pinned base-plus-overlay tuple. No W1 amendment or implementation should begin while either finding remains open.

