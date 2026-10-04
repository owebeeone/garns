# Garns v9-6 W1 — State-axis review

**Review object:** all 22 files listed by `dev-docs/W1-MANIFEST.sha256`, manifest SHA-256 `5e04e8ece03d3a98d0bef293b3140a74c86cf967ff63fedc2a19359973d05bed`; controlling `dev-docs/W1-DRAFT.md` SHA-256 `4680ff38273b1958a06b59cfa75b347ff209f88256c7aeefde436f902006d6f5`  
**Baseline:** pre-initial-commit, SHA-pinned draft/interface review under the inherited plan §15/W0 exception; no committed-tree or Git-landing claim  
**Date:** 2026-10-03  
**Axis:** durable-state semantics and adversity. Independent, adversarial and read-only. The Code axis ran independently in parallel; nothing here relies on it.

**Verdict: NO-GO** — seven P2 findings block acceptance. Six are architectural root causes and one is a bounded reference-model correction. I pre-commit to GO on a revision that resolves P2-1 through P2-7 as specified, provided focused regression tests reproduce and close each counterexample without introducing a new architectural root cause.

## 0. Evidence base

At both start and end, I verified:

- `dev-docs/W1-MANIFEST.sha256` has SHA-256 `5e04e8ece03d3a98d0bef293b3140a74c86cf967ff63fedc2a19359973d05bed`.
- `dev-docs/W1-DRAFT.md` has SHA-256 `4680ff38273b1958a06b59cfa75b347ff209f88256c7aeefde436f902006d6f5`.
- `shasum -a 256 -c dev-docs/W1-MANIFEST.sha256` reports all 22 entries `OK`.
- The complete inventory under `docs/adr/**`, `src/garns/backends/contracts/**` and `tests/contracts/**` matches the manifest with no unlisted source file.

I verified the controlling digests for the W1 execution brief, governed-write scope amendment, parent plan, provider-neutral amendment and both operator-decision records. I read the current checkpoint, scope acceptance, W0 acceptance, product layout, all controlling documents, all A1–A15 ADRs and index, all four contract source files, and both contract test files.

The permitted focused suite passed:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src \
  /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .

Ran 25 tests in 0.001s
OK
```

Pure counterexamples established that:

- `copy.copy(TrustedContext(...))` produces a distinct context that validates successfully.
- A mutable `set` passed as `TrustedClaims.capabilities` can acquire `GOVERNED_WRITE` after issuance and still validate.
- Publishing the same `TransactionIdentity` twice assigns revisions 1 and 2.
- Mutating a nested list after constructing `Snapshot` changes the snapshot’s retained rows.

The manager’s neutral verification supplement reports full 128-test reproduction on Python 3.11.14, 3.12.12 and 3.14.3 plus passing product checks. That supersedes only the builder’s interpreter-availability limitation; it does not close the contract defects below.

## 1. Findings

### [P2-1] Cancellation alone is encoded as authoritative abort

**Classification:** architectural root cause.

**Location:** `src/garns/backends/contracts/state.py:37-40`; asserted by `tests/contracts/test_contracts.py:74-75`; contradicted by `docs/adr/A7-isolation-retry.md:11-17` and the W1 execution brief’s requirement that cancellation not imply rollback.

**Violated invariant:** `KNOWN_ABORTED` requires authoritative database evidence. Task cancellation is not a database outcome.

**Counterexample:** a statement has begun and the task is cancelled before a commit request. Rollback or protocol quiescence then loses its connection or exceeds its cleanup deadline. Calling `cancellation_outcome(transaction, False)` nevertheless returns `KNOWN_ABORTED`, even though rollback was never acknowledged and the implementation may not know whether the transaction remains active or was committed by an internal/autocommit path.

**Impact:** callers may reuse the durable client identity or retry work on the false premise that no effect survived, creating duplicate or conflicting effects.

**Required correction:** replace the `commit_requested: bool` shortcut with a closed event/evidence grammar. Pre-commit cancellation must remain indeterminate until an authoritative rollback/abort boundary is observed; only verified rollback or an authoritative abort record may yield `KNOWN_ABORTED`.

**Closure test:** simulate cancellation followed independently by successful rollback, rollback acknowledgement loss, connection loss and cleanup timeout. Only the verified-rollback trace may return `KNOWN_ABORTED`; all unresolved traces must remain `INDETERMINATE`.

### [P2-2] The commit-publication reference model permits duplicate durable identities to publish twice

**Classification:** bounded reference-model correction backed by an architectural idempotency obligation.

**Location:** `src/garns/backends/contracts/state.py:89-115`, especially `publish_committed()` at lines 106-110; missing from `tests/contracts/test_contracts.py:116-155`. A4 requires durable identity, reconciliation and uniqueness at `docs/adr/A4-revision-publication.md:7-18`.

**Violated invariant:** retrying or reconciling the same qualified client transaction identity must resolve the original outcome, not allocate a second revision.

**Counterexample:** invoke `publish_committed(TransactionIdentity(scope, "same"))` twice. The model returns revisions 1 and 2. There is no identity ledger or duplicate disposition.

**Impact:** the executable reference model blesses duplicate governed effects/revisions after acknowledgement loss, defeating the central durable-identity recovery guarantee.

**Required correction:** model publication by transaction identity. First publication records identity-to-revision atomically; later publication of that identity must return the same committed outcome or refuse a conflicting payload, never increment the revision.

**Closure test:** duplicate same-identity publication before and after simulated acknowledgement loss must return one revision and leave the publication cursor advanced exactly once. A conflicting second payload under the same identity must fail closed.

### [P2-3] A structural copy of a trusted context retains full authority

**Classification:** architectural root cause.

**Location:** `src/garns/backends/contracts/model.py:265-281`; the purported copy test at `tests/contracts/test_contracts.py:164-167` constructs a fresh counterfeit token rather than copying the context. The accepted provider-neutral amendment requires cloning and structural copies to refuse before effect at lines 47-58.

**Violated invariant:** possession of a public context object must not allow an ordinary caller to manufacture another authoritative context by structural copying.

**Counterexample:** `clone = copy.copy(context)` creates a distinct `TrustedContext`; because `_issuer_token` is copied by reference, `clone.validate(original_issuer, owner, now, epoch)` succeeds.

**Impact:** the frozen A11 mechanism does not satisfy its accepted anti-cloning contract. Identity/provenance checks that depend on genuine context instance identity can be bypassed by ordinary Python copying.

**Required correction:** use a runtime-owned issuance registry or equivalent uncopyable capability identity checked independently of copied fields. Explicit copy, replace, reconstruction and serialization operations must refuse or produce non-authoritative objects.

**Closure test:** exercise `copy.copy`, `copy.deepcopy`, `dataclasses.replace`, constructor reconstruction and pickle round trips. Every resulting distinct object must fail validation before query, transaction, subscription or governed effect; only the exact live issued capability may validate.

### [P2-4] Trusted claims are only nominally immutable and permit post-issuance capability escalation

**Classification:** architectural root cause.

**Location:** `src/garns/backends/contracts/model.py:253-278`; `TrustedClaims` is frozen but performs no defensive normalization or validation. The accepted provider-neutral amendment requires an immutable claim snapshot and post-issuance mutation refusal.

**Violated invariant:** scope, capabilities, writer identity, validity and ownership cannot change after issuance.

**Counterexample:** construct `caps = {Capability.QUERY}`, issue `TrustedClaims(..., capabilities=caps, ...)`, then execute `caps.add(Capability.GOVERNED_WRITE)`. Python type annotations do not enforce `frozenset`; validation still succeeds and the context now carries write authority.

**Impact:** a once-genuine read-only context can gain governed-write authority after issuance without renewal or invalidation.

**Required correction:** defensively validate and normalize every claim at construction, including conversion to immutable owned values and validation of nonempty identities, finite validity, valid epochs and qualified scope. Issuance must retain no caller-owned mutable object.

**Closure test:** pass mutable sets and mutable/hostile subclasses for every claim container, mutate originals after issuance, and verify the issued snapshot is unchanged. Attempts to alter any normalized claim must fail before effect.

### [P2-5] Connection-level reads and snapshot creation have no trusted-context authority path

**Classification:** architectural root cause.

**Location:** `src/garns/backends/contracts/protocols.py:34-42`. `AsyncConnection.execute()` and `consistent_snapshot()` accept no `TrustedContext`; `AsyncBackend.open()` and `AsyncPool.acquire()` also establish no context binding. In contrast, `begin()` and `subscribe()` accept a context. The accepted amendment requires public execute, transaction and subscription operations to derive or constrain scope and capability through A11.

**Violated invariant:** every database operation must check the request-bound context at entry and before each database effect or protected delivery; caller parameters cannot become authority.

**Counterexample:** acquire a connection using only deployment scope and deadlines, then call `execute(plan, parameters)` or `consistent_snapshot(plan, parameters)` with no context and no owner/epoch evidence. The frozen protocol leaves an implementation no contract-level way to enforce `QUERY`, scope ownership, expiry or invalidation for those operations.

**Impact:** implementations can conform structurally while permitting unauthenticated reads or snapshots and while bypassing zero-staleness context checks.

**Required correction:** either pass `TrustedContext` through every authority-bearing operation or freeze an explicit authenticated request/connection binding whose ownership, scope, capability and validity are rechecked at the required barriers. The protocol must make unauthenticated execution impossible rather than relying on undocumented ambient state.

**Closure test:** runtime-checkable conforming fakes must be unable to execute or snapshot without a genuine context. Missing, expired, invalidated, copied, wrong-owner and wrong-scope contexts must refuse before adapter invocation.

### [P2-6] Snapshot and delivery rows remain mutable through nested result values

**Classification:** architectural root cause in value semantics.

**Location:** `src/garns/backends/contracts/model.py:212-220` and `230-250`. Both constructors make only a shallow dictionary copy and wrap only the top-level mapping.

**Violated invariant:** a delivered row state is an immutable record of state at its declared durable cursor.

**Counterexample:** construct a snapshot from `{"x": []}`, then append to the original list. `snapshot.rows[0]["x"]` changes after construction while `snapshot.cursor` remains fixed. JSON arrays/objects are ordinary database result values, so this is not an exotic type violation.

**Impact:** retained snapshots and deliveries can silently mutate after publication and falsely claim later data as state at an earlier revision. Replay/fold comparisons and audit evidence become unstable.

**Required correction:** define and enforce an immutable result-value algebra, recursively freeze supported structured values, or encode them into immutable canonical values before constructing `Snapshot` and `Delivery`. Reject unsupported mutable values.

**Closure test:** nested list/dict/set and mutable custom-value inputs must either be recursively detached into immutable canonical values or refuse. Mutating every source object afterward must leave snapshots and deliveries byte-for-byte/equality stable.

### [P2-7] SQLite forced close can return while an abandoned worker may still perform effects

**Classification:** architectural root cause.

**Location:** `docs/adr/A8-sqlite-async.md:8-12`, combined with `docs/adr/A3-async-lifecycle.md:9-13` and `docs/adr/README.md:93-96`.

**Violated invariant:** bounded shutdown must not allow new database effects after shutdown has returned, and failure to quiesce must fail closed without inventing an outcome.

**Counterexample:** a worker begins a long-running or hung SQLite statement. Cancellation requests interruption, but the worker does not reach a transaction boundary before the shutdown deadline. A8 then says close “abandons/discards the worker connection.” Python cannot kill that running thread; the worker still owns the connection and can resume, finish the statement or commit after close has returned.

**Impact:** callers can observe a terminally closed runtime and then receive late database effects. Those effects may lack live publication, authorization rechecks or a usable reconciliation owner.

**Required correction:** freeze an executable shutdown fence. No worker may autonomously commit after the runtime marks shutdown; begun work must run inside an explicitly controlled transaction whose final commit requires a still-live runtime authorization/fence. If a worker cannot quiesce, close must expose a typed unresolved shutdown state and retain containment/reconciliation ownership rather than claiming terminal closure. Process isolation is another admissible design if hard termination is required.

**Closure test:** block a worker before statement completion and before commit, expire cleanup/shutdown deadlines, return from forced close, then release the block. Assert no new effect or commit can occur after the reported terminal boundary; any already-requested commit must remain durably reconcilable and never be reported aborted merely because shutdown returned.

## 2. Invariant analysis including failed attacks

The following attacks did not produce additional findings:

- A4’s prose correctly rejects pre-commit sequence allocation, assigns revisions under a per-scope durable publication lock and treats wakeups only as hints. Reverse request/commit order and rollback gaps are described in the correct fail-closed direction.
- A4/A7 correctly distinguish row absence from authoritative abort and retain `INDETERMINATE` for in-flight or missing reconciliation evidence.
- `reconcile()` rejects a committed revision from another deployment scope and does not attach revisions to unresolved outcomes.
- Delivery cursors enforce one scope and generation and reject labeling state observed through revision 6 as if it were triggered at revision 8.
- A6 closes the snapshot/register race by registering before releasing the repeatable snapshot and then scanning durable revisions after the snapshot cursor. Refresh labels rows with the actual high-water mark rather than the earliest wakeup revision.
- Queue capacity is derived from the authored live bound, overflow becomes an explicit refetch handshake, and neutral refreshes advance the internal cursor without fabricating a batch.
- A12’s three migration classes preserve the accepted effect-accounting rule: metadata-only transitions must prove no row/value/shape change, while backfills and DDL-induced changes must be atomically accounted or refused before effect.
- A15’s floor-before-delete ordering is conservative under crashes: a crash before floor advancement deletes nothing, while a crash after advancement can leave extra old rows but does not advertise unavailable retained history. Strictly-below-floor deletion preserves the floor row.
- Lifecycle transition helpers reject reopening closed resources and direct open-to-closed transitions that skip draining.
- Connection disposition fails closed when protocol, transaction or sanitation state is not clean.
- Deadlines reject zero, negative and non-finite values.
- Qualified transaction identities include world and deployment, preventing the tested cross-deployment alias.
- External capture is explicitly deferred and refused before effect; I found no W1 obligation to implement an external source.
- Named-provider integration and W2/W3/W4/W5 implementation evidence remain properly deferred and were not treated as gaps.

## 3. Risks and next action

The current passing tests encode two false assurances: cancellation before a commit request is treated as proof of abort, and the “structural copy” test does not copy anything. The reference publication model also omits its central duplicate-retry case. These make the suite green while the durable recovery and trust invariants fail under direct pure counterexamples.

The single next action is one consolidated W1 remediation that closes P2-1 through P2-7, adds the specified pure regression traces, reruns the focused contract suite, and returns the exact revised tuple for focused State re-verdict.
