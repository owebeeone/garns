# W1 Registry/Containment Redesign — CODE-AXIS REVIEW

**Review object:** all 26 files in `dev-docs/W1-RegistryContainmentRedesign-MANIFEST.sha256`, manifest SHA-256 `fbd11e908f97938b23ad8870e86e703976e7859660b38058ac9188593d13eeff`; operator-authorized W1 registry/containment replacement design; controlling draft `dev-docs/W1-RegistryContainmentRedesign-DRAFT.md`, SHA-256 `d5802a9ed79df01716c956922488e7f53336b23bbadba4f6608a5c4289ec33bd`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`, authorized pre-initial-commit SHA-pinned review mode; redesign brief SHA-256 `afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d`; controlling implementation plan SHA-256 `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`; W1 execution brief SHA-256 `1d13f70330c254791ffbcdb65690b3c4343a82e1b09b2dc7de061331f231c344`  
**Date:** 2026-10-03  
**Axis:** architecture, interfaces, call graphs and compatibility reality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one new bounded P2 finding blocks acceptance. Both final stopped-object counterexamples are closed, but `WorkerCommitFence` does not enforce uniqueness or terminal non-reuse of a begun transaction identity. Its set/dictionary representation can collapse distinct begun commands or strand a reused identity after an apparently successful repeated resolution. I pre-commit to GO on a revision that resolves P2-1 as specified, provided the original counterexample and retained regressions pass and no new blocking defect is introduced.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on redesigned tree | Status |
|---|---|---|---|
| Code-3 P2-1 / initial Code P2-5 | Replace claim-bearing caller context with an empty identity handle and issuer-owned registry | `TrustedContext` has only `__weakref__`; no claim, issuer or registry field is reachable from the handle. Canary-bearing claims remain only in `RuntimeAuthority._issued`. `repr`, `str`, `dir`, member inspection, slots, `vars`, dataclass conversion, copy/deepcopy and pickle/reduction attacks disclose no canary and create no registered authority. Exact-instance, cross-issuer, reconstruction and reinitialization attacks refuse. | **CLOSED** |
| State-3 P2-1 / initial State P2-7 | Prevent pre-commit completion from erasing commit-requested work; require identity-matching terminal resolution | `finish_without_commit()` refuses a commit-requested identity. `resolve()` retains `INDETERMINATE`, consumes only identity-matching terminal outcomes, and `CommitOutcome` rejects a committed revision from another qualified scope. Matching committed and aborted outcomes close; conflicting repeated resolution refuses. | **CLOSED** |

## Changed-range analysis

The historical source bytes are represented by `dev-docs/W1-MANIFEST-3.sha256`; no unavailable Git diff was invented. A sorted checksum-inventory comparison showed that exactly the six operator-authorized paths changed:

- `docs/adr/A11-trusted-context.md`
- `docs/adr/A8-sqlite-async.md`
- `docs/adr/README.md`
- `src/garns/backends/contracts/authority.py`
- `src/garns/backends/contracts/state.py`
- `tests/contracts/test_contracts.py`

The other 20 manifested files are byte-identical to the stopped W1 tuple. The complete scoped path inventory under `docs/adr`, `src/garns/backends/contracts`, and `tests/contracts` exactly matches the 26-file redesign manifest.

The authority changed range implements the required empty-handle/issuer-registry boundary without weakening runtime clock, epoch, task-owner, scope, capability, invalidation, or post-await delivery checks.

The worker changed range closes the prior erasure route, but introduces or exposes one **NEW BOUNDED, NON-ARCHITECTURAL root cause**: `WorkerCommitFence.begin()` accepts an identity already active or terminal, while `_begun` is a set and `_resolved` permanently retains terminal outcomes. This is a localized lifecycle-validation and state-transition defect; it does not require replacing the registry/containment architecture.

---

## 0. Evidence base

I read and checked:

- workspace `AGENTS_GWZ.md`, product `AGENTS.md`, and `dev-docs/CurrentProgramCheckpoint.md`;
- the complete review-loop skill and canonical reviewer template;
- `W1-RegistryContainmentRedesign-Brief.md`, `W1-RegistryContainmentRedesign-DRAFT.md`, `W1-STOP.md`, `W1-ReviewCode-3.md`, `W1-ReviewState-3.md`, both W1 remediation plans, and the W1 execution brief;
- the controlling implementation plan, provider-neutral seam amendment and acceptance, D6a/D7/D8 and D4/D6b decisions, governed-write scope amendment and acceptance, W0 acceptance, and `docs/PRODUCT_LAYOUT.md`;
- all 26 manifested files: A1–A15 and the ADR index, all eight contract modules, and both contract-test files;
- retained `TypeRef` and relevant plan/value semantics needed to verify the integrated contract.

The controlling digests matched the prompt: implementation plan `11268a…`, provider-neutral seam `b99c43…`, D6a/D7/D8 `079517…`, D4/D6b `94b9e5…`, governed-write amendment `d68cb0…`, its acceptance `dac75f…`, W1 execution brief `1d13f7…`, redesign brief `afc66a…`, draft `d5802a…`, and redesign manifest `fbd11e…`.

At both start and end:

```text
fbd11e908f97938b23ad8870e86e703976e7859660b38058ac9188593d13eeff  dev-docs/W1-RegistryContainmentRedesign-MANIFEST.sha256
d5802a9ed79df01716c956922488e7f53336b23bbadba4f6608a5c4289ec33bd  dev-docs/W1-RegistryContainmentRedesign-DRAFT.md
afc66a9f025404c5f8e4dc6803619d45f0d61e9a1174f3c209e80f618d4de59d  dev-docs/W1-RegistryContainmentRedesign-Brief.md
```

Both executions of:

```sh
shasum -a 256 -c dev-docs/W1-RegistryContainmentRedesign-MANIFEST.sha256
```

reported all 26 paths `OK`. The scoped-files-versus-manifest comparison produced no differences.

The prescribed focused suite passed:

```text
.......................................
----------------------------------------------------------------------
Ran 39 tests in 0.014s

OK
```

Pure in-memory Python 3.14 `-B` probes used the prescribed cached dependency and `src` paths, wrote no bytecode or files, and contacted no service.

The context reduction probe produced:

```text
reduce RAISE TypeError a class that defines __slots__ without defining __getstate__ cannot be pickled
getstate RETURN None
object_reduce RAISE TypeError a class that defines __slots__ without defining __getstate__ cannot be pickled
dict? False
slots ('__weakref__',)
dir-canary False
```

The worker identity probes produced:

```text
duplicate_begin_close_true CloseOutcome(knowledge=CLOSED, unresolved=())
duplicate_begin_close_false ValueError unresolved close must name transactions
reuse_close_true CloseOutcome(
    knowledge=UNRESOLVED,
    unresolved=(TransactionIdentity(scope=QualifiedDeployment(world='w', deployment='d'),
                                    client_id='same'),))
```

---

## 1. Findings

### [P2-1] The worker fence accepts duplicate and terminally reused transaction identities that its state representation cannot track correctly

**Classification:** **NEW BOUNDED, NON-ARCHITECTURAL root cause.**

**Location:** `src/garns/backends/contracts/state.py:215-275`, specifically `_begun` and `_resolved` at lines 220–222, unconditional set insertion in `begin()` at lines 224–227, early return for an identical prior terminal outcome at lines 262–266, and removal of the sole set entry at lines 273–275. The missing cases are also absent from `tests/contracts/test_contracts.py:389-443`.

**Violated invariant:** The redesign brief requires final outcome accounting for every begun identity, no loss of containment, and repeatable shutdown/reconciliation. A worker fence must either reject a second active or terminally reused identity before work begins, or represent every distinct begun operation. It cannot accept multiplicity that its state cannot distinguish, and a repeated terminal resolution cannot leave active work stranded.

**Reproduction 1 — concurrent duplicate begin collapses containment:**

```python
fence.begin(tx)
fence.begin(tx)  # accepted; set still contains one entry
fence.request_commit(tx)
fence.resolve(tx, known_committed)
fence.close_outcome(quiescent=True)
```

The second `begin(tx)` is silently collapsed by `_begun: set[TransactionIdentity]`. One resolution removes the only set entry, and `close_outcome(True)` returns `CLOSED`, although the model accepted two begun commands and recorded only one terminal outcome.

If the caller correctly reports nonquiescence because the second command is still running, `close_outcome(False)` attempts `UNRESOLVED` with an empty identity tuple and raises `ValueError` instead of returning a typed containment result.

**Reproduction 2 — reuse after a terminal outcome becomes permanently unresolved:**

```python
fence.begin(tx)
fence.request_commit(tx)
fence.resolve(tx, known_committed)

fence.begin(tx)                 # accepted after terminal resolution
fence.request_commit(tx)
fence.resolve(tx, known_committed)
```

The second identical resolution returns early because `_resolved[tx]` already equals the outcome. It therefore does not remove the newly added `_begun` entry. `close_outcome(True)` remains `UNRESOLVED` forever for that identity. A conflicting second result instead raises against the old terminal result, also without a defined begin-time refusal.

**Impact:** A conforming SQLite worker built against this reference model can falsely claim terminal closure after accepting two commands under one identity, throw instead of returning the required typed unresolved outcome, or strand a reused identity indefinitely. This breaks containment, recovery, and diagnosability at the exact shutdown boundary the redesign is intended to freeze.

The durable publication contract’s idempotent transaction identity does not excuse this behavior: replaying an already terminal transaction may return its cached durable result, but it must not be admitted as a fresh worker command whose lifecycle the fence cannot represent. Concurrent reuse likewise must refuse before work begins.

**Required correction:** Define and enforce the fence’s identity admission rule in `begin()`:

- refuse if the identity is already in `_begun`;
- refuse terminal reuse when the identity exists in `_resolved`, unless `begin()` is redesigned to return the cached terminal outcome without admitting new work;
- use a stable typed refusal or a specifically documented invalid-state exception;
- preserve idempotent repeated `resolve()` for the already completed operation without letting it consume or strand a later operation;
- ensure `close_outcome(False)` always returns a valid typed outcome for every accepted nonquiescent state rather than constructing `UNRESOLVED` with no identities.

No multiplicity counter is needed if duplicate and terminal reuse are rejected at admission.

**Closure/regression test:** Add both executed sequences above. Assert that a duplicate active `begin(tx)` refuses before state change; a `begin(tx)` after terminal resolution either refuses or returns the already recorded result without adding `_begun`; repeated identical resolution of the original operation remains idempotent; conflicting resolution refuses; and every reachable `close_outcome(False)` returns a valid `UNRESOLVED` naming all accepted unfinished identities. Repeat with equal client IDs in distinct qualified scopes to confirm that valid cross-scope identities remain separate.

---

## 2. Invariant analysis

The following adversarial attacks did not produce additional findings:

- **Caller-handle containment:** `TrustedContext` stores no instance state other than weak-reference support. Ordinary attribute and slot traversal from the handle does not reach claims, issuer, registry, task owner, scope, capability, validity, or context identity.
- **Canary nondisclosure:** principal, writer, world, deployment, context identity, capability, validity and epoch canaries did not appear through `repr`, `str`, `dir`, member diagnostics, instance slots, copying, serialization, reduction, `vars`, or dataclass helpers.
- **Counterfeit authority:** an unregistered `object.__new__(TrustedContext)` is an exact-class lookalike but fails issuer lookup. A handle from another issuer also fails. Copy, deepcopy, pickle and caller reinitialization do not produce registered authority.
- **No issuer backreference:** the handle contains no route to `RuntimeAuthority` or its `_issued` registry. The issuer remains trusted host-owned state, consistent with the explicit non-sandbox boundary.
- **Detached claim normalization:** issuance rebuilds `TrustedClaims`; capability containers are frozen, qualified scope is reconstructed, string subclasses normalize to plain strings, validity is finite, and invalidation epoch is a nonnegative exact integer.
- **Runtime-owned provenance:** current time, epoch and genuine task identity come from setup-injected providers. Ordinary validation cannot supply substitutes; task ownership compares by object identity.
- **Post-await delivery:** `AuthorityBoundIterator.__anext__()` validates before reading and after the awaited read. Close suppresses delivery, renewal closes the old iterator, and the subscription protocol exposes no second authority-free iteration method.
- **Original worker erasure counterexample:** `finish_without_commit()` rejects any identity in `_commit_requested`; it accepts only a matching `KNOWN_ABORTED` outcome for pre-commit work.
- **Outcome-bound resolution:** wrong transaction identity refuses before mutation; a committed revision must match the transaction’s qualified scope; `INDETERMINATE` leaves `_begun` and `_commit_requested` intact; matching committed or aborted outcomes remove containment; repeated identical terminal resolution is idempotent and conflicting resolution refuses.
- **Late-commit fence:** after `start_shutdown()`, a begun pre-commit command cannot newly request commit. Failure to quiesce retains its identity.
- **Retained W1 protocol shape:** the full async backend surface remains present for query, snapshot, governed mutation, commit/reconciliation, schema inspection, migration, ledger replay, subscription binding and lifecycle operations. Unsupported capabilities remain pre-effect refusals rather than optional missing methods.
- **Prior authority and ownership fixes:** runtime-owned freshness, exact task ownership, immutable values, plan-origin binding, migration effect coupling, closed cancellation phase/evidence grammar, commit-ordered publication, and authority-bound subscription delivery remain represented and covered by passing regressions.
- **Conditional-boundary hygiene:** the modified Python contract files introduce no conditional compilation attributes or C-style control-flow bodies to which the workspace brace rule applies.

Explicit deferrals remain deferrals: these pure contracts do not prove arbitrary host-process secrecy, real worker/thread behavior, restart durability, PostgreSQL or SQLite execution, driver cancellation, database fault cuts, migration atomicity, external capture, W2 algebra, or the W3 public surface.

---

## 3. Risks and next action

The remaining risk below the finding bar is evidentiary: `WeakKeyDictionary` behavior and the worker fence are still pure in-memory reference models. Passing tests cannot establish real runtime containment, durable reconciliation, or database behavior; those proofs remain assigned to later gates.

The single next action is a bounded correction to P2-1 in `WorkerCommitFence.begin()` and its regression tests, followed by a same-axis re-verdict on a newly pinned complete 26-file tuple. The correction must preserve both now-closed stopped-object counterexamples and all existing authority, cancellation, publication, migration, delivery, and immutable-value regressions.
