# W1A11 worker-exit implementation — consolidated remediation 2

**Status:** manager verdict merge for review round 2, and proposed disposition.
**Correction 2 is not authorized.** It is the last correction the implementation
gate allows. Source writes stay stopped until the operator decides.  
**Date:** 2026-10-05  
**Object reviewed:** the corrected candidate after correction 1, MANIFEST-2
`ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720` (128 entries).
The implementation correction count is 1 of 2.

## Round 2 dispatch and filing

- **Two fresh full reviewers** ran the generated prompts `ReviewCode-2-Prompt`
  (`d0e3ea5d…`) and `ReviewState-2-Prompt` (`8a9b8bbd…`).
- **The four round-1 reviewers** were resumed with their context intact, under
  `Reverdict-Prompt` (`2c64f44e…`). Each re-ran its own round-1 counterexamples.
  Both closure reviewers also re-ran the historical roots.
- Models below are taken from the transcripts.

| Filed report | Model | Window (UTC, 2026-10-04) | Verdict |
|---|---|---|---|
| `W1A11-WorkerExitImplementation-ReviewCode-2.md` (fresh full, Code) | claude-opus-5-5 | 15:02:15–15:42:31 | NO-GO: 2 P2, 4 P3 |
| `W1A11-WorkerExitImplementation-ReviewState-2.md` (fresh full, State) | claude-opus-5-5 | 15:02:20–15:46:22 | NO-GO: 2 P2, 2 P3 |
| `W1A11-WorkerExitImplementation-ReviewCode-1-Reverdict.md` | claude-fable-5-1 | 15:02:24–15:22:46 | GO; 1 new P3, 1 P3 partial |
| `W1A11-WorkerExitImplementation-ReviewState-1-Reverdict.md` | claude-fable-5-1 | 15:02:28–15:15:32 | GO |
| `W1A11-WorkerExitImplementation-OriginCodeClosure-1-Reverdict.md` | claude-opus-5-5 | 15:02:32–15:19:47 | NO-GO: 1 new P2 |
| `W1A11-WorkerExitImplementation-OriginStateClosure-1-Reverdict.md` | claude-opus-5-5 | 15:02:36–15:27:24 | NO-GO: 1 new P2, 4 P3 |

Filed SHA-256:

- ReviewCode-2 `b1488cc303170251f46981f2beb1881e5453941a7897bfa93da879c1aed857ab`
- ReviewState-2 `fdceadec6d24d27f8707e8b70acccae11f415f370f614f866d0b86e26c11b029`
- ReviewCode-1-Reverdict `c9872c4c7de7398cb8a286398e8b1f181a46aeffedf4aa23852c206a4f66bb54`
- ReviewState-1-Reverdict `f10e3ef952469982663ca5485a8a953edf7c477ee67ef09ecb919876ec040eb9`
- OriginCodeClosure-1-Reverdict `134305d82cae745cd54abd16f27f2df0f3d806f2465813d076b61d2653f98ee5`
- OriginStateClosure-1-Reverdict `43428228184450d8f93c08eb631951d07653be1a3528918a167d9fff60e0a0e4`

Each report is its subagent's final message, byte for byte. For the resumed
reviewers, that is the final message of the resumed run. The reports were held
outside the product tree until all six finished, and each confirms that no other
current-round report existed in `dev-docs/` during its run.

Manager notes on the testimony (verified; report text unchanged):

- ReviewState-2's final message opens with one line before its report heading
  ("The tuple held at END and I have read every control. Here is my report.").
  It is filed with that line.
- Disclosed procedural deviations, none touching the reviewed bytes:
  - ReviewState-2 wrote three listing files to the session scratchpad.
  - ReviewCode-2 ran one read-only `find` to locate the skill.
  - Both closure reviewers report that the harness compacted their context
    between rounds.
- After the last report the manager re-verified MANIFEST-2 (128/128), every
  guard, and the Revision1 archive (117/117). No bytecode was found, and the
  tree held only the expected changes.

## Verdict merge

**NO-GO.** There are no P0 or P1 findings.

**Every round-1 blocker is closed.** All 28 round-1 P2 findings were closed by
the reviewer who raised each one, each re-running the original counterexample
on MANIFEST-2. Each counterexample still reproduces on the Revision1 archive.

| Round-1 report | P2 closed | P3 closed |
|---|---|---|
| ReviewCode-1 | 8/8 | 6/7 (P3-7 partial) |
| ReviewState-1 | 6/6 | 3/3 |
| OriginCodeClosure-1 | 7/7 | 3/3 |
| OriginStateClosure-1 | 7/7 | 3/3 |

Both fresh full reviewers also independently re-ran IR1–IR19 and found every
root closed.

**Round 2 found three new blocking roots, IR21–IR23.** None is a regression in
behavior. Each either reproduces on the Revision1 archive or has a trigger that
already existed there. All reviewers classify them as bounded source repairs
needing no accepted-design, ownership or compatibility change, and none as
architectural. No STOP is triggered.

**Historical stopped roots on MANIFEST-2:**

| Root | Status |
|---|---|
| Failed FIFO | Closed (OriginCode, OriginState, both full) |
| Neutral refresh | Closed (OriginState, both full) |
| Stale phase proof | Closed (OriginState, both full, State re-verdict) |
| Worker exit | Original counterexample closed; root open through IR22 and IR23 |
| Participant lifecycle | Original reproductions A and B closed; root open through IR21 |

**Blind convergence.**
- IR21 is the strongest signal this lane has produced. Five reviewers on both
  models and both axes found it independently: both fresh full reviewers, both
  closure reviewers, and the Code re-verdict.
- IR24 was found by three reviewers. IR25 and IR26 were each found by two.

**Severity rule** (unchanged): the higher rating stands until the raiser
verifies closure.
- IR21: four reviewers rated it P2, the Code re-verdict P3. It is P2.
- IR22: rated P2 by ReviewCode-2. ReviewState-2 and round-1 ReviewCode-1 (D6)
  noted it below the bar. It is P2.

## Finding map

| Report | ID → root |
|---|---|
| ReviewCode-2 | P2-1→IR21 · P2-2→IR22 · P3-1→IR25 · P3-2→IR24 · P3-3→IR26 · P3-4→IR29 |
| ReviewState-2 | P2-1→IR21 · P2-2→IR23 · P3-1→IR24 · P3-2→IR25 |
| ReviewCode-1-Reverdict | P3-8→IR21 · P3-7 (partial)→IR30 |
| ReviewState-1-Reverdict | none open |
| OriginCodeClosure-1-Reverdict | P2-8→IR21 |
| OriginStateClosure-1-Reverdict | P2-8→IR21 · P3-4→IR24 · P3-5→IR27 · P3-6→IR26 · P3-7→IR28 |

## Blocking roots — disposition and closure

### IR21 — A runtime can join after its local close has begun (P2)

Mapped: ReviewCode-2 P2-1, ReviewState-2 P2-1, OriginCodeClosure-1-Reverdict
P2-8, OriginStateClosure-1-Reverdict P2-8, ReviewCode-1-Reverdict P3-8.

**Defect.** The failure runs in four steps:
1. `open_lifetime`/`join_runtime` never check the registry's runtime resource.
2. `start_close(runtime)` on a registry that is not yet joined witnesses nothing.
3. A later join is then accepted.
4. `close_outcome` commits `LOCAL_CLOSED` and retires admissions, then calls
   `witness_local_close`, which refuses. Every retry refuses again.

The closed runtime stays a JOINED member. Every later frozen attempt requires its
acknowledgement, so `begin_migration` and no-effect reopen refuse. Once the
registry object is gone, nothing can remove the member. The only recovery is an
undocumented second `start_close`, which also relabels RETIRED admissions back to
DRAINING.

The trigger already existed on Revision1. There, close returned CLOSED and left a
JOINED ghost; correction 1 changed the symptom to commit-then-raise.

Design: §9 (join validates the local open resource; closing before activation is
`UNJOINED → LEFT` and a later join refuses; a closed runtime is never a permanent
acknowledgement obligation); overlay §4 and A16 (validate-then-commit); IR9 (close
validates before mutating).

**Correction.**
- `open_lifetime` refuses once the registry's runtime resource has left
  `LOCAL_OPEN` or a runtime close has begun. A registry that was never joined and
  whose close has begun proceeds only `UNJOINED → LEFT` through `close_unjoined`.
- `close_outcome` establishes every coordinator precondition before its first
  local mutation. A refusal leaves resources, admissions and membership unchanged.
- `_admit` refuses when the runtime is not `LOCAL_OPEN`.
- A repeated `start_close` never relabels RETIRED or REVOKED admissions
  (ReviewState-2 §3).

**Closure.**
- Close begun on an unjoined registry, graceful and hard: `open_lifetime` refuses,
  with membership `None` and the coordinator's participants, join serial and
  activation unchanged.
- `close_outcome` then returns CLOSED via `close_unjoined`, and a later join still
  refuses.
- A later attempt requires exactly the live members, and both `begin_migration`
  and no-effect reopen proceed.
- Property: any `close_outcome` refusal leaves resources, admissions and
  membership unchanged.
- A repeated close is a no-op for admissions.

### IR22 — The executor façade's `revoke` reaches containment without authority (P2)

Mapped: ReviewCode-2 P2-2. ReviewState-2 §3 and round-1 ReviewCode-1 §3 (D6)
recorded the same route below the bar.

**Defect.**
- `registry.worker_issuer.revoke(authorization)` →
  `_revoke_worker_authorization` → `_contain_lease`, with no task, worker or
  receiver check.
- `dispatch_worker` hands the authorization to the receiver, so any holder can
  use it.
- A third task can therefore refuse a queued operation, kill a running command's
  success path, close a quiescent result, or retire a delivery's registration.
- Nothing in the registry calls `revoke` any more.
- It reproduces on Revision1.
- After correction 1 it is the only route into the containment routine that
  skips presentation validation.

Design: §5.2 allows exactly three trusted cancellation sources. A caller never
supplies an owner. §7 row 1 requires refusal before mutation. IR4 says
presentation refusals never reach the routine.

**Correction.**
- Preferred: remove `revoke` from the façade, together with the uncalled
  `_revoke_worker_authorization`.
- Otherwise: through the trusted providers, require that the current task is the
  exact assigned worker or the live receiver before any mutation.
- Either way, add a source rule that enumerates every public method reaching
  `_contain_lease` and requires each one to validate a receiver, an assigned
  worker, or a trusted observation or barrier first.

**Closure.**
- Run a third-task revoke, or the route that replaces it, at QUEUED, RUNNING_IDLE,
  EFFECT_IN_FLIGHT (from inside the effect), SUCCESS_PENDING and
  QUIESCENT_SUCCESS, on EXECUTE and on a running two-range delivery.
- Each refuses with the full state vector unchanged.
- The source rule passes.

### IR23 — `run_worker_cleanup` claims its step only after the action returns (P2)

Mapped: ReviewState-2 P2-2. OriginCodeClosure-1-Reverdict §3 noted a related
residual: cleanup running while the effect frame is still on the stack.

**Defect.** The cleanup step is validated, then the trusted action runs, and
`next_cleanup_step` advances only in `finally`. A cleanup action that re-enters
for the same step therefore:
- runs step 1 twice;
- skips step 2;
- still reaches success exit and publication.

This reproduces on Revision1; the IR7 rewrite did not close it.

Design:
- §5.1: the wrapper performs every trusted cleanup before success exit.
- §5.3: the cleanup schedule is finite and ordered, and success exit comes only
  after cleanup returns.
- §4.2: re-entry must refuse without consuming anything.
- IR7: validate the next step before the containment scope.

**Correction.**
- Claim the step atomically with its validation, before invoking the action. A
  claimed step counts as consumed whether the action returns or raises.
- Refuse any cleanup call while that command's cleanup action is on its stack.
- Refuse effect reservation once cleanup has begun (ReviewState-2 §3).

**Closure.**
- A hostile cleanup action re-entering for the same step, and separately for the
  next step, refuses with the vector unchanged.
- The actions run exactly `[1, 2]`.
- Success exit refuses, and publications stay 0, until both steps have run.
- Effect reservation during or after cleanup refuses.

## Non-blocking roots

P3s never block. Correction 2 is the last allowed, so every extra change is risk
that cannot be corrected again. The manager therefore recommends fixing only the
P3s that are small and sit on paths correction 2 already touches. The rest are
recorded and assigned to W3, like the existing W1 P3.

| Root | Mapped | Defect | Recommendation |
|---|---|---|---|
| IR24 | ReviewCode-2 P3-2, ReviewState-2 P3-1, OriginStateClosure-1-Reverdict P3-4 | History discard keeps `active_command_serial`; `lease_facts` reports `(…, 1, 0)` and a late delivery-stop setup raises `IndexError` | **Fix in correction 2**: clear the serial at discard; a post-terminal delivery stop refuses or replays |
| IR25 | ReviewCode-2 P3-1, ReviewState-2 P3-2 | A non-worker's refused late `worker_exit_success` fills the late-return diagnostic | **Fix in correction 2**: validate the current worker before recording |
| IR26 | ReviewCode-2 P3-3, OriginStateClosure-1-Reverdict P3-6 | Unconsumed initial-snapshot candidates, with their frozen rows, outlive terminal registrations | **Fix in correction 2**: discard at terminalization, in the same function as IR24 |
| IR29 | ReviewCode-2 P3-4 | The formal seam declares `mark_indeterminate` without its exit `recover_migration` | **Fix in correction 2**: declare it and add it to the source rule |
| IR30 | ReviewCode-1-Reverdict P3-7 (partial) | No test drives issuing-task `run_effect` after a distinct worker has dequeued | **Fix in correction 2**: test only |
| IR27 | OriginStateClosure-1-Reverdict P3-5 | Cancel or task loss after acceptance returns the accepted command's SUCCESS receipt | **Defer to W3** unless it is trivially safe: it changes return values on paths outside the three blockers |
| IR28 | OriginStateClosure-1-Reverdict P3-7 | Close, barrier and revocation scan every retained terminal lease and retired registration, so work grows with history | **Defer to W3**: live indexes are invasive; the design bounds the commit path, not these scans |

Below the bar and open, recorded so they are not lost:

- **Refused design-legal edge** (ReviewState-2 §3). Design §11's
  `CURRENT × NONE → RETIRED × NONE` is refused under IR17 pending
  decommissioning authority. This needs an operator decision before W3 or W4
  rely on binding non-reuse from CURRENT.
- **A7 truth is caller-supplied** (ReviewCode-2 §3). A7 unresolved identities
  reach `close_outcome` from its caller, so the registry cannot verify A7 truth.
- **Spurious diagnostic** (ReviewState-1-Reverdict and ReviewState-2). Double
  containment of a worker-backed refresh sets a spurious cancel diagnostic. It
  can be fixed inside IR22's containment work if trivial.
- **Misleading refusal text** (ReviewState-1-Reverdict). A wrong-task
  `prepare_delivery_publication` gets the publication-precondition message rather
  than a presentation refusal.
- **IR20** (G10) stays outside the allowlist, as decided.

## Correction shape and boundary

This is one consolidated patch. The boundary is unchanged:
- **Writes:** the brief's 23 allowlisted paths. `worker_authority.py`, which IR22
  touches, is one of them.
- **Ownership:** `lifetime_reference.py` stays the sole lease and worker owner.
- **Read-only:** ReadOnly 741, Inputs 31 and the Legacy maps stay byte-identical.
- **Tests:** retained tests are adapted, never deleted.
- **Forbidden:** helpers, Git/GWZ, network and `tools/check.py`.

The three blockers are small and local:
- IR21: the open, admit and close ordering in `lifetime_reference.py`, with a
  possible witness marker in `generation_reference.py`.
- IR22: the façade surface in `worker_authority.py` plus one registry method.
- IR23: one entry and the reservation guard.

## Next steps

1. **Operator decisions:**
   - Authorize correction 2, the last allowed.
   - Choose the builder. The recommendation is to continue the same Fable
     builder with its context intact under a new pinned BuilderPrompt-3, as the
     lane's precedent has one builder own consecutive corrections. A fresh Fable
     builder is the alternative.
   - Confirm the P3 split above.
2. **Before any write, the manager:**
   - preserves MANIFEST-2's exact files under
     `W1A11-WorkerExitImplementation-Revision2/`, so MANIFEST-2 verifies from
     inside that archive;
   - pins this plan, the six round-2 reports and the controls in a RemInputs-2
     map.
3. **The builder** writes the single patch, stops writing and returns DRAFT-3.
4. **The manager** reproduces the gates and the failing-before evidence on the
   Revision2 archive, verifies every guard, and pins MANIFEST-3.
5. **Round 3** runs because IR22 changes the worker façade, an interface:
   - fresh full Code and State reviews;
   - re-verdicts by every round-2 reviewer who raised an open finding:
     ReviewCode-2, ReviewState-2, OriginCodeClosure-1-Reverdict,
     OriginStateClosure-1-Reverdict and ReviewCode-1-Reverdict.
6. **The cap.**
   - After correction 2 there is no third correction.
   - If round 3 is GO/GO with every P0–P2 closed by its raiser, the object is
     accepted: internal contracts and reference tests only.
   - If round 3 reports any new P0–P2, the lane stops, and redesign or accept is
     the operator's decision.
