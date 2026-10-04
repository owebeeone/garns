# Worker exit implementation baseline verification

Date: 2026-10-04. Manager record before builder dispatch.

The operator authorized the narrow contract/reference build after accepting
the replacement design. The exact execution brief is
`aa75d255cf5d07b0f94a5311596150ea6d992e33bc9c354053c70080f666be44`;
Inputs31 is `89ee484c8a4980972f0cc7e0cc0f12577a8f00dd5aba07c0eb8c7b83ab884cb5`.

Before archival, manager verified original design115, acceptance evidence13,
stopped source71, readOnly111 and product614 entries without failures.
Twenty writable original UTF-8 source/test/ADR files were preserved
byte-identically through apply_patch and checked against their original hashes.
No original source or historical review bytes changed in preparation.

New verification passed: baseline20, immutable741, inputs31 and rebased
historical maps of115/71/111/614 entries. These maps substitute only the exact
20 writable original paths with archived copies. They are separate maps,
not rewritten historical manifests or new claims of source acceptance.

Available interpreters are Python3.11.14,3.12.12,3.13.12 and3.14.3.
Manager ran on `/opt/homebrew/bin/python3.14`, from the product root:

- `env PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:/Users/owebeeone/.cache/uv/archive-v0/mY6l38X45N5FrBKUv7meb /opt/homebrew/bin/python3.14 -B -m unittest discover -s tests/contracts -t .` —97/97, exit0.
- Same environment/interpreter with `-B -m unittest discover -s tests -t .` —200/200, exit0.

Inherited SQLite ResourceWarnings remain visible and unfiltered. Passing
baseline tests do not cover/close the five stopped defects. No product
generator, network/install, database service, Git/GWZ operation or bytecode
generation was used. No PostgreSQL/async production evidence is claimed.

One builder receives the exact existing20/new3 allowlist. It must preserve
the accepted sole-owner architecture, implement all mapped causal tests and
stop writing for a new complete tuple and independent/originating review.
Initial implementation correction count is zero; source acceptance is pending.
