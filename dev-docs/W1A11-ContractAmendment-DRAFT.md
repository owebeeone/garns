Implemented the authorized W1/A11 contract amendment and stopped all writes.

Implementation summary:

- M1: exact `ResultFieldRole`, independent key flag, structured nested-owner marker, reserved alias and owner-link validation.
- M2: sealed empty admission/lease handles, operation identities, lease states, guarded lexical plan consumption, lease-only executable protocols, provenance-vs-fixture distinction.
- M3: immutable ancestry, ancestor charging, compare-and-transfer ownership, contained work, retained read identities in close outcomes, local-close isolation.
- M4: issuer-private worker command authorization with exact task/worker/command/runtime/generation bindings and one-shot effect ordinals.
- M5: activation/generation coordinator contracts, finite subscription units, buffer/permit exchange, pre-zero migration queue barrier, two-participant schedules, irreversible active protocol epoch.

Cohesion review moved the deployment coordinator into the manager-approved `generation_reference.py`; final sizes are 172 lines for it and 495 lines for `lifetime_reference.py`.

Modified existing paths:

- `src/garns/backends/contracts/semantic.py`
- `src/garns/backends/contracts/protocols.py`
- `src/garns/backends/contracts/values.py`
- `src/garns/backends/contracts/state.py`
- `src/garns/backends/contracts/authority.py`
- `src/garns/backends/contracts/model.py`
- `src/garns/backends/contracts/__init__.py`
- `tests/contracts/test_contracts.py`
- `docs/adr/README.md`

Created paths:

- `src/garns/backends/contracts/admission.py`
- `src/garns/backends/contracts/lifetime.py`
- `src/garns/backends/contracts/lifetime_reference.py`
- `src/garns/backends/contracts/generation_reference.py`
- `src/garns/backends/contracts/worker_authority.py`
- `tests/contracts/test_result_roles.py`
- `tests/contracts/test_admission_contracts.py`
- `tests/contracts/test_lifetime_contracts.py`
- `tests/contracts/test_worker_authority.py`
- `tests/contracts/test_generation_contracts.py`
- `docs/adr/A16-admission-lifetime.md`
- `dev-docs/W1A11-ContractAmendment.md`

Final matrix used each of:

- `/Users/owebeeone/.local/share/uv/python/cpython-3.11-macos-aarch64-none/bin/python3.11`
- `/Users/owebeeone/.local/share/uv/python/cpython-3.12-macos-aarch64-none/bin/python3.12`
- `/opt/homebrew/bin/python3.13`
- `/opt/homebrew/bin/python3.14`

With these exact command forms:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb <python> -B -m unittest discover -s tests/contracts -t .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb <python> -B -m unittest discover -s tests -t .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb <python> -B tools/check_product.py
```

Results on every Python 3.11–3.14 interpreter:

- Focused contracts: 76/76 passed.
- Full discovery: 179/179 passed.
- Product checks: 5/5 passed.
- Inherited unfiltered SQLite `ResourceWarning`s appeared on 3.13/3.14.
- No warning filtering was used.

Additional verification:

- `ast.parse`: 18 amended Python files passed.
- Input manifest: 9 entries passed.
- Baseline archive manifest: 120 entries passed.
- Read-only guard: 111 entries passed.
- Product guard: 614 entries passed.
- No `__pycache__` remains.
- Brief SHA: `1400d30c27e844a35ed1f59a75ec1bce5742e76fafb6df5fce41d984417e14c7`
- Input manifest SHA: `032508b3b5ba210be4b53d939c1301e85a06083b787727a2fd9bf78270b9da24`
- Ownership extension SHA: `039f752614b95680956159b0e9a3ebf9ddafc64babd884f8879ae359a8f85cf1`
- Product guard SHA: `6446ccb2caf7a2c6b901ed4295f7a2ce477c81f03e3135da70fe3144b8c04818`
- Direct archive diff confirms the existing W1 Code P3 body is unchanged; `state.py` only gained operation-aware close fields/validation.

One hygiene incident occurred: an explicit `python3 -B -m py_compile` unexpectedly created nine `.pyc` files. `check_product.py` detected them immediately; exactly those files and the empty cache directory were removed. Subsequent product checks and both immutable guards passed.

Current tuple hashes:

```text
ba1b73f43d17212b05cf8e53c86a05b54de7e09913b00bdeaf7ea0e237d2b4ef  semantic.py
f6a1a6540b6a7ff73a6583b6abfe9f5f7a259dced64759332e0b1ac8a522008c  protocols.py
7655a21367688816d7112996879c9179379a66274e0a7bd3adc10ac3bb0b2243  values.py
3929edef5c85ec114c193eb941bd4388abb90a55cd412e5fb26bbedfcb146bdd  state.py
4925e69464b0b94e1ebd6f197b48a6b2c3120d32e82511a31c479eb192c0183c  authority.py
a1d7c3ce8445e271fa240c9644a27b0e7be64e0c45ca142e2338ff2db7315483  model.py
38948b2c8192a9e2e70fcc76b5e16dde7e024a3cf196d4ef799fb4dd17da4fe2  __init__.py
9210c4a20e0b67e869492ed3f07079f8a9482c392db5f48b2f387631b001e19a  test_contracts.py
5317bcefbdd12042eff9e6fe56d6ad7836208d362922f14e0f207e22f1d44e3e  docs/adr/README.md
acc9b74fb9aa742b9211dc6bad6db421430bdc6dbb9598539b9cff90b21f98e7  admission.py
930d5fb20eb90f07a433d5ffbd53c4a8fdec09570d34d3d79a3c291a573340ba  lifetime.py
7d8cd13358d754ee08a06272a3c0b72c0b1af28680d17ab2edb05b16a8da90c3  lifetime_reference.py
9dbde8feb1398658dee8ee49844cad8e2f360248ea6a04cff52e94165dc72d27  generation_reference.py
db6bab8f02d7ebb290ac1f43eef8640f489b08beaba128e64861bc0d1f833a2f  worker_authority.py
a66967393f5d6ffec572a02a781a5d313e5f2073ef152b6fe88ed483cf54b055  test_result_roles.py
160ea213bcc9c72b0b200136ab00918caba591d6fbcb87431a1edf1c4fdfc4d5  test_admission_contracts.py
b920774183c98558ee6561fdce70d19f809d0cc99dba0fc52f7a000aeeea3005  test_lifetime_contracts.py
1e13d62bd5c084dbb30fe71a17af49be2e7f1a0f22c2f04950febe037330ce31  test_worker_authority.py
51c5fbbe804b58077c6e4ab27388caa0478530005a58c444c8eadfed1d93c69c  test_generation_contracts.py
a4c9a65fad443d5dbe9d40492824dd50e92cfbc6d4fc951e798d87b0ed1d6df2  A16-admission-lifetime.md
e5293ebeb777a31f07203bcba6860e5875fb0d1e643ea98f3a49efc92438db48  W1A11-ContractAmendment.md
```

No known in-scope implementation obligation remains unmet. Independent Code/State review and manager acceptance remain pending. The reference models do not prove production canonical provenance, static whole-program data-flow closure, real async/thread/worker/database behavior, cross-process coordination, physical legacy fencing, crash recovery, or supported backend/version behavior.
