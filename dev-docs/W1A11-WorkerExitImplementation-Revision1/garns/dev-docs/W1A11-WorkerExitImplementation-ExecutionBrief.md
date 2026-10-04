# Worker exit contract implementation brief

Date: 2026-10-04. Owner: manager.
Status: operator-authorized narrow build; implementation acceptance pending.

## Purpose and authority

The operator's “go on next” authorizes the contract/reference implementation
proposed in the accepted worker-exit design and acceptance record. One
`gpt-5.6-sol` builder owns the implementation; independent peer-blind
`gpt-5.6-sol` Code and State reviewers attack its frozen result. Originating
Code/State reviewers additionally verify executable closure of their stopped
counterexamples. Use high reasoning effort. No competing architecture or
whole-product builds are launched.

This is a source implementation object of an already accepted design, not
a third correction to the old stopped amendment or accepted design. Their
two-correction histories and immutable evidence remain intact. Initial
implementation remediation count is zero, with at most two consolidated code
corrections. Any correction requiring a change to the accepted architecture,
ownership boundary or compatibility decision must STOP for operator direction;
do not spend implementation rounds silently redesigning accepted contracts.

The brief authorizes internal contracts, deterministic reference transitions,
causal/property/source-rule tests and candidate additive A16 wording only.
It does not authorize W2 planning/lowering, production async/thread/process
execution, adapters, PostgreSQL services, credentials, activation, locks,
database durability, external capture, packaging, dependency installation,
network access, Git/GWZ operations or workspace structural changes.

## Controlling inputs and history

Read workspace `AGENTS_GWZ.md`, product `AGENTS.md`, checkpoint and
`docs/PRODUCT_LAYOUT.md` before work. Read the review-loop and split-files
skills completely. The accepted composition and exact precedence control,
not historical candidate status headers.

| Controlling input | SHA-256 |
|---|---|
| Worker-exit design | `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc` |
| Design acceptance | `884a0bfb8c5db660f8ee0f79b658a0c3eaf8c5c49e25ea3e2c04d4825d975d89` |
| Design acceptance evidence | `882a3fec6ddecf7a7230a9e332e649be29020a326fe917b75ac523a691c84854` |
| Accepted W2 base | `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e` |
| Accepted W2 lifetime overlay | `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26` |
| W2 composition acceptance | `9d5c76a86c14229d2f37023a61692f1fb845d4c75a30d1af6b9eb68c68910334` |
| W1 acceptance | `524175276f7de2fa44b11d0308aaef9d3ad7e1a869ab17cc0cd24b87dc60316d` |
| Stopped source manifest | `23db272cffd9121f309a852a4ecbf213d8f0be02ddfd629c9cae33cc75ac5424` |
| This build's 20-file baseline manifest | `d95fab4103e1c4e252bff6f0415e04228da96802836b8be906c5df177318490a` |
| This build's 741-file read-only manifest | `53d32f0522a5c0ff7434cfa97ac569fe064ac180f2ccb1294355588ea254d1da` |

All named design/acceptance/manifest inputs live in `dev-docs/`.
The manager pins their exact paths in `W1A11-WorkerExitImplementation-Inputs.sha256`.
Also read the old amendment STOP, ReviewCode-3, ReviewState-3,
FreshCodeClosure-2, OriginStateClosure-2, both historical remediation plans,
and the replacement design's complete finding/test maps and final review reports.

## Sole writer and explicit paths

The builder may modify exactly these existing paths:

- src/garns/backends/contracts/admission.py
- src/garns/backends/contracts/authority.py
- src/garns/backends/contracts/consumers.py
- src/garns/backends/contracts/worker_authority.py
- src/garns/backends/contracts/lifetime_reference.py
- src/garns/backends/contracts/buffer_reference.py
- src/garns/backends/contracts/snapshot_reference.py
- src/garns/backends/contracts/generation_reference.py
- src/garns/backends/contracts/migration_reference.py
- src/garns/backends/contracts/lifetime.py
- src/garns/backends/contracts/protocols.py
- src/garns/backends/contracts/values.py
- src/garns/backends/contracts/__init__.py
- tests/contracts/test_admission_contracts.py
- tests/contracts/test_lifetime_contracts.py
- tests/contracts/test_worker_authority.py
- tests/contracts/test_generation_contracts.py
- tests/contracts/test_contracts.py
- docs/adr/A16-admission-lifetime.md
- docs/adr/README.md

New builder paths are exactly:

- tests/contracts/test_worker_exit_contracts.py
- tests/contracts/test_contract_source_rules.py
- dev-docs/W1A11-WorkerExitImplementation.md

No other writes. Manager alone owns execution brief, manifests, baseline copies,
prompts, verbatim DRAFT testimony, reports, remediation plans, acceptance and
checkpoint. Do not spawn helpers. Use `apply_patch`; preserve unrelated edits.

The extra existing paths beyond the design's prospective ownership table have
narrow wiring purposes: `authority.py` may participate in issuer-private
task lifecycle invalidation without transferring claims; `consumers.py`
may represent the finite issuer-owned command schedule and detached products;
`__init__.py` may wire internal names; `test_contracts.py` may adapt retained
attack fixtures; ADR README may add candidate status/history links only.
They authorize no new subsystem or public surface.

`test_worker_exit_contracts.py` is the focused deterministic causal schedule
suite. `test_contract_source_rules.py` implements fast syntax-aware contract
checks. They are not arbitrary line-count splits.
Keep `lifetime_reference.py` the sole mutable worker/lease owner, with buffer
state as its transactional subledger and deployment generation as the existing
coordinator domain. Its current 796-line atomic-state exception is retained;
record growth and cohesion/revisit reasoning in the implementation document.
Do not create a second authorization/worker state owner to shorten that file.
Immutable identities and types belong in their cohesive existing files.

Historical `W1A11-ContractAmendment.md`, accepted design documents, all reports,
source STOPs, A1–A15, `operations.py`, result-role semantics, grammar, compiler,
shipped runtime, generated evidence, package metadata and dependency files
remain read-only. Do not edit an old report or manifest to imply new closure.

## Historical verification and write containment

Twenty byte-identical original writable files are preserved under
`dev-docs/W1A11-WorkerExitImplementation-Baseline/`.
Its `Legacy-*` verification maps rebase only those files and retain every
other original hash/path. From product root verify:

- `W1A11-WorkerExitImplementation-Baseline.sha256` — 20 entries;
- `W1A11-WorkerExitImplementation-ReadOnly.sha256` — 741 entries;
- `W1A11-WorkerExitImplementation-Inputs.sha256`;
- all four `Legacy-*` maps inside the new baseline directory — original
  design115, stopped source71, old readOnly111 and old product614 entries;
- design `AcceptanceEvidence.sha256` — 13 entries.

After authorized source changes, do not run historical live source/design
manifests against altered bytes or claim they still describe live source.
The original manifest files remain byte-identical evidence; use the manager's
explicit rebased maps for their content checks. The new implementation tuple
will have a separate complete manifest. Verify guards at START and END.
Any mismatch outside the write allowlist stops work for manager reconciliation.

## Required implementation and executable closure

The complete accepted design §§3–12 is mandatory. The summary below is a
routing map, not permission to omit a clause or counterexample.

| Root | Required implementation | Mandatory executable evidence |
|---|---|---|
| Worker exit and sequential commands | Finite positive closed schedule M; distinct bounded command records/tombstones, one active serial, one outer permit; fixed issuer-owned effects, reserve-before-invoke/nonreentrancy; success escrow, exact stop, exact receiver accept; contained failures/cancellation/task loss; ordered finite cleanup and diagnostics; generic non-delivery atomic publication/terminal/release | Every §7 pause and adversarial trace; effect1 raises before effect2; BaseException; nested/concurrent reservation; C1 replay against C2; first/later queue removal; body/cleanup/cancel races; task loss at every prepublication state; wrong/copy/stale/replay identity; no publication before stop or after revocation |
| FIFO settlement | Nonterminal publication candidate; specialized sole success commit publishes/settles FIFO/terminalizes/releases atomically; generic completion structurally refuses handoffs; two-phase non-success retirement invalidates successors but retains the active charge through exact worker-and-iterator stop before release; full new refetch baseline | Two queued ranges with first unpublished failure under every cause; no successor or cursor invention; last-permit close/migration/fence/task-loss races both sides of commit; queued versus active releases, replay/conflict and successful FIFO |
| Participant lifecycle | Constructor UNJOINED, no preactivation membership/admission; activated exact open joins atomically; request/final leave bound to all retained obligations; frozen attempt sets; pending leave handled at cutover/reopen/recovery | Pre/post activation; leave-before-activation; each retained obligation; duplicate/copy/cross/stale membership; join/leave during drain; final idle runtime absent from later attempts |
| Neutral refresh | Q from authored bound/deployment ceiling, C=Q+1, R=C; separate produced/delivered cursors; one span per changed gap and bounded replay; current candidates only in charged operation records A<=L_refresh; atomic neutral consumption/cursor/span/ring/terminal/release; uniform unavailable absent handles; complete known-candidate error dispositions | Zero/one/Q queued plus active head; substantially more than R neutral commits; exact retained/evicted/current/cross/counterfeit results; no side history; delayed head success/failure; changed-neutral-changed; overflow/close/migration; resource counts and bounded mutation work; next changed range |
| Phase proof | Exact deployment-state × attempt-phase product; serial/request/successor-bound proof, pre-effect reopen only, first effect disables edge, invalidation before reopen | Enumerate legal product and reject every other pair/edge; same-attempt stale DRAINING proof; one exact current pre-effect proof; post-effect/replay/wrong/cross variants with unchanged state |

Keep all initial18, stopped amendment correction1's13/F1–F10, expanded
publication revocation and later residual attacks. The five accepted result
vectors, detached pinned parameters, parent-owned child/nested/total commands,
no-raw-Plan execution seam, activation epoch, exact successor binding and
A7 unresolved transaction retention are unchanged requirements.
Do not delete coverage merely because fixture entry points change.

Every refusal must assert unchanged owner, lease/command state, active
reservation/ordinal sets, result/failure/publication facts, ancestry/shared
counts, lineage, membership and migration state as applicable. Exact replay
must prove idempotence, not accept a generic label. Tests must execute actual
transitions and fixed fixture effects; no expected-answer dispatch or echoes.

Trusted reference providers may issue sealed setup observations and fixed
hostile effect/cleanup actions to exercise sequences. Ordinary invocation
cannot supply effect callbacks, worker/task identity, context claims, stop
booleans, containment owner or fabricated durable proof. Empty identities
must be exact-type/instance, noncopyable/nonserializable and reveal no semantic
fields. Observation of worker return/cancellation/finally is not stop evidence.
A known commit does not establish quiescence; stop does not establish A7 truth.

Syntax-aware checks enumerate execution consumers, effect/exit entry points,
terminalizers, membership/cursor mutation and proof construction; reject
raw Plan execution/unwrap escape, caller-proof overrides, independent child
permits and secondary mutable worker state. Inspect disabled conditional
source branches if any owned C-style/Rust files are introduced; none are
authorized by this Python-only boundary. Standing braced-control-flow and
explicit cfg-scope rules apply to any new/modified applicable code; do not
claim a broader migration.

## Candidate documentation and verification

`W1A11-WorkerExitImplementation.md` records enacted method/type inventory,
the exact accepted supersession map, per-finding causal regression locations,
ownership/size rationale and explicit reference-versus-production limits.
A16/README may reflect this candidate and accepted design direction without
self-accepting source. Do not rewrite A1–A15 or historical amendment text.

Offline verification uses these existing interpreters, with no installs:

- `/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11`
- `/Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`
- `/opt/homebrew/bin/python3.13`
- `/opt/homebrew/bin/python3.14`

Set `PYTHONDONTWRITEBYTECODE=1` and
`PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb`
(cached Lark1.3.1, not0.7.8). Run each interpreter with:

- `-B -m unittest discover -s tests/contracts -t .`;
- `-B -m unittest discover -s tests -t .`;
- `-B tools/check_product.py`.

Keep inherited SQLite ResourceWarnings visible. Do not run `tools/check.py`
in the live tree because it writes out-of-scope gate-report evidence.
The manager separately checks inherited hashes and records limitations.
Do not create bytecode. No passing suite is self-closure or real backend,
concurrency, durability, crash or provenance evidence.

## Handoff and review gate

Stop all writes before returning your complete final testimony: actual changed
paths, commands/results/counts, regression mapping, limits and unmet obligations.
Do not declare GO or findings closed. Manager files it verbatim as DRAFT,
reproduces focused/full/product gates, verifies immutable guards and exact
inventory, then pins the complete contracts/tests/ADR/document/control tuple.

Fresh full peer-blind Code/State review is mandatory. Both original stopped
Code and State reviewers must also rerun their actual counterexamples on that
same source tuple; prior design-only GO is not executable closure.
Design-origin Consistency/Safety findings map to the named new executable
regressions and are attacked by both source axes. No public name freezes here;
W3 Surface and final P12 remain separate gates.

Any P0/P1/P2 blocks. Manager consolidates all findings into one disposition
plan and one patch per correction, with originating reviewer verification.
Fresh full reviewers replace old proofs after material source interface/call
graph changes; bounded corrections use the same reviewers plus changed-range
attacks. A required accepted-design change stops for operator direction.
Acceptance is contracts/reference tests only on exact reviewed bytes, not
an async runtime, PostgreSQL execution, activation or downstream launch.
