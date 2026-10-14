DRAFT builder testimony — W1/A11 worker-exit contract/reference implementation

STOP-WRITES is in effect. The candidate implementation is complete within the authorized boundary. No reviewer was launched, and no finding is claimed closed or accepted.

Implemented:

- Sole mutable lease/worker ownership in `ReferenceLifetimeRegistry`.
- Finite sequential command ledgers, reserve-before-invoke effects, fixed trusted setup providers, exact exit/stop/result acceptance, ordered cleanup, containment, and receiver-loss handling.
- Specialized atomic delivery success settlement and two-phase non-success retirement/refetch.
- Activation-bracketed participant membership and obligation-bound leave.
- Bounded neutral lineage with `Q`, `C=Q+1`, `R=C`, coalesced spans, bounded replay, uniform unavailable results, retryable `RefreshCommitRefused`, and stop-gated containment.
- Exact migration attempt phase/serial/request/successor proof and pre-effect reopen.
- Syntax-aware ownership and raw-`Plan` source rules.
- Candidate-only A16 and implementation documentation. The split-files review retained the explicit 1,780-line atomic-owner exception to avoid creating a second mutable state owner.

Changed existing paths:

- `src/garns/backends/contracts/admission.py`
- `src/garns/backends/contracts/worker_authority.py`
- `src/garns/backends/contracts/lifetime_reference.py`
- `src/garns/backends/contracts/buffer_reference.py`
- `src/garns/backends/contracts/snapshot_reference.py`
- `src/garns/backends/contracts/generation_reference.py`
- `src/garns/backends/contracts/migration_reference.py`
- `src/garns/backends/contracts/values.py`
- `tests/contracts/test_admission_contracts.py`
- `tests/contracts/test_lifetime_contracts.py`
- `tests/contracts/test_worker_authority.py`
- `tests/contracts/test_generation_contracts.py`
- `tests/contracts/test_contracts.py`
- `docs/adr/A16-admission-lifetime.md`
- `docs/adr/README.md`

Created exactly:

- [test_worker_exit_contracts.py](/Volumes/projects/limbo/datascad/garns-v9-6/tests/contracts/test_worker_exit_contracts.py)
- [test_contract_source_rules.py](/Volumes/projects/limbo/datascad/garns-v9-6/tests/contracts/test_contract_source_rules.py)
- [W1A11-WorkerExitImplementation.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W1A11-WorkerExitImplementation.md)

The other five authorized existing paths were byte-identical to baseline: `authority.py`, `consumers.py`, `lifetime.py`, `protocols.py`, and `__init__.py`. No out-of-allowlist change or bytecode/cache artifact was found.

Test-count reconciliation:

- Manager baseline: 97 focused / 200 full.
- Adapted pre-new-file suite: 96 / 199.
- The seven historical worker-authority tests became six stronger grammar-level tests; all seven attack themes retain mapped executable coverage in the implementation document.
- Added 27 causal tests and 7 source-rule tests.
- Final: 130 focused / 233 full.

Regression mapping:

- Worker exit: finite C1/C2 schedule, premature C2 refusal, stale C1 attacks, reserve/reentrancy/BaseException, body/cleanup/cancel ordering, first/later queue removal, exact stop-before-accept, task loss at every prepublication pause, identity attacks, and atomic non-delivery publication.
- FIFO settlement: two-range direct failure, cancellation, cleanup failure, expiry, fence, migration, receiver loss, successor invalidation, active-charge retention, commit-first late barriers, replay/conflict, and successful FIFO settlement.
- Membership: unjoined admission/close, live-operation and unresolved-close obligations, frozen-attempt pending leave, later-attempt absence, copy/cross/stale token attacks, and join-during-drain refusal.
- Neutral refresh: zero queue, delayed active head with substantially more than `R` neutral commits, exact replay eviction, active plus `Q` overflow, changed-neutral-changed gaps, retryable wrong-owner presentation, uniform absence, and exact-stop containment settlement.
- Phase proof: exact product transitions, stale same-attempt drain proof, wrong request, exact current pre-effect proof, effect-begun refusal, replay and cross-coordinator attacks.
- Initial-18, correction-1 13/F1–F10, expanded publication revocation, five result vectors, pinned inputs, parent-owned derived commands, raw-`Plan` containment, activation epoch, exact successor, and A7 independence remain covered across the retained suites. Detailed mapping is in the implementation document.

Verification used:

```text
PYTHONDONTWRITEBYTECODE=1
PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb
<python> -B -m unittest discover -s tests/contracts -t .
<python> -B -m unittest discover -s tests -t .
<python> -B tools/check_product.py
```

Results:

| Interpreter | Focused | Full | Product |
|---|---:|---:|---|
| Python 3.11 | 130 OK | 233 OK | 5 PASS |
| Python 3.12 | 130 OK | 233 OK | 5 PASS |
| Python 3.13 | 130 OK | 233 OK | 5 PASS |
| Python 3.14 | 130 OK | 233 OK | 5 PASS |

Inherited SQLite `ResourceWarning`s remained visible in Python 3.13/3.14 full runs. `tools/check.py` was not run.

END verification passed:

- Inputs: 31 entries; manifest SHA `89ee484c8a4980972f0cc7e0cc0f12577a8f00dd5aba07c0eb8c7b83ab884cb5`
- Baseline: 20 entries; SHA `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a`
- Read-only: 741 entries; SHA `53d32f0522a5c0ff7434cfa97ac569fe064ac180f2ccb1294355588ea254d1da`
- Legacy maps: 115, 71, 111, and 614 entries, all passing
- Acceptance evidence: 13 entries, passing
- Brief SHA: `aa75d255cf5d07b0f94a5311596150ea6d992e33bc9c354053c70080f666be44`
- Accepted design SHA: `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`
- Acceptance SHA: `884a0bfb8c5db660f8ee0f79b658a0c3eaf8c5c49e25ea3e2c04d4825d975d89`

New-file hashes:

- Worker-exit tests: `9dda5f8ec1860c4b5cbc9894e3bbad036ef7a51ebf9dd79621f769e29d95adc2`
- Source-rule tests: `d19ce75e29eb782fe6689eb2e48e5c915ff806b8d6e7b25899a2abd89f56d9de`
- Implementation record: `64626738a9507aa8bec64c6c3052b4299561bef530f6bebd4a1ff9d7a3fc3783`

Limits and remaining obligations:

- This is deterministic single-process reference evidence, not production concurrency, async/thread/process execution, durability, crash recovery, backend execution, migration locking, activation fencing, credentials, or database provenance.
- Trusted fixture stop/request observations and fixed hostile actions do not prove physical or durable facts.
- Names remain provisional pending W3 Surface.
- Manager inventory/tuple freezing remains pending.
- Fresh independent full Code and State review and both originating executable closure runs remain mandatory on the exact frozen tuple.
- Historical stopped source/design two-round records remain unchanged.
- Initial implementation remediation count remains zero.

