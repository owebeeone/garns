# W1A11 worker-exit implementation — acceptance

**Status: accepted at MANIFEST-4
`596c8ab80821646749a24fc63477d278a8b2f0ae1c145746c2a77255fb6e6339` (156 entries)
after `W1A11-WorkerExitImplementation-ReviewCode-3-Reverdict.md` and
`W1A11-WorkerExitImplementation-ReviewState-3-Reverdict.md` reported GO. This
accepts the worker-exit internal contracts and the deterministic reference
implementation and tests only.**

**Date:** 2026-10-05  
**Owner:** manager

## What is accepted

The candidate implements the accepted design `W1A11-WorkerExitRedesign.md`
(`167f6ce7…`) inside its ExecutionBrief boundary:
- a single mutable lifetime and worker owner;
- finite command ledgers with reserve-before-invoke effects;
- exact exit, stop and receiver acceptance, with ordered cleanup;
- one containment routine;
- atomic non-delivery publication and specialized delivery settlement;
- two-phase non-success retirement;
- registry-witnessed, activation-bracketed membership;
- bounded neutral lineage and replay;
- exact migration-phase proofs.

| Gate | Result on MANIFEST-4 |
|---|---|
| Focused tests | 190 pass on CPython 3.11–3.14 |
| Full tests | 293 pass on CPython 3.11–3.14 |
| Product checks | 5 pass |
| ReadOnly guard | 741 entries verify |

The tests are corroboration only. Acceptance rests on the review record below.

## Review record

| Round | Object | Reports | Merge | Outcome |
|---|---|---|---|---|
| 1 | MANIFEST-1 `7e80ca67…` (original build) | 4 | [RemPlan](W1A11-WorkerExitImplementation-RemPlan.md) | NO-GO: 13 blocking roots, IR1–IR13 |
| 2 | MANIFEST-2 `ee441c18…` (after correction 1) | 6 | [RemPlan-2](W1A11-WorkerExitImplementation-RemPlan-2.md) | Round 1 fully closed; NO-GO: IR21–IR23 |
| 3 | MANIFEST-3 `9a9f8b2a…` (after correction 2) | 8 | [RemPlan-3](W1A11-WorkerExitImplementation-RemPlan-3.md) | Rounds 1–2 fully closed; NO-GO: one regression, IR31 |
| 4 | MANIFEST-4 `596c8ab8…` (after correction 3) | 2 | this record | GO/GO |

Correction 3 was an operator-authorized, one-line exception to the two-correction
gate. Round 4 used the two-reviewer cap that the operator set and the review-loop
skill now records.

Every P0–P2 raised in rounds 1–3 is closed on the final code:
- **Rounds 1–2.** Each was confirmed closed on MANIFEST-3 by the reviewer who
  raised it. The one-line correction only adds a refusal while a cleanup action
  runs, so those closures carry over. Both round-4 re-checkers re-ran the full
  suites.
- **IR31.** Six reviewers found it. The two round-4 re-checkers closed it on
  MANIFEST-4 by re-running all eight variants on two interpreters. The other
  four raisers were not resumed, an operator-directed economy deviation recorded
  in RemPlan-3.

## Historical stopped roots

| Root | Status on MANIFEST-4 |
|---|---|
| Worker exit (`ReviewState-3 P2-1`) | Closed |
| Failed FIFO (`ReviewCode-3 P2-1`, `ReviewState-3 P2-2`, `FreshCodeClosure-2 P2-1`) | Closed |
| Participant lifecycle (`ReviewCode-3 P2-2`) | Closed |
| Neutral refresh (`ReviewState-3 P2-3`) | Closed |
| Stale phase proof (`OriginStateClosure-2 State-Closure-P2-1`) | Closed |

## Carried forward, not accepted here

- **To W3: open P3 findings.**
  - IR20: `tools/check.py` G10 fails on read-only `semantic.py`.
  - IR27: a cancel after acceptance returns the success receipt.
  - IR28: close and barrier scans grow with history.
  - IR32: the authority source rule checks presence, not order.
  - IR33: the cleanup-provider lookup comes before the step claim.
  - IR34: `revoke_generation` relabels RETIRED admissions.
- **To W3: stale wording in the implementation record.** "no further correction
  is allowed after correction 2" and the round-3 sentence.
- **To W3: below-bar items** recorded in the round-2 and round-3 reports.
- **To the operator:** the design-legal `CURRENT × NONE → RETIRED` binding edge is
  explicitly refused pending decommissioning authority. It needs a decision
  before W3 or W4 rely on binding non-reuse from CURRENT.
- **Outside this acceptance:**
  - W3 Surface review and the public name freeze;
  - production async, thread and process execution;
  - locks, durability and crash recovery;
  - database provenance;
  - PostgreSQL;
  - activation;
  - final P12.

  This is deterministic single-process reference evidence.

Pinned by `W1A11-WorkerExitImplementation-AcceptanceEvidence.sha256`.
