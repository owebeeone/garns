# W1A11 worker-exit implementation — round 3 merge and correction 3

**Status:** manager verdict merge for review round 3, and disposition.
**Correction 3 was authorized by the operator on 2026-10-05** ("authorize a
one-line correction 3 for the regression"; "ok, go ahead with correction 3").
It is an operator exception to the exhausted two-correction gate and is limited
to one source line. The operator also set three economy rules, all applied here:
- the builder is a fresh Sonnet agent;
- no Fable agent is resumed;
- at most two reviewers per round. This rule is now recorded in the review-loop
  skill.

**Date:** 2026-10-05  
**Object reviewed:** MANIFEST-3 `9a9f8b2a8e56b0411ebb7948d91aabf58a1459adbcfdbdac02efec75f6b36af9`
(141 entries).

## Round 3 filing

Eight reviews ran on MANIFEST-3. Each report is filed byte for byte as its
subagent's final message (for resumed agents, the final message of the resumed
run). Models are taken from the transcripts. All windows are 2026-10-04 UTC.

| Report | Model | Window (UTC) | Verdict |
|---|---|---|---|
| `…-ReviewCode-3.md` (fresh full, Code) | claude-opus-5-5 | 23:04–23:36 | NO-GO: P2-1, 2 P3 |
| `…-ReviewState-3.md` (fresh full, State) | claude-opus-5-5 | 23:04–23:42 | NO-GO: P2-1, 2 P3 |
| `…-ReviewCode-2-Reverdict.md` | claude-opus-5-5 | 23:05–23:16 | NO-GO: P2-3 |
| `…-ReviewState-2-Reverdict.md` | claude-opus-5-5 | 23:05–23:16 | NO-GO: P2-3 |
| `…-OriginCodeClosure-1-Reverdict-2.md` | claude-opus-5-5 | 23:05–23:16 | NO-GO: P2-9 |
| `…-OriginStateClosure-1-Reverdict-2.md` | claude-opus-5-5 | 23:18–23:35 | NO-GO: P2-9 |
| `…-ReviewCode-1-Reverdict-2.md` | claude-fable-5-1 | 23:04–23:15 | GO |
| `…-ReviewState-1-Reverdict-2.md` | claude-fable-5-1 | 23:12–23:24 | GO |

SHA-256:

| Report | SHA-256 |
|---|---|
| ReviewCode-3 | `188c46684f97dd299c19e1b55780db8c589c4c64335dcd0183bc05186747a07a` |
| ReviewState-3 | `9a9637bc11a1ce32b3ac88f2c1f00548401e574f19adcab610d34bcd0d9625c2` |
| ReviewCode-2-Reverdict | `34ab2d754025c3cf7988a9188120bb79898c72437a6e8756232ea8b70694e083` |
| ReviewState-2-Reverdict | `a023cdb346cb346911ab87acbd3869d23c727bcca34f86727e252d0dcd2c34bf` |
| OriginCodeClosure-1-Reverdict-2 | `018fd7a223227e2bd4e631a559351a0558d56de56d5cdd5ab6601520061a134f` |
| OriginStateClosure-1-Reverdict-2 | `0cfbf6985c40f8240a989e3769cf39a8d341206aaf6309375489c9fef3c896b4` |
| ReviewCode-1-Reverdict-2 | `4e7a7d881b66357ffe14864389436b7b2f18c76de9f0dfe26b096d771e8f55e4` |
| ReviewState-1-Reverdict-2 | `b5faa906a59a6bc6297c38eb2cf467785fd6f21b34252d37d6bcd07b3ac991fd` |

**Blindness.** The reports were held outside the tree until all eight had
finished. Each confirms that no current-round report existed during its run.

**Disclosures.**
- ReviewCode-3 wrote one probe script to the session scratchpad, outside the tree.
- OriginStateClosure-1-Reverdict-2 saw the ReviewState-3 prompt's filename in a
  search result and did not open it.

**Tuple.** After the last report, the manager re-verified MANIFEST-3 (141/141),
every guard and both archives.

**Reviewer count.** Eight reviewers in one round exceeded the review-loop default
of two. From correction 3 on, the operator's two-reviewer cap applies.

## Verdict merge

**NO-GO.** There are no P0 or P1 findings.

**One new P2 root, IR31.** Six reviewers found it independently on both models
and both axes. It is a regression introduced by correction 2's IR23 cleanup
claim. The two GO re-verdicts did not probe a success exit made from inside a
cleanup action.

**Every P0–P2 raised in rounds 1 and 2 is closed on MANIFEST-3 by its raiser:**

| Raiser | Closed |
|---|---|
| ReviewCode-1-Reverdict-2 | 8 P2 and all P3, including P3-7 and P3-8 |
| ReviewState-1-Reverdict-2 | 6 P2 and 3 P3 |
| OriginCodeClosure-1-Reverdict-2 | 11 findings |
| OriginStateClosure-1-Reverdict-2 | 8 P2 |
| ReviewCode-2-Reverdict | 2 P2 and 4 P3 |
| ReviewState-2-Reverdict | 2 P2 and 2 P3 |

IR27 and IR28 stay open as operator-deferred W3 items. They do not block.

**Historical roots.**

| Root | Status |
|---|---|
| Participant lifecycle | Closed (OriginCode, both full reviews) |
| Neutral refresh | Closed |
| Phase proof | Closed |
| Worker exit | Original counterexample closed; root open through IR31 |
| Failed FIFO | Original sequences closed; IR31 can defeat the cleanup-failure cause, settling a failed head as delivered |

**New P3 roots.** These do not block and are assigned to W3:
- **IR32.** The IR22 source rule checks that an authority marker is present, not
  that it comes first. `setup_reference_initial_snapshot` contains a lease before
  any receiver check. Raised by ReviewCode-3 P3-1 and ReviewState-3 P3-2.
- **IR33.** The cleanup-provider lookup comes before the step claim, so a
  re-entrant provider runs a step twice and skips the next. Raised by
  ReviewCode-3 P3-2; the defect predates correction 2.
- **IR34.** `revoke_generation` relabels RETIRED admissions to REVOKED. Raised by
  ReviewState-3 P3-1; the defect predates correction 2.

The below-bar observations in the round-3 reports also go to W3 as recorded
there. The design-legal `CURRENT × NONE → RETIRED` edge remains an operator
question.

## Finding map (round 3)

| Report | ID → root |
|---|---|
| ReviewCode-3 | P2-1→IR31 · P3-1→IR32 · P3-2→IR33 |
| ReviewState-3 | P2-1→IR31 · P3-1→IR34 · P3-2→IR32 |
| ReviewCode-2-Reverdict | P2-3→IR31 |
| ReviewState-2-Reverdict | P2-3→IR31 |
| OriginCodeClosure-1-Reverdict-2 | P2-9→IR31 |
| OriginStateClosure-1-Reverdict-2 | P2-9→IR31 · P3-5→IR27 (open, deferred) · P3-7→IR28 (open, deferred) |
| ReviewCode-1-Reverdict-2 | none open |
| ReviewState-1-Reverdict-2 | none open |

## IR31 — disposition (correction 3)

**Defect.** `run_worker_cleanup` claims each step (`next_cleanup_step += 1`,
`cleanup_in_progress = True`) before its action runs. `worker_exit_success`
still gates only on `next_cleanup_step <= cleanup_steps`. So a success exit
requested from inside the final cleanup action is accepted. If the action then
raises, the failure is only a diagnostic and the operation publishes SUCCEEDED.
On an iterator handoff, the failed head settles as delivered and the successor
proceeds. Revision2 and Revision1 both refuse this sequence.

**Design.** Success exit comes only after every trusted cleanup step has
returned (§5.1, §5.3). A cleanup failure with no earlier primary exit is the
primary FAILURE (§5.3, §8). Re-entrant calls refuse (§4.2).

**Correction: exactly one source line.** In `worker_exit_success`, the cleanup
gate becomes:

    if command.cleanup_in_progress or command.next_cleanup_step <= command.spec.cleanup_steps:

This check comes before every mutation in that function.

**Closure tests.**
1. **EXECUTE, raising action, K = 1 and K = 2.** An in-frame success request
   refuses with the full vector unchanged. When the action then raises:
   - the primary exit is FAILURE;
   - the command is CONTAINED under the containment owner;
   - publications stay 0;
   - after the stop, the operation completes REFUSED with count 0.
2. **EXECUTE, non-raising action.** The in-frame request refuses. Success after
   the action returns succeeds exactly once and publishes once.
3. **Two-range iterator handoff, raising action.** The in-frame request
   refuses. The handoff reaches RETIRING_HANDOFF. Cursors stay (2, 0) and the
   successor never dequeues. Non-success settlement returns `RefetchRequired`
   with count 0.

**Out of scope for this one-line correction:**
- IR32–IR34;
- IR27 and IR28;
- the stop fixture that ignores an active cleanup frame;
- `worker_exit_failure` called inside a cleanup action, which already fails
  closed.

## Re-check: two reviewers only

Under the operator's two-reviewer rule, only the round-3 Code and State full
reviewers are resumed, with context intact. They give a focused re-verdict on
MANIFEST-4:
1. They verify IR31's closure tests.
2. They confirm that the one-line delta changes nothing else.
3. They issue the full-review verdict for MANIFEST-4.

The other four reviewers that raised IR31 are not resumed. Their identical
findings close through the same counterexample, verified by the two
re-checkers. This is an operator-directed economy deviation from "closed by the
reviewer who raised it".

Every other finding closed on MANIFEST-3 carries over to MANIFEST-4, for two
reasons:
- The delta only adds a refusal while a cleanup action is running. Removing an
  accepted transition cannot reopen a closed counterexample.
- Both re-checkers re-run the full suites.

**Acceptance.** GO from both re-checkers on MANIFEST-4 accepts the object as
internal contracts and reference tests only. The following then carry to W3:
- IR20, IR27, IR28 and IR32–IR34;
- the below-bar items recorded in the reports.

The `CURRENT × NONE → RETIRED` edge goes to the operator.

## Correction 3 boundary

- **Builder:** one fresh Sonnet subagent, briefed by
  `W1A11-WorkerExitImplementation-BuilderPrompt-4.md`.
- **Allowlist:** three paths:
  - `lifetime_reference.py`, the one line only;
  - `test_worker_exit_contracts.py`, new tests only;
  - the implementation record, one entry.
- **Manager preparation:**
  - MANIFEST-3's exact files are archived under
    `W1A11-WorkerExitImplementation-Revision3/`;
  - `W1A11-WorkerExitImplementation-RemInputs-3.sha256` pins this plan, the
    prompt, the eight reports, the archived manifest, MANIFEST-3 and the
    ReadOnly guard.
- **Manager verification:**
  - the gates on all four interpreters;
  - failing-before evidence against Revision3;
  - MANIFEST-4.
