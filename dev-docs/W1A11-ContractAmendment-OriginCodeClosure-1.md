# W1A11-ContractAmendment — ORIGINATING CODE CLOSURE REVIEW 1

**Intended file:** `dev-docs/W1A11-ContractAmendment-OriginCodeClosure-1.md`  
**Review object:** remediation 1, complete 59-file filesystem manifest SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`; controlling amendment SHA-256 `21fec4cc88967464844288d5486c84bfa2e9aa5ebf974ce7f7d178a8334d7b6b`; DRAFT-2 SHA-256 `d5c45f54f4fb1ed6105dd227050229b6a2c35b7517208df7156f36a041d4e58c`; RemPlan SHA-256 `7a8d145e29f5a1c2de01d91a205bf2689b974763795a73046d0c4db39712aa53`.  
**Comparison object:** preserved Revision1 complete 47-file manifest SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8`.  
**Date:** 2026-10-04  
**Axis:** originating Code reviewer, focused closure of all nine original Code P2 findings plus changed-range and adjacent-path attack review. Independent, adversarial and read-only.

**Verdict: NO-GO.** Six original findings are closed. Three remediation roots remain open: P2-1 and P2-6 retain architectural escape paths, while P2-3’s ordinary step grammar is repaired but its required publication/fence closure is incomplete. The latter exposes one new bounded closed-queue registration route. No new architecture root was discovered; the two architectural blockers are residual paths in original architectural roots.

## Prior-finding closure table

| Original finding | Exact counterexample result | Adjacent-path result | Closure status |
|---|---|---|---|
| Code P2-1 — arbitrary Plan-taking continuation | A callable passed directly to `run_plan_step` now refuses before invocation, with zero effects. Forged and cross-issuer consumers also refuse. | A callable accepted by `issue_consumer` executes directly under `ReferenceConsumerIssuer.consume` while its caller frame retains local `plan`. `inspect.currentframe().f_back.f_locals["plan"]` recovered the exact private `Plan`. | **OPEN — architectural residual** |
| Code P2-2 — split parameter sets | `execute`, `consistent_snapshot` and `subscribe` no longer accept a second `parameters` argument. A lease acquired with `tenant=A` produced only the pinned detached `{"tenant": "A"}` value. | Buffer registration, refresh and handoff derive or compare registry-owned frozen parameters. | **CLOSED** |
| Code P2-3 — no closed ordering / duplicate publication | Direct `ACQUIRED` publication, duplicate publication, backward steps, post-publication steps and generic refresh publication now refuse without an extra effect or publication. | Special subscription registration can publish to an already `LOCAL_CLOSED` delivery queue because its publication barrier validates only the subscription lease ancestry, not the target queue fence. | **OPEN — bounded residual in the required publication/fence closure** |
| Code P2-4 — no-effect reopen preserves old authority | After `begin_drain` and `reopen_no_effect`, both the old admitted handle and its already-acquired lease refused. A newly admitted handle acquired successfully. | The coordinator epoch is pinned in admissions, leases and exact generation permits. | **CLOSED** |
| Code P2-5 — unlinked buffered provenance | Copied, wrong-admission and replayed envelopes refused with unchanged counts. Correct dequeue exchanged one buffer permit for one handoff lease. | Registration, digest, parameters, binding, queue, cursor and advancement are compared through both exchanges. | **CLOSED** |
| Code P2-6 — command absent from queued ownership | Wrong command/worker/authorization tuples refuse and preserve the queued lease. Direct generic queued transfer is rejected atomically. | Without switching to the assigned worker task, the dispatching task successfully called `dequeue_worker` using the worker object as an argument and then executed an effect. No trusted current-task-to-worker check exists. | **OPEN — architectural residual** |
| Code P2-7 — privileged kinds default to QUERY | `GOVERNED_MUTATION` and `MIGRATION` are absent from `OperationKind`; the remaining closed map derives QUERY or LIVE exhaustively. | Query/live plan nouns are disjoint at acquisition. | **CLOSED** |
| Code P2-8 — close finalizes from OPEN | Direct `close_outcome` from `LOCAL_OPEN` refused without mutation. After `start_close`, acquisition through the selected ancestry refused while an unrelated peer acquired normally. | Post-close registration targeting a closed queue remains possible; recorded separately under the P2-3 publication-barrier residual. | **CLOSED for the original counterexample** |
| Code P2-9 — proofless activation rollback | `None`, wrong type and stale-epoch recovery evidence refused without state change. Exact binding/epoch proof returned to `UNACTIVATED`, and the used epoch could not be reused. Unused withdrawal also has an exact typed proof shape. | Active activation retains no reset edge; migration recovery has three typed, pinned outcomes. | **CLOSED** |

## Changed-range analysis

The Revision1 and remediation manifests have 47 common paths. Fourteen common paths changed, twelve paths were added, and none were removed.

Changed common paths:

- `docs/adr/A16-admission-lifetime.md`
- `dev-docs/W1A11-ContractAmendment.md`
- `src/garns/backends/contracts/admission.py`
- `src/garns/backends/contracts/generation_reference.py`
- `src/garns/backends/contracts/lifetime.py`
- `src/garns/backends/contracts/lifetime_reference.py`
- `src/garns/backends/contracts/model.py`
- `src/garns/backends/contracts/protocols.py`
- `src/garns/backends/contracts/worker_authority.py`
- `tests/contracts/test_admission_contracts.py`
- `tests/contracts/test_contracts.py`
- `tests/contracts/test_generation_contracts.py`
- `tests/contracts/test_lifetime_contracts.py`
- `tests/contracts/test_worker_authority.py`

The three new implementation files are cohesively scoped:

- `consumers.py` owns sealed consumer identities and closed products.
- `buffer_reference.py` owns registration and buffered-delivery provenance.
- `recovery.py` owns typed activation and migration proof inputs.

The remaining added entries are remediation controls, preserved initial reports/evidence, DRAFT-2 and the prior manifest. The 33 unchanged common entries remained byte-identical.

The split generally improves cohesion. The documented 611-line exception for `lifetime_reference.py` remains within the manager-authorized boundary, but its central registry still owns all special publication target checks. The closed-queue registration defect is a localized missing validation in that state graph, not evidence that a new subsystem is required.

The amended prose currently overclaims three points:

- A16 and the amendment say ordinary registered effects receive no Plan, but the issuer invokes arbitrary effects from a frame containing the raw Plan.
- The amendment says worker tests demonstrate distinct-task consumption, but there is no trusted check that the current task is the assigned worker.
- The amendment describes one publication barrier revalidating local fences, but subscription registration omits the destination queue fence.

## Findings

### [P2-1 residual] Registered arbitrary effects can recover the private Plan from the issuer’s live frame

`src/garns/backends/contracts/consumers.py:86-97` accepts any callable as a registered effect. `consume` at lines 104-129 holds `plan` as a local and directly calls that effect at line 128.

The exact probe registered:

```python
def effect(product):
    leaked.append(inspect.currentframe().f_back.f_locals["plan"])
```

After one legal `LOWER` step, `leaked[0] is fixture["plan"]` was true. This does not require a Plan return value, wrapper, property or forged consumer. The remediation has replaced a direct argument leak with a Python call-stack leak while still running caller-supplied code inside the private-plan lexical boundary.

The direct original `lambda plan: ...` attack is correctly refused, but R1 required lexical containment and specifically rejected merely changing the shape of the return-value guard. Arbitrary caller code must not run on a stack retaining the Plan. Prefer fixed issuer-owned consumer behavior or ensure private-plan processing fully returns before any external effect runs; add current-frame and raised-traceback recovery probes.

**Classification:** residual original architectural root, not a new architecture root.

### [P2-6 residual] The dispatching task can impersonate the assigned worker

`ReferenceLifetimeRegistry.dequeue_worker` at `lifetime_reference.py:279-290` compares the supplied command, worker and authorization identities, then transfers ownership to the supplied worker. `worker_operation_live` at lines 350-368 compares the same supplied objects. `WorkerAuthorizationIssuer.run_effect` at `worker_authority.py:138-178` validates the original context record and stored tuple but never proves that the caller is the assigned worker.

`RuntimeAuthority._validate_worker_source` at `authority.py:76-91` intentionally validates the original context without task impersonation, but no separate trusted worker-source check follows. `RuntimeAuthority.is_current_task` exists and is unused by this path.

The probe kept `current_task` equal to the original dispatching caller, with a distinct `worker` object. It then:

1. dispatched the lease to that worker;
2. called `dequeue_worker(lease, command, worker, authorization)` without changing tasks;
3. called `run_effect` with the stored worker argument.

The callback ran once. Thus an exact tuple is recorded, but the claimed assigned worker is still caller-supplied at consumption. This contradicts the accepted requirement that the exact assigned worker performs the immediate issuer-private check and leaves the original command-ownership attack only partially repaired.

Bind dequeue and effect validation to a trusted current worker/task identity, separately from validation of the original task-bound public context. Add a negative test in which the issuing task presents the otherwise exact worker tuple and observes zero effects and unchanged queued ownership.

**Classification:** residual original architectural root, not a new architecture root.

### [P2-3 residual / new bounded route] Registration publishes to a delivery queue after that queue is CLOSED

`register_subscription` at `lifetime_reference.py:370-395` resolves the target queue but does not check either its `LocalResourceState` or `_queues` state. `_validate_barriers(record)` checks only `record.resources`, which for the registration lease is the subscription ancestry and excludes its delivery-queue child.

The exact probe:

1. hard-closed the delivery queue;
2. finalized it to `CloseKnowledge.CLOSED`;
3. acquired a snapshot-registration lease through the still-open parent subscription;
4. ran `REGISTRATION`;
5. called `register_subscription` with the already-closed queue.

The call succeeded, moved the lease to `PUBLISHING`, returned a registration and incremented `publications` from zero to one.

The normal step grammar, refresh publication barrier and original close-from-OPEN counterexample are repaired. This is a distinct special-publication target-fence omission. Validate the exact queue ancestry plus both local and queue state in the same precommit barrier; a refusal must preserve registration state, lease state, publication count and queue closure.

**Classification:** new bounded correctness route within original R3/R8 scope; no new architecture root.

## Verified repaired invariants

The following remediation behavior survived direct hostile probes:

- sealed admitted handles, leases, generation permits, buffer permits, consumers and registrations reject construction/copy/replay paths;
- parameter values are detached and pinned once;
- query and live operation grammars are disjoint;
- step rank is strictly increasing;
- direct and duplicate generic publication refuse;
- authority expiry, logical revocation and hard fences suppress later generic or refresh publication while retaining uncertain charges;
- graceful deployment drain permits already-pinned old-generation work;
- no-effect reopen invalidates both old handles and old leases;
- rejected owner transfer is validate-before-commit and leaves the old owner usable;
- generation permits require exact issuer identity and owner;
- buffer provenance and permit exchange conserve the global count;
- selected queued buffers are invalidated exactly once during close;
- privileged mutation and migration are outside the read-operation grammar;
- close finalization requires an installed drain or fence;
- activation and migration recovery now require exact typed proof-input shapes;
- active activation has no reset or retirement escape.

These successes do not close the three blocking paths above.

## Verification testimony

At both start and end:

- `W1A11-ContractAmendment-MANIFEST-2.sha256` matched SHA-256 `7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b`.
- All 59 manifest entries verified.
- Amendment, DRAFT-2, RemPlan and RemInputs matched their dispatched hashes.
- RemInputs verified 13/13.
- Original Inputs verified 9/9.
- Control verified 3/3.
- Baseline verified 120/120.
- ReadOnly verified 111/111.
- ProductGuard verified 614/614.
- The archived Revision1 manifest matched SHA-256 `76d4c5a823bda12a00b5b1dfdb4601d5490f0195a43103ff74fe48053daaa9f8` and verified 47/47 from inside its archive.
- Bytecode/cache inventory remained zero.

Independent Python 3.14 execution produced:

- focused contracts: 85/85 passed;
- full suite: 188/188 passed;
- product checks: 5/5 passed;
- `ast.parse`: 23/23 manifest Python files passed.

The inherited SQLite `ResourceWarning`s remained visible during the full suite. No warning filters were used. No source, test, documentation, manifest or workspace file was written; no bytecode, Git/GWZ operation, service, network access, dependency change or helper agent was used.

The green suites do not contain the three reproduced attacks and therefore do not establish closure.

## Required next action

Remediation 1 cannot be accepted. A consolidated correction should:

1. remove caller-controlled code from the raw-Plan call stack and add frame/traceback escape attacks;
2. authenticate the actual assigned worker at dequeue and immediately before each effect, with an issuing-task impersonation regression;
3. include the target delivery queue in the atomic registration publication fence and test draining, fenced and closed queue states with zero publication.

P2-1 and P2-6 are unresolved original architectural roots. The closed-queue registration path is bounded. No new architectural root consumes the remaining architecture allowance, but the current tuple still requires correction and renewed focused closure plus fresh full peer-blind Code/State review before acceptance.

