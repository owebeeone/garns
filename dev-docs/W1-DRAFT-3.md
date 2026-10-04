COMPLETE — final W1 architectural remediation round 2 is ready for manager pinning and fresh review.

Revised 26-file tuple:

`3385fe97c6c8ecfdde3731fc150442e3fcd005f092dafebdc8b8afea05c14c13`

Closure candidates:

- Code-2 P2-1: subscription is no longer directly iterable and has no parallel `next_delivery` path. It returns one concrete authority-bound iterator. Each `__anext__` validates before reading and again after any awaited read, immediately before returning rows. Renewal closes the old iterator; an in-flight old read cannot deliver afterward.
- State-2 P2-1: ordinary protocols no longer accept caller-selected time, epoch or owner. `RuntimeAuthority` owns injected clock, invalidation-epoch and current-task providers; operations carry only the opaque context.
- State-2 P2-2: migration success is coupled to its exact request. Metadata-only success requires a proof digest and forbids data publication. Backfill/DDL success requires nonempty effects, requested binding, matching scope/generation, `migration:<request-digest>` identity and matching payload digest. Refused/indeterminate results are separate non-success types.
- State-2 P2-3: cancellation uses an exhaustive phase/evidence matrix. Invalid combinations refuse; notably, commit-requested plus rollback-confirmed cannot manufacture an abort.
- State-2 P2-4: transaction ownership is captured from the runtime’s genuine non-null current-task identity and checked by identity, not equality. Equal strings, hostile equality objects and child tasks cannot enter.

All round-1 counterexample regressions remain covered, including immutable semantic values, binding-aware plans, genuine context instances, defensive claims, duplicate publication, indeterminate rollback failure, and SQLite shutdown fencing.

Verification command pattern, run for Python 3.11.14, 3.12.12, 3.13.12 and 3.14.3:

```sh
PYTHONWARNINGS=ignore::ResourceWarning \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="${LARK_ROOT}:src" \
"$py" -B -m unittest discover -s tests/contracts -t .

PYTHONWARNINGS=ignore::ResourceWarning \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="${LARK_ROOT}:src" \
"$py" -B -m unittest discover -s tests -t .
```

Every interpreter passed:

- Focused contracts: 34/34.
- Full discovery: 137/137 — 34 W1 tests plus 103 inherited tests.

Additional verification:

- `tools/check_product.py`: all five checks passed.
- Inherited evidence manifest: all five entries verified.
- Grammar SHA-256 unchanged: `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`.
- No bytecode cache directories were created.
- No database, backend, real worker, dependency, Git/GWZ, grammar, capture, W2 algebra or manager-record changes were made.

The inventory remains:

- 16 files under `docs/adr/**`
- 8 files under `src/garns/backends/contracts/**`
- 2 files under `tests/contracts/**`

Limitations remain explicit: these are pure protocols, reference models and conforming fakes. They do not prove PostgreSQL execution, SQLite responsiveness, real migration atomicity, actual driver cancellation, worker containment or database fault cuts.

All ADRs remain **PROPOSED FOR REVIEW**. This report is builder self-assessment, not finding closure, W1 acceptance or W2 authorization.
