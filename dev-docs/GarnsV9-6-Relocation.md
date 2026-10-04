# Garns v9-6 relocation record

**Date:** 2026-10-04  
**Authority:** operator decision — move v9-6 development into garns-wz (option B),
cutting over now. The plan and its full execution log are in the workspace root at
`dev-docs/GarnsV9-6-MigrationPlan-Rev1.md`.  
**Status:** relocation only. This record changes no accepted design, closes no
finding and grants no acceptance.

This product tree moved byte-exact from datascad into the garns-wz workspace, which
is now where v9-6 development continues. **When resuming from garns-wz, start
here**, then read the W1A11 handoff.

## Path map

| | Before | After |
|---|---|---|
| Product root | `/Volumes/projects/limbo/datascad/garns-v9-6` | `/Volumes/projects/limbo/garns-wz/garns` |
| GWZ workspace | `/Volumes/projects/limbo/datascad` | `/Volumes/projects/limbo/garns-wz` |
| GWZ member | `mem_garns_v9_6` at `garns-v9-6` | `mem_garns` at `garns` |
| Git history | none (0 commits, no remote) | `git@github.com:owebeeone/garns.git` (public) |

`/Users/owebeeone/limbo` is a symlink to `/Volumes/projects/limbo`, so the
`/Users/owebeeone/limbo/…` spellings in historical records name the same places.

The datascad copy is left untouched as the historical record. Absolute paths in
historical documents — reviews, reports, logs, drafts, evidence — refer to it and
remain correct as history.

## What moved, and the proof

- Import commit `a4ade29dd01c9e5f712f0ad503493dbad9517e90` in this repository: the
  source tree exactly, with nothing edited.
- Source inventory: 1,135 files, SHA-256 `11e120ce63676529afa5751e8688a099d7265485d3ba24561df446456041d233`, filed in the workspace root as
  `dev-docs/GarnsV9-6-Migration-SourceInventory.sha256`.
- Checked against the working tree and against a `git archive` of the import
  commit: 1,135/1,135 OK, no extra files, nothing excluded by `.gitignore`.
- Nine empty directories under `generated/` — empty `python/`, `queries/` and
  `questions/` folders for worlds without such reads — cannot be represented in
  git. A clone-equivalent tree without them passes G9 Evidence honesty 5/5, the
  product checks 5/5 and the full suite 233/233, so they carry no evidence.

## Guards, verified at both locations

Run from the product root exactly as the W1A11 prompts specify, before and after the
move: MANIFEST-1 self-hash `7e80ca67…`; MANIFEST-1 117/117; Inputs 31/31; Baseline
20/20; ReadOnly 741/741; Legacy WorkerExitRedesign-MANIFEST-3 115/115; Legacy
ContractAmendment-MANIFEST-3 71/71; Legacy ContractAmendment-ReadOnly 111/111;
Legacy ContractAmendment-ProductGuard 614/614; WorkerExitRedesign
AcceptanceEvidence 13/13; HandoffEvidence 7/7; no bytecode or cache artifacts.

Two entries reach outside the product root: `../AGENTS_GWZ.md`, in MANIFEST-1 and
in Inputs. From here it resolves to `garns-wz/AGENTS_GWZ.md`, which is byte-identical
to the pinned value (`432b1ba9…`). **Do not run `gwz init --update` in garns-wz until
the W1A11 gate closes**: regenerating that file would break both pins.

The lane's test matrix was rerun in a scratch copy with its exact commands and
interpreters: focused 130, full 233, product 5, all exit 0, on CPython 3.11.14,
3.12.12, 3.13.12 and 3.14.3. This matches VerificationLogs-1. SQLite
`ResourceWarning`s appear on 3.13 and 3.14 only, as the handoff states. This is
relocation evidence, not review closure.

## Superseded self-descriptions

These files are hash-pinned, so they were not edited. Where they describe location
or registration, this record supersedes them.

| File | Stale statement |
|---|---|
| `AGENTS.md` | registered with GWZ as `mem_garns_v9_6` at `garns-v9-6`; `../garns-v9-5/` as read-only evidence |
| `docs/PRODUCT_LAYOUT.md` | "Current infrastructure status": registered as `mem_garns_v9_6` at `garns-v9-6` |
| `BASELINE.json` | `selected_source.path` = `../garns-v9-5/build/B2` |
| `dev-docs/W1A11-WorkerExitImplementation-Handoff.md` | its "Workspace" and "Product root" lines name datascad |
| the four W1A11 `…-Prompt-1.md` files | their tuple and working-directory lines name datascad (re-issued below) |

The `../garns-v9-5/` citations are citation-only. No tool reads them:
`tools/check_product.py` reads `BASELINE["sha256"]`, which is product-relative. The
B2 tree remains at `/Volumes/projects/limbo/datascad/garns-v9-5`, with a second copy
at `/Users/owebeeone/old-limbo/datascad/garns-v9-5`.

## Re-issued W1A11 review prompts

The four saved prompts were never dispatched. Each is re-issued as `-Prompt-2.md`,
identical to its `-Prompt-1.md` except on two lines — the tuple line and the
working-directory line — where `/Volumes/projects/limbo/datascad/garns-v9-6` becomes
`/Volumes/projects/limbo/garns-wz/garns`.

| Prompt-2 | Changed lines | SHA-256 |
|---|---|---|
| `W1A11-WorkerExitImplementation-ReviewCode-Prompt-2.md` | 30, 55 | `2d4d5281baa0d3cac1012f58452ef94be658a47777d297dee3ea8670848b4c07` |
| `W1A11-WorkerExitImplementation-ReviewState-Prompt-2.md` | 31, 57 | `dc57d5e6c25af8e58ced5b63aca0f5b2d4abfe7a6657d30d891dd3c5a53236a2` |
| `W1A11-WorkerExitImplementation-OriginCodeClosure-Prompt-2.md` | 30, 47 | `5f5226af4ae9b9ef1ba7d487558e7a45807065d3cbde7da8bfe12ba019d94ce9` |
| `W1A11-WorkerExitImplementation-OriginStateClosure-Prompt-2.md` | 31, 48 | `ccb3c419fcc4f998f5ddeaef23c7e6edf45ee10bf8a8708eb3c90ff8963c51cc` |

The `-Prompt-1.md` files and the original HandoffEvidence stay byte-identical as
history. The review object is unchanged: MANIFEST-1 `7e80ca67…`, 117 entries. The
prompts' statement that the tuple is "not a Git commit" still holds: the object is
defined by the filesystem hash tuple, even though the same bytes are now also
committed.

## Evidence for this relocation

`dev-docs/W1A11-WorkerExitImplementation-RelocationEvidence.sha256` pins this
record, the four Prompt-2 files, MANIFEST-1, the handoff and the updated checkpoint.
HandoffEvidence was verified at both locations before the checkpoint was updated, so
its checkpoint entry is expected to differ from now on. Every other HandoffEvidence
entry still verifies.

## Pre-existing finding for the reviewers

This was not caused by the move: the datascad tree fails identically.
`tools/check.py` G10 "no corpus vocabulary in compiler" fails 13/14 at
`src/garns/backends/contracts/semantic.py:98`. The regex
`\b(everbility|vaultwarden|appflowy|practice|book|author)\b` (case-insensitive,
`tools/check.py:589`) matches "author" in "reserved key aliases cannot be visible
author fields".

- The word is absent from the W1A11 ContractAmendment's archived pre-amendment
  `semantic.py`, and the current bytes are pinned from ContractAmendment MANIFEST
  onward, so the line came from the ContractAmendment.
- `semantic.py` is listed in MANIFEST-1, so the line is inside the frozen review
  object.
- It went unseen because the lane does not run `tools/check.py` (it writes gate
  evidence) and `tools/check_product.py` does not include G10. The committed
  `gate-report.json` (2026-10-03, all pass) predates the amendment.
- The disposition belongs to the review, under the lane's correction rules: reword
  the string, or refine the gate. Nothing was changed here.

## Resuming

> "Resume from `dev-docs/GarnsV9-6-Relocation.md`, then
> `dev-docs/W1A11-WorkerExitImplementation-Handoff.md`. Verify RelocationEvidence
> and MANIFEST-1, then launch the Prompt-2 peer-blind Code/State reviews and the
> originating executable closure. Do not rebuild or change accepted design."

Everything else in the handoff stands, except that the review launch uses the
Prompt-2 files and this working directory.
