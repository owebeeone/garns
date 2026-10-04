Remediation 1 is frozen; writes have stopped. This is a builder-complete candidate only—no reviewer finding is self-closed or accepted.

Implemented all 13 remediation groups, including:

- Issuer-owned exact closed consumers and closed step products.
- Lease-pinned parameters and original authority.
- Strict operation/step grammar and one causal publication barrier.
- Admission/coordinator epoch binding and reopen invalidation.
- Exact registration, buffer provenance, cursor lineage, and permit exchange.
- Exact queued command/worker/authorization tuples.
- Disjoint static-query and live-question operations.
- Legal close transitions with queue/subscription/runtime conservation.
- Proof-bearing activation and migration recovery.
- Sealed registry-owned execution and buffer permits.
- Atomic rejected owner transfer.
- Direct handoff and generic live-publication bypass prevention.

Changed relative to preserved Revision1:

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

Created under the remediation allowlist:

- `src/garns/backends/contracts/consumers.py`
- `src/garns/backends/contracts/buffer_reference.py`
- `src/garns/backends/contracts/recovery.py`

Final matrix command forms, run with each authorized Python 3.11–3.14 interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:src:." <python> -B -m unittest discover -s tests/contracts -t .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:src:." <python> -B -m unittest discover -s tests -t .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb:src:." <python> -B tools/check_product.py
```

Every interpreter passed:

- Focused contracts: 85/85
- Full suite: 188/188
- Product checks: 5/5
- All exit codes: 0
- No warning filtering
- Existing SQLite `ResourceWarning`s remained visible on Python 3.13/3.14

Additional verification:

- `ast.parse`: 23 contract/test Python files passed.
- Remediation inputs: 13/13.
- Original inputs: 9/9.
- Control manifest: 3/3.
- Baseline archive: 120/120.
- Read-only guard: 111/111.
- Product guard: 614/614.
- Revision1 manifest verified from inside its archive: 47/47.
- No `__pycache__` or `.pyc` remains.
- No `tools/check.py`, network, dependencies, services, Git, or workspace-control mutations were used.

Control hashes remain exact:

```text
7a8d145e29f5a1c2de01d91a205bf2689b974763795a73046d0c4db39712aa53  RemPlan
6abcd861c58160bec0c2124a0dda680456ff6dcf0e06eff05110d234cb5bae63  RemInputs
185e748c729872fc3ca697577a4638243887a75bbb479bab544b4cdb9e38148d  ReadOnly
6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818  ProductGuard
```

Cohesion review followed the `split-files` guidance. Generation, consumers, buffer provenance, recovery, and worker authorization are separated. `lifetime_reference.py` remains 611 lines because its remaining admission/lease/resource/publication/close transitions share one atomic registry state graph; the amendment records the exception and a revisit point after review or when a transactional production owner exists.

Current changed-file hashes:

```text
5b01ec6b948403b9804e2ab7184986073899061370a2d8bfc95bf88619cfa87b  docs/adr/A16-admission-lifetime.md
21fec4cc88967464844288d5486c84bfa2e9aa5ebf974ce7f7d178a8334d7b6b  dev-docs/W1A11-ContractAmendment.md
2c471c87e63e496fae13e971afa962888c43839218b22d20e7edb10c292be0fa  admission.py
a03a2b83d0ca1ab345992a96d9144e4031b06ef8ce6ce8469bbc658c46d00539  generation_reference.py
0ac05de117648ee965b258f8fea4a52ba3aa684df83436e82bc4978bc5ab7eaa  lifetime.py
2253c22f9f311706f347ddf141eba437e7a3284178e26376584529695d5ec78f  lifetime_reference.py
0dd2f148549cf40fa8d0d5f52b8f2568b24275a77a039813c6039701a67678e3  model.py
786bb1ae61beab3a3517cabf7568707f1c75831889f9da928659e776266c900c  protocols.py
31a11f611097387fce1c80435d9ff481fd46537280a7af509629aecd3655f39d  worker_authority.py
52589edd596db89f1c21709f0b07b9c3ec6c38c38da0120745826b82fdc88774  consumers.py
9bb88b8062c9e110f2dc03d91593e500496669d8961b5d322f976dc20f91f42e  buffer_reference.py
58fbe0ed638f538da432f0b5069cdcbd6b91584860dc414dd1dbf87eea495d29  recovery.py
f17571d403435fa932d70e44ad4b6041a19c6bb6e07475a352ebd5fdcb93d890  test_admission_contracts.py
51ad9c221d9b044c7efd784a8457d55fd6c7212cee2f3d96e67bef8d8c8e3455  test_contracts.py
d5e1052d5cd933a02aa3269a049e7c8571ac41be39e4af5de22f51249fc7d5c2  test_generation_contracts.py
b1f3c6a09a0154623837d142391f2e0b3b4310dadff5b4f6d4849ba803939f35  test_lifetime_contracts.py
803d3b3e7b5b8cf0b7111b4d4a22095a0cf48274511c2dac076a3757dc5fb557  test_worker_authority.py
```

Recorded hygiene incidents:

- The earlier `py_compile` check created nine bytecode files despite `-B`; exactly those generated files and the empty cache directory were removed. All subsequent guards and cache checks passed.
- Three read-only inventory attempts failed harmlessly because `cmp`/`diff` were unavailable and one zsh loop temporarily reused its special `path` variable. No files changed; the inventory was rerun successfully using `shasum` and a safe variable name.

The original W1 P3 remains unchanged. Original A1–A15, accepted W2 documents, archived history, ReadOnly111, and ProductGuard614 remain immutable.

Residual limits remain explicit: these are deterministic reference contracts, not production planner/lowering/backend/runtime code, canonical provenance proof, real worker/thread synchronization, database or cross-process coordination, physical activation/fencing evidence, or crash/restart proof. Fresh Code/State and originating closure reviews remain required.

