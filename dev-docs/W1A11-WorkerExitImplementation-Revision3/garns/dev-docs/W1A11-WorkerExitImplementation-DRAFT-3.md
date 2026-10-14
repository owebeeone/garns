# W1A11-WorkerExitImplementation — DRAFT 3 (correction 2 builder testimony)

Header:
- Date: 2026-10-05.
- Model: Claude Fable 5.1 (`claude-fable-5-1`), the same builder that wrote correction 1, context intact.
- Object: the corrected candidate at MANIFEST-2 `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720` (128 entries), corrected under `W1A11-WorkerExitImplementation-RemPlan-2.md`; prompt `dab49348089adbbd6fb97860895f6c9278422e90da281c9f6d592dec48840dd9` and RemInputs-2 `cb19ae72328dcca1f5504603d213e289ddaef8726427a3c4e8c2efc333a3e79a` verified before reading and unchanged at END.
- STOP-WRITES is in effect: the last writes were the implementation record and A16; the verification matrix and every END guard ran after them, and only read-only commands followed. Nothing here is self-accepted or claimed closed; closure belongs to the reviewers who raised each finding. This was the last correction the gate allows.

## Changed paths

Eight allowlisted paths changed; fifteen allowlisted paths are byte-identical to MANIFEST-2; no file was created or written outside the allowlist.

| Path | SHA-256 before (MANIFEST-2) | Lines | SHA-256 after | Lines |
|---|---|---:|---|---:|
| `src/garns/backends/contracts/lifetime_reference.py` | `4843cc540cae56513b1ded4bc892729d480a867b4801600156dea65e428b5a6c` | 2009 | `803a3008b52f62df926250b2f0528e7e15f186d584c4d67e4286b2d4162e4723` | 2074 |
| `src/garns/backends/contracts/worker_authority.py` | `773ec0fdd5014b72fed232527c8f1864237a1196712b71ff52bbc951abafb301` | 143 | `9107b814f147b1289fcea16fb191a3bf90dc98cfe9ed3d1cbfced87892d9c875` | 144 |
| `src/garns/backends/contracts/snapshot_reference.py` | `dfc22a849374b7d6cd9629a818233ddabc42f932368322ae166da53f85788e26` | 181 | `77472ac6cdd18cb5fd52eddee43630a74c6e7831e724e10f1f901d7be5274df3` | 186 |
| `src/garns/backends/contracts/lifetime.py` | `955470918f92bd958485c9d2e343baf04d3b301cb41f42562306f1e2f63bea41` | 344 | `5986ce273ac1f1289dd4d8c0e37f82c942717a0182105f0f01fd0ebf664ea10f` | 346 |
| `tests/contracts/test_worker_exit_contracts.py` | `ea24704070df17b4040884ebccbdff017b663160a8713290e72a5c61727962d6` | 2682 | `189982b4f40d7bfb0537e44bc6d2600baf4c118e85a18c947a3679d62691c551` | 3200 |
| `tests/contracts/test_contract_source_rules.py` | `d9124894a6434e7020a59047e039ee7eefcda4fb1c73d2934a031e1df5651187` | 340 | `85cadb62ef572cba729aefca53ff126b761aafd1885f0f0c238859c2b9a70711` | 413 |
| `docs/adr/A16-admission-lifetime.md` | `9090265032135e333be3c382f8c1a8af8d43d5c38f05c9fb63a0109467b19baa` | 192 | `0dc3d64726b7d698bcea627e54ce9adab512a01c3149e494903f61c054995d90` | 208 |
| `dev-docs/W1A11-WorkerExitImplementation.md` | `16fb98655a752b968dae942b0d1f77efe88aec57753ae7643496a0160e7b7c8c` | 222 | `a15a937bda3b11267e9a1bd4315d823f4e7b8a2f14f2f9570126904c6099193e` | 262 |

Byte-identical to MANIFEST-2: `admission.py` (`4bc15e20…`), `authority.py` (`4925e694…`), `consumers.py` (`6b940605…`), `buffer_reference.py` (`a3f28263…`), `generation_reference.py` (`5c8d2278…`), `migration_reference.py` (`ba5df136…`), `protocols.py` (`786bb1ae…`), `values.py` (`139faf5b…`), `__init__.py` (`38948b2c…`), `test_admission_contracts.py` (`2babc923…`), `test_lifetime_contracts.py` (`c17be038…`), `test_worker_authority.py` (`3d5ddf4c…`), `test_generation_contracts.py` (`c917b7c9…`), `test_contracts.py` (`6ef5b9a5…`), `docs/adr/README.md` (`a33f43f7…`, candidate-status wording still accurate; no history link added since the manager files this testimony).

## Root-by-root implementation

Line ranges are in the final files. `LR` = `lifetime_reference.py`, `WE` = `test_worker_exit_contracts.py`, `SR` = `test_contract_source_rules.py`.

**IR21 — implemented (blocking).** `LR` `_require_runtime_open` (325–337) refuses once `_runtime_close_begun` is set or any RUNTIME resource has left `LOCAL_OPEN` (`LOCAL_RESOURCE_DRAINING`/`LOCAL_RESOURCE_FENCED` by state); `open_lifetime` (251–258) calls it before `join_runtime`, so a never-joined closing registry proceeds only `UNJOINED -> LEFT` through `close_unjoined`; `_admit` (299–315) calls it after the membership check; `start_close(runtime)` (1548–1584) sets the close-begun flag and relabels admissions only along legal edges (ADMITTED -> DRAINING/REVOKED, DRAINING -> REVOKED; RETIRED and REVOKED never relabel); `close_outcome` (1586–1626) validates every local transition and performs the coordinator witness (`close_unjoined` or `witness_local_close`) before its first local mutation, so a refusal leaves resources, admissions and membership unchanged. Observer `admission_state(handle)` (339–345) added for the testimony. Design §9 (join validates the local open resource; closing before activation is `UNJOINED -> LEFT`; a closed runtime is never a permanent acknowledgement obligation), overlay §4 and A16 validate-then-commit, RemPlan IR9. Counterexamples: ReviewCode-2 P2-1, ReviewState-2 P2-1, OriginCodeClosure-1-Reverdict P2-8 (J1–J8), OriginStateClosure-1-Reverdict P2-8, ReviewCode-1-Reverdict P3-8 (N1), ReviewState-2 §3 admission relabel → `WE.JoinAfterCloseTests` (2728–2847): graceful and hard close on an unjoined registry → join refuses with membership `None`, live membership and activation unchanged, admission refuses, `close_outcome` → CLOSED, later join refuses, later attempt requires only the live member and both no-effect reopen and `begin_migration` proceed; barrier-missing refusal and an injected coordinator-witness refusal (trusted-setup hostile coordinator) leave resources, admissions and membership unchanged; repeated graceful/hard close never relabels RETIRED or REVOKED admissions.

**IR22 — implemented (blocking), preferred route.** `revoke` and its `_revoke` slot are removed from `WorkerAuthorizationIssuer` (`worker_authority.py` 121–144; the façade exposes only `run_effect` and `context_owner`); `_revoke_worker_authorization` is deleted from `LR`, and the registry constructs the façade with two callables (`LR` 243–245). Source rule `SR.test_public_containment_entries_validate_authority_first` (170–205) computes the transitive callers of `_contain_lease` within the registry, pins the exact public set (`CONTAINMENT_ENTRIES`, 68–80: 23 entries) and requires each to carry a receiver, assigned-worker, trusted-observation or barrier validation marker (`AUTHORITY_MARKERS`, 59–67) in the method or its direct private helpers; `SR.test_worker_entries_have_no_callback_or_caller_identity_override` (125–168) additionally pins that the façade has no `revoke` and that `_revoke_worker_authorization` no longer exists. Design §5.2 (three trusted cancellation sources), §7 row 1. Counterexample: ReviewCode-2 P2-2 (ReviewState-2 §3, ReviewCode-1 D6) → `WE.FacadeRouteTests` (2849–2940): at QUEUED, RUNNING_IDLE, EFFECT_IN_FLIGHT (from inside the effect), SUCCESS_PENDING and QUIESCENT_SUCCESS on EXECUTE and on a running two-range delivery, a third task drives the route if present plus the other cancel entries and the full vector is unchanged; the façade exposes exactly `run_effect` and `context_owner`. Retained adaptation: `TerminalAbsorptionTests` (`WE` 1620–1623) replaces its `worker_issuer.revoke` entry with the structural check that no revoke route exists, keeping the attack.

**IR23 — implemented (blocking).** `run_worker_cleanup` (`LR` 697–746) refuses while `cleanup_in_progress` is set, then claims the step atomically with its validation (`next_cleanup_step += 1`, `cleanup_begun = True`, `cleanup_in_progress = True`) before the fixed action runs, clearing the in-progress marker in `finally`; a claimed step is consumed whether the action returns or raises. `run_worker_effect` (582–590) refuses reservation once `cleanup_begun` is set. New `_WorkerCommandRecord` fields `cleanup_begun`, `cleanup_in_progress` (154–155). Design §5.1, §5.3, §4.2. Counterexample: ReviewState-2 P2-2 (OriginCodeClosure-1-Reverdict §3 residual) → `WE.CleanupClaimTests` (2942–3066): hostile same-step and next-step re-entry refuse with the vector unchanged, actions run exactly `[1, 2]`, success exit refuses and publications stay 0 until both steps have run; a raising action still consumes its claimed step; effect reservation refuses from inside the cleanup action and after cleanup with ordinals unchanged.

**IR24 — implemented.** `_discard_operation_history` (1986–2010) clears `active_command_serial`; `setup_reference_delivery_stop` (1466–1481) replays the recorded observation on a settled retirement or refuses, never reaching the discarded ledger. ReviewCode-2 P3-2, ReviewState-2 P3-1, OriginStateClosure-1-Reverdict P3-4 → `WE.TerminalTombstoneTests.test_every_terminal_route_clears_the_active_serial` (publication, `complete_contained`, queue removal, delivery success, neutral commit, both refresh dispositions report `(…, None, 0)`), `test_late_delivery_stop_setup_after_settlement_replays_without_indexerror`.

**IR25 — implemented.** `worker_exit_success` (642–673) validates the exact current assigned worker before recording the late-return diagnostic; a non-worker refuses `WORKER_AUTHORITY_INVALID` without mutation. ReviewCode-2 P3-1, ReviewState-2 P3-2 → `WE.LateReturnAuthorityTests` (3166–3196): receiver and third-task late success leave `worker_exit_facts` unchanged; the worker's late return fills the slot once and is idempotent.

**IR26 — implemented.** `_LeaseRecord.initial_candidate` (127) is set by `setup_reference_initial_snapshot` (972–1008; a second setup on the same operation discards the first), cleared by `register_subscription` after consumption (1058), and discarded by `_discard_operation_history` through the new `ReferenceSnapshotRegistry.discard_initial` (`snapshot_reference.py` 138–141). ReviewCode-2 P3-3, OriginStateClosure-1-Reverdict P3-6 → `TerminalTombstoneTests.test_unconsumed_initial_candidates_die_with_their_operation` (weak-reference proof after five abandoned registrations; a later registration still delivers).

**IR29 — implemented.** `SharedGenerationCoordinator.recover_migration(proof: "MigrationRecoveryProof") -> None` declared (`lifetime.py` 19, 328); `COORDINATOR_METHODS` and `MEMBERSHIP_AND_PROOF_METHODS` include it (`SR` 36–51), so `CoordinatorProtocolTests` now proves a stub lacking `recover_migration` does not conform and the registry refuses it. ReviewCode-2 P3-4.

**IR30 — implemented (test only).** `WE.WorkerEntryValidationTests.test_issuing_task_cannot_run_an_effect_after_a_distinct_worker_dequeued` (1848–1875): receiver and third task get a refusal, zero effects and an unchanged vector; the worker runs the effect once. ReviewCode-1-Reverdict P3-7 residual.

**IR27, IR28 and IR20: untouched.** IR27 (post-acceptance cancel/task-loss return value) and IR28 (close/barrier/revocation scans over retained outer records) are deferred to W3 per the operator decision and were not changed; `semantic.py` and `tools/check.py` were not written. Also untouched, as recorded below the bar in RemPlan-2: the refused design-legal `CURRENT × NONE -> RETIRED × NONE` edge, caller-supplied A7 identities, the spurious double-containment cancel diagnostic, and the wrong-task `prepare_delivery_publication` refusal text.

## Retained-test adaptations

One retained test changed: `TerminalAbsorptionTests.test_every_entry_leaves_a_terminal_lease_unchanged_from_every_task` (`WE` 1620–1623) — its `worker_issuer.revoke(authorization)` entry is replaced by `assertFalse(hasattr(registry.worker_issuer, "revoke"))`, keeping the attack (no authorization holder has a containment entry) now that the route is removed (IR22). One retained source rule changed: `test_worker_entries_have_no_callback_or_caller_identity_override` drops `_revoke_worker_authorization` from its exact authorization-entry set and adds the façade-surface assertions. No test was deleted; every correction-1 test still runs unchanged in behavior (173 → 187 focused).

## Failing-before evidence

Method: `tests/__init__.py` (read-only) forces the live `src`, so the six behavioral contract modules plus `test_contract_source_rules.py` (for its constants) were copied into a scratchpad package with empty `__init__.py` files and run with `PYTHONPATH=<abs>/dev-docs/W1A11-WorkerExitImplementation-Revision2/garns/src:<lark>` and `-B` on Python 3.14; `garns.__file__` resolved into the Revision2 archive. Result on Revision2: `Ran 172 tests … FAILED (failures=26, errors=4)`, 13 distinct tests; the same 172 pass on the corrected tree (`OK`). Classification by final exception:

| Test | Revision2 | Class |
|---|---|---|
| IR21 `JoinAfterCloseTests.test_join_refuses_once_local_close_has_begun_and_close_proceeds_unjoined_to_left` | `ContractRefusal not raised` (join accepted after close began) | behavioral |
| IR21 `test_close_outcome_refusals_leave_resources_admissions_and_membership_unchanged` | `AttributeError: … no attribute 'admission_state'` | API-absence (new observer) |
| IR21 `test_repeated_close_never_relabels_retired_or_revoked_admissions` | `AttributeError: … 'admission_state'` | API-absence (new observer) |
| IR22 `FacadeRouteTests.test_third_task_has_no_containment_route_at_any_stage` | vector diffs at RUNNING_IDLE, EFFECT_IN_FLIGHT, SUCCESS_PENDING, QUIESCENT_SUCCESS (the third-task `revoke` contained the command); at QUEUED the revoke terminalized the operation so the vector read raised `authorization is unavailable` | behavioral |
| IR22 `test_facade_exposes_only_effect_and_context_owner` | `True is not false` (`revoke` present) | interface shape (route still present) |
| IR22 adapted `TerminalAbsorptionTests.test_every_entry…` | `True is not false` (`revoke` present) | interface shape |
| IR23 `CleanupClaimTests.test_reentrant_cleanup_refuses_and_actions_run_exactly_once_in_order` | `RecursionError` (same-step re-entry accepted, so the hostile action re-enters without bound) | behavioral |
| IR23 `test_effect_reservation_refuses_during_and_after_cleanup` | `ContractRefusal not raised` | behavioral |
| IR24 `TerminalTombstoneTests.test_every_terminal_route_clears_the_active_serial` | `(1, 0)` active serial on a terminal lease | behavioral |
| IR24 `test_late_delivery_stop_setup_after_settlement_replays_without_indexerror` | assertion on the late stop setup (`IndexError` path) | behavioral |
| IR25 `LateReturnAuthorityTests.test_non_worker_late_success_leaves_the_diagnostic_slot_unchanged` | vector diff (diagnostic recorded for a non-worker) | behavioral |
| IR26 `test_unconsumed_initial_candidates_die_with_their_operation` | candidates alive after terminalization | behavioral |
| IR29 `CoordinatorProtocolTests.test_reference_coordinator_conforms_and_partial_stubs_do_not` | stub lacking `recover_migration` conforms | behavioral (seam) |

Every blocking root has at least one behavioral failing-before test (IR21: the join test; IR22: the third-task route test; IR23: both cleanup tests), each written against observers that exist on MANIFEST-2 (`membership`, `membership_state`, `close_outcome`, `lease_facts`, `worker_cleanup_step`, `worker_exit_facts`, `worker_ordinals`, `vector`). `IR23`'s claimed-step-consumed test and `IR30`'s test pass on both trees (the behavior already held) and are kept as regressions. Source rules are exempt (they read live files).

## Test inventory and counts

New tests: 13 in `test_worker_exit_contracts.py` (`JoinAfterCloseTests` 3, `FacadeRouteTests` 2, `CleanupClaimTests` 3, `TerminalTombstoneTests` 3, `LateReturnAuthorityTests` 1, `WorkerEntryValidationTests` +1; 67 → 80 test methods) and 1 in `test_contract_source_rules.py` (10 → 11), total 14. Focused suite 173 → 187; full suite 276 → 290; `tools/check_product.py` 5 PASS before and after.

## Verification

Commands, from the product root, with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`, per interpreter: `-B -m unittest discover -s tests/contracts -t .`, `-B -m unittest discover -s tests -t .`, `-B tools/check_product.py`, plus `ast.parse` of the six changed `.py` files.

| Interpreter | ast.parse | focused | full | product |
|---|---|---|---|---|
| `…/cpython-3.11…/bin/python3.11` (3.11.14) | 6 ok | Ran 187 OK | Ran 290 OK (0 ResourceWarning lines) | 5 PASS |
| `…/cpython-3.12…/bin/python3.12` (3.12.12) | 6 ok | Ran 187 OK | Ran 290 OK (0) | 5 PASS |
| `/opt/homebrew/bin/python3.13` (3.13.12) | 6 ok | Ran 187 OK | Ran 290 OK (112 inherited SQLite ResourceWarning lines, visible, unfiltered) | 5 PASS |
| `/opt/homebrew/bin/python3.14` (3.14.3) | 6 ok | Ran 187 OK | Ran 290 OK (140, visible) | 5 PASS |

`tools/check.py`, `compileall` and `py_compile` were not run; no Git/GWZ, network, install, service or helper subagent; scratch files only under the session scratchpad. MANIFEST-1 was not checked against live source.

Guards START (before any write) and END (after the last write): MANIFEST-2 self-hash `ee441c18da74c30a6afc2fdc6ac1ef07f6e39990fecf113e98f34c1f81200720` both times; `shasum -a 256 -c` MANIFEST-2 128 OK at START, 120 OK + 8 FAILED at END; Inputs 31, Baseline 20, ReadOnly 741, Legacy 115/71/111/614, AcceptanceEvidence 13, RemInputs 18, RemInputs-2 22 OK both times; Revision1 archive MANIFEST-1 117 OK and Revision2 archive MANIFEST-2 128 OK both times; `.pyc`/`.pyo`/`__pycache__` count 0 both times. The 8 MANIFEST-2 live entries failing at END are exactly the 8 changed allowlisted paths in the table above: `dev-docs/W1A11-WorkerExitImplementation.md`, `docs/adr/A16-admission-lifetime.md`, `src/garns/backends/contracts/{lifetime,lifetime_reference,snapshot_reference,worker_authority}.py`, `tests/contracts/{test_contract_source_rules,test_worker_exit_contracts}.py`. Nothing outside the allowlist mismatched.

## Limits and open items

- Interface change for round 3: `WorkerAuthorizationIssuer` lost its `revoke` member and its constructor takes two callables; no module outside `contracts/` constructed or called it, but any future executor that expected a façade cancel must use the three trusted sources. The new `admission_state` observer, like `lease_facts` and `worker_cleanup_step`, is a provisional closed observer (labels only) for W3 Surface.
- IR21's `close_outcome` ordering performs the coordinator witness before the local mutations rather than querying a separate precondition; in this single-threaded reference that is validate-then-commit, and a hostile coordinator stub proves a refusal mutates nothing. A production coordinator must keep the witness refusable only before any local commit.
- Items needing operator direction, carried from RemPlan-2 and unchanged here: the refused design-legal `CURRENT × NONE -> RETIRED × NONE` edge (needs a decision before W3/W4 rely on binding non-reuse from CURRENT); IR27 and IR28 deferred to W3; A7 truth remains caller-supplied to `close_outcome`.
- Below the bar and unchanged: the spurious cancel diagnostic on double containment of a worker-backed refresh; the wrong-task `prepare_delivery_publication` refusal text; retained outer terminal-lease, observation and retirement records (unbounded by design); the queue relabel by the migration barrier.
- Deterministic single-process reference evidence only; no concurrency, durability, crash, provenance, PostgreSQL, activation or W3-name claims. IR20 remains open outside the write boundary. Round-3 full Code and State review and the re-verdicts of ReviewCode-2, ReviewState-2, OriginCodeClosure-1-Reverdict, OriginStateClosure-1-Reverdict and ReviewCode-1-Reverdict remain mandatory; no further correction is available after this one.
