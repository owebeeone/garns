# W0 manager acceptance

**Status:** accepted as the W1 semantic baseline  
**Date:** 2026-10-03  
**Owner:** manager

The registration hold in `W0-REPORT.md` is closed. That report is preserved as
the original promotion record; this acceptance supplies the current disposition.

## Registration evidence

The operator created the repository. The manager executed:

```sh
/Users/owebeeone/.cargo/bin/gwz --json --target garns-v9-6 status
```

GWZ returned no errors and member status `Ok` for `mem_garns_v9_6` at
`garns-v9-6`. The local `.git` directory exists. The repository is on its
initial `main` branch with no commit yet; its product files are untracked.
Acceptance here does not assert a clean committed checkout or a publication.

## Renewed verification

The registered tree was tested using CPython 3.14.3 and existing cached Lark
1.3.1. Commands ran from the product root:

```sh
LARK_ROOT=/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$LARK_ROOT" /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests -t .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$LARK_ROOT" /opt/homebrew/bin/python3.14 -B tools/check.py
(cd evidence/v9-5-b2 && shasum -a 256 -c MANIFEST.sha256)
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.14 -B tools/check_product.py
```

All commands exited 0:

- 103 unit tests passed.
- All 128 G0–G11 checks passed, including 168 mutants, fresh regeneration and
  real Rust compilation/row parity.
- All five inherited manifest entries verified.
- Product paths, pinned inputs, cache hygiene and shipped path hygiene passed.

The Python 3.11–3.14 matrix and full deletion/regeneration evidence from
`W0-REPORT.md` remain applicable. The inherited SQLite connection
`ResourceWarning`s recurred under 3.14 and remain recorded for runtime lifecycle
work. These runs exercise source trees with an existing cached dependency;
they do not establish wheel installation or hermetic CI provisioning.

## Accepted bytes

| Artifact | SHA-256 |
|---|---|
| `W0-REPORT.md` | `f5fc6781d0332ddfd84133b72c9a5d126d635575fb399b905a8b2c75f9adcf2e` |
| Renewed `gate-report.json` | `ea8ba06fc9c86a45b81ee65e033fa834574a05efa1c25d074f0e5b0b0e4c7a95` |

The 604-file product payload after the registration-status documentation
updates has SHA-256:

```text
7b3b21f7439931c0394864df96e2eeee4569d04d0aac1b6acb3adefea16bd560
```

Method: sorted product-relative path, NUL, file bytes, NUL. Exclude `.git`,
`__pycache__` and this acceptance document to avoid a self-reference.

## Handoff

W0 is accepted for W1 contract and ADR work. D4 (SQLite tier), D5 (first capture
branch) and D6b (PostgreSQL version range) remain open. W1 must close them and
accept all A1–A15 before handing its protocol tuple to W2. No downstream
implementation builder has been launched by this acceptance.
