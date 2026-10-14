# Worker-exit replacement design acceptance

Date: 2026-10-04. Decision owner: manager. Status: ACCEPTED — DESIGN ONLY.

## Decision and exact tuple

The operator-authorized narrow worker-exit replacement design is accepted after
the required independent reviews and same-origin counterexample retraces.
This decision consumes no new correction: the design used exactly two
corrections of two. No third patch, architecture-counter reset, waiver or
accepted risk replaces a blocking finding.

| Accepted artifact | SHA-256 |
|---|---|
| [Replacement design](W1A11-WorkerExitRedesign.md) | `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc` |
| [Verbatim final drafter testimony](W1A11-WorkerExitRedesign-DRAFT-3.md) | `cecd5667569417f8958e0a4697c74bf80ba053097178369474e9b48c6af641ae` |
| [Complete 115-entry reviewed object](W1A11-WorkerExitRedesign-MANIFEST-3.sha256) | `aa5d1b7b1c41d4148ef0c690f7e908c0f5e6b71fb8d8aae9d91102f24679a737` |
| [13-entry acceptance evidence](W1A11-WorkerExitRedesign-AcceptanceEvidence.sha256) | `882a3fec6ddecf7a7230a9e332e649be29020a326fe917b75ac523a691c84854` |
| [Final manager verification](W1A11-WorkerExitRedesign-Verification-3.md) | `533151a2012cee0f4b6d49234019617bee69704e3cd3d38b37167c12d00716d4` |

The reviewed design retains its historical candidate wording. This separate
acceptance record controls status without changing its reviewed bytes.
AcceptanceEvidence pins the final reports, erratum, canonical prompts,
verification and original reviewed tuple; it does not replace or rewrite
MANIFEST-3. Its self-hash and this decision are not included recursively.

## Review gate

The two full round-2 reviewers independently returned final focused re-verdicts
on their exact findings plus changed-range attacks. Four originating reviewers
independently retraced their assigned counterexamples on the same final tuple.
All are 5.6 Sol reviewers; no final verdict relied on a current peer report.

| Required evidence | Verdict | Exact SHA-256 |
|---|---|---|
| [Consistency re-verdict](W1A11-WorkerExitRedesign-ReviewConsistency-3.md) | GO | `376535e7bbb88f91d0c8535e0cf8d9b8dd1efc1d1ed9cd6a90565b2570a485d3` |
| [Safety re-verdict](W1A11-WorkerExitRedesign-ReviewSafety-3.md) | GO | `9694adff2e8e30f777f6839b8d20fd8a66a335556963efff067d7fec74eb2e22` |
| [Original Consistency preservation](W1A11-WorkerExitRedesign-OriginConsistencyClosure-3.md) | GO | `7215317aa7c14a4b07a733994fef9730466961c96e894f3eeab8c73ac1c729ab` |
| [Original Safety preservation](W1A11-WorkerExitRedesign-OriginSafetyClosure-3.md) | GO | `05a1266ffe006514910d6bae728fb4648c5ff4c6cd6dfb4e27eaa7da4b00e188` |
| [Originating Code prospective closure](W1A11-WorkerExitRedesign-OriginCodeClosure-3.md) | GO | `01d7d50fb5764648af0d33cad33d7ba594dce3128d67e0ed03ef67790809dd16` |
| [Code evidence erratum](W1A11-WorkerExitRedesign-OriginCodeClosure-3-Erratum.md) | GO unchanged | `279d5a9b5819c003a2ccf46e8c8b78363cca61ea630b537ec526926e8595e51b` |
| [Originating State prospective closure](W1A11-WorkerExitRedesign-OriginStateClosure-3.md) | GO | `3522360a606de27d8e365044edb963455033429f996e3d7e0f12cde52c96ace9` |

Reports and the erratum are filed verbatim. The Code erratum corrects only a
mistyped Revision1 map hash after the same reviewer reverified 88/88 entries;
the report itself was not silently edited. No design bytes or verdict changed.

The final pair closes both Consistency-2 P2 findings and Safety-2 P2-1
prospectively, preserves all six round-1 design dispositions, and finds no
new P0–P3 design finding or architectural root. Earlier round-2 NO-GOs and
narrower GOs remain historical evidence; only this final gate resolves the
design. The original reviewers' closure is not implementer self-closure.

## Accepted design and precedence

The accepted composition is W2-QueryPlanningDesign, the accepted
W2-AdmissionLifetimeRedesign overlay, and this replacement design's exact
additive supersessions. Existing W1 and W2 acceptances remain controlling
outside those explicitly named supersessions.

- W1 acceptance SHA:
  `524175276f7de2fa44b11d0308aaef9d3ad7e1a869ab17cc0cd24b87dc60316d`.
- W2 base SHA:
  `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`.
- W2 overlay SHA:
  `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`.
- W2 composition acceptance SHA:
  `9d5c76a86c14229d2f37023a61692f1fb845d4c75a30d1af6b9eb68c68910334`.

Replacement §2's supersession table and corresponding detailed clauses control
the finite multi-command/worker-exit ledger, exact task-loss and cleanup
ownership, operation-kind-specific final publication, failed FIFO
retirement/refetch, activation-bracketed participant membership, bounded
neutral lineage/replay and phase-exact no-effect migration proof.
No stopped source or unaccepted A16 wording independently overrides that
composition. Any later public API naming still needs W3 Surface review.

The central conserved rule is one authoritative owner and one exact release:
iterator success commits publication, FIFO settlement, terminal outcome and
release together; iterator failure retains its active charge through exact
worker-and-iterator stop before specialized terminal release. Neutral refresh
terminal/release is part of its cursor/span/ring commit, not a later guessed
completion. Empty evicted handles reveal no reconstructed history.

## Verification and remaining OPEN source roots

Manager and reviewer checks passed at their start/end boundaries:
115 final-object entries, 25 second-remediation inputs, 100 and 88 archived
revision entries, 13 first-remediation inputs, 19 original inputs, 71 stopped
source entries, 111 read-only entries and 614 product guards. Source/test
inventory remains the exact 62 guarded files with no new files or bytecode.

No tests were run for this design gate. Existing passing source tests cannot
prove these prospective transitions. No source, test, accepted ADR, grammar,
generated evidence, backend, runtime, service, database or Git/GWZ state changed.

| Stopped root | Design disposition | Source status |
|---|---|---|
| Worker result/failure exit ownership | Accepted §§3–7 | OPEN |
| Failed FIFO head/publication settlement | Accepted §8 | OPEN |
| Preactivation membership and final leave | Accepted §9 | OPEN |
| Neutral refresh and bounded lineage/replay | Accepted §10 | OPEN |
| Same-attempt phase-proof freshness | Accepted §11 | OPEN |

All mapped initial 18 source findings, the stopped amendment's correction-1
13 IDs/F1–F10 causal obligations, expanded revocation, later residuals and
design-discovered counterexamples remain mandatory executable regressions.
The [old source STOP](W1A11-ContractAmendment-STOP.md) and its exhausted
two-correction history remain intact; this is not source acceptance.

The recorded 796-line lifetime-owner cohesion exception remains explicit,
following split-files guidance. No unrelated refactor or broad braces/cfg
migration is claimed.

## Scope and next step

Python >=3.11, PostgreSQL-primary support, supported secondary SQLite,
async-only future database access, in-process provider-neutral trusted context,
one convergent implementation, unchanged grammar and standalone `unenforced`
are preserved. Governed writes remain the release scope. External capture,
provider cryptography, decommissioning and online/mixed-version migration stay
deferred. W1's terminal wrong-method P3 remains assigned to W3 with originating
closure.

The next step is a separately authorized narrow contract/reference build:
freeze an execution brief and exact cohesive write boundary, implement this
accepted composition, add all causal/state-machine regressions, freeze a new
source tuple, then obtain independent Code/State review and originating
executable closure. It must preserve this design and the historical evidence.

This acceptance does not launch that build or authorize W2 planner/lowering,
database adapters, production async/thread execution, activation, credentials,
durability/crash-recovery claims, packaging, deployment or Git/GWZ work.
