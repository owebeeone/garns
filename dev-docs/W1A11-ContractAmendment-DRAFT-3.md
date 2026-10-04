STOP WRITES — remediation2 builder testimony

Outcome: one consolidated correction2 implemented on the exact authorized surface; no self-acceptance or reviewer-closure claim.

Changed 14 Revision2 paths:
- docs/adr/A16-admission-lifetime.md
- dev-docs/W1A11-ContractAmendment.md
- src/garns/backends/contracts/admission.py
- src/garns/backends/contracts/buffer_reference.py
- src/garns/backends/contracts/consumers.py
- src/garns/backends/contracts/generation_reference.py
- src/garns/backends/contracts/lifetime.py
- src/garns/backends/contracts/lifetime_reference.py
- src/garns/backends/contracts/recovery.py
- src/garns/backends/contracts/worker_authority.py
- tests/contracts/test_admission_contracts.py
- tests/contracts/test_generation_contracts.py
- tests/contracts/test_lifetime_contracts.py
- tests/contracts/test_worker_authority.py
Created only the two additionally authorized paths:
- src/garns/backends/contracts/snapshot_reference.py
- src/garns/backends/contracts/migration_reference.py
Archive comparison: exactly 14/59 Revision2 entries changed, 0 missing; only those two authorized source additions.

Implemented F1–F10: callback-free fixed closed consumers and commit-before-return publication; sealed parent-owned ordinal child/total commands with no independent kinds/permits/publications; FIFO produced/delivered frontiers with one active head and atomic buffer-permit→handoff-permit exchange; retained same activation fence; frozen migration participant set with exact attempt/ack barriers; sealed lease/queue-bound initial+refresh candidates and closed rows/watermark publication; exact generation+1 in migration and recovery; sealed current-attempt pre-effect proof reopening DRAINING_OLD or pre-effect MIGRATING only after all barriers; actual trusted current-worker-task checks at dequeue and immediately before effect; final exact destination queue local/QueueState barrier. PUBLISHING cannot complete REFUSED.

Cohesion: snapshot candidate state is in snapshot_reference.py (160 LOC), migration identity/barrier records in migration_reference.py (111 LOC). lifetime_reference.py is 796 LOC after orchestration/tests support; I retained it because admission/lease/resource/special-publication/buffer-exchange/close transitions share one atomic registry graph. Another split would create cyclic mutation ownership or obscure validate-then-commit. Amendment records revisit when a real transactional owner exists, not a size-only split.

Exact environment for every execution command: cwd /Volumes/projects/limbo/datascad/garns-v9-6; PYTHONDONTWRITEBYTECODE=1; PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb (Lark1.3.1); each interpreter invoked with -B; no warning filters.
Interpreters:
/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11
/Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12
/opt/homebrew/bin/python3.13
/opt/homebrew/bin/python3.14
For each interpreter, exact command suffix/results:
- -m unittest discover -s tests/contracts -t . => 97/97, exit0 (all four)
- -m unittest discover -s tests -t . => 200/200, exit0 (all four)
- tools/check_product.py => 5/5 PASS, exit0 (all four)
Existing SQLite ResourceWarnings remained visible on 3.13/3.14 full runs; none filtered. 3.11/3.12 full runs emitted none in captured output.

AST/cache: `/opt/homebrew/bin/python3.14 -B` inline ast.parse over all `src/garns/backends/contracts/*.py` plus `tests/contracts/*.py` => AST_OK 25. Final `find . ( __pycache__ or *.pyc )` => zero. No py_compile/compileall in remediation2. Earlier amendment work did accidentally use py_compile, creating 9 cache files; that incident was reported, the exact caches were removed, all later/current checks used ast.parse, and final inventory is clean.

Controls/history verified after final writes:
- RemPlan2 exact SHA 749bea84dc2220bf040467322e096a5e867ccf56c049e7b02004e15d9985284c
- RemInputs2 manifest exact SHA b96517c9cfb8e3f35622242b61a135cbb42b784f5c8b8245081d58e30b4280ac; 16/16
- RemInputs1 13/13; Inputs 9/9; Control 3/3; Baseline 120/120; ReadOnly 111/111; ProductGuard 614/614
- Revision1 internal manifest 47/47
- Revision2 internal MANIFEST-2 SHA 7847467fbe2c1b1252195d441d57f4658315cbb643cd93637686b9365fa4047b; 59/59 from inside archive
- seven historical Baseline nested manifests: 26/26, 11/11, 18/18, 5/5, 13/13, 13/13, 48/48
- no tools/check.py.

Final hashes for 16 builder paths:
513b07655efccd5b973b98769ebd5ad1bc10a20f44918df3d9d7b8ddab50bd7b A16
f21a7cc2af35078bf1af8d09d2c07d10888bdbf956740fd5907a199392d89d9f amendment
483861066a2c8d94af233d73316ecc1983a6e20008725a78c5ad106e85add64c admission.py
55a2ec860bfc4a20750b9674dfe0c4d81d7d82482be2cbb59b5c27be9d4d80fc buffer_reference.py
6b940605168ff9c1351e5ddb796da628adc838db3f9e54128ae699cb53fe442a consumers.py
a8448fb3636f26c642710328894dbf0df77b95199f081a71dce8f643cff93611 generation_reference.py
605d2a45f3685b929a6939ec4eb2cc6def2c91ab3957b146edd445be6ea4b120 lifetime.py
4183405d18401b132b611284cb95b087ca5de97e2daa28c8c714e5a090ebf676 lifetime_reference.py
687397dccda8051b84d071323fa2f7e6648ec464cf74431127dfc81abcd65c5a recovery.py
dacaf8445c29b64837f0c83b2fb36ebcd01b52c4716d20c80d3d0a1d7a4ed8c2 worker_authority.py
6dd83a2bbf2ac898756ca9386b475f815aab56b1ba1cebf463c1c2c8276b1e9c snapshot_reference.py
16143c84739fbf51bdaa001d614dd649c1bbd39dee0f7572986bdc5e700ac981 migration_reference.py
d38899b613f55686ec16e325bf83c5f03c35ee67c0e3ec7c6bbc21664b7656d1 test_admission
7634ea8a85f8040f65058a75e30d7156c4967376dde0b06761abae5545363794 test_generation
c7cc814b4b85071be1c4d2de5e80ea7090883c8508262a4810ec02426750e86b test_lifetime
b402178a37ae0b14d11c79e938c44c9968a7e6edb5aa4d0950dca1936284e84d test_worker

Limits/unmet: deterministic single-process reference contract evidence only. Named `setup_reference_*` production/proof methods accept trusted fixture evidence and do not establish real database provenance, durable recovery, exclusive-request release, worker authentication, locks, threads/cross-process synchronization, crash/restart behavior, or physical fencing. No actual planner/lowerer/backend/runtime/activation/service/database/dependency/network/Git/GWZ work. Original W1 wrong-method P3 remains W3. Fresh dual review plus originating closure and manager manifest pinning remain required.
