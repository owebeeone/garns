# W2 composed query-planning/lifetime design — acceptance

**Status:** ACCEPTED DESIGN ONLY; amendment and implementation gated
**Date:** 2026-10-04
**Owner:** manager

## Accepted object

Accept ONLY the exact composed pair:

| Component | SHA-256 |
|---|---|
| [Stopped W2 base](W2-QueryPlanningDesign.md) | 0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e |
| [Final lifetime overlay](W2-AdmissionLifetimeRedesign.md) | 01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26 |

[Manifest 3](W2-AdmissionLifetimeRedesign-MANIFEST-3.sha256), eighteen entries,
has SHA-256 86be2201fe5211a9e0ce42346cbd155074e22c23c3430a44072133f66c06b2e2.
The overlay's exact supersession map controls only the named lifetime clauses;
all remaining base requirements are retained.

This additive acceptance overrides draft/nonaccepted status wording only for
this exact composed pair. Neither document alone is accepted. The prior
[W2 STOP](W2-Design-STOP.md), exhausted old-object history, prior reports and
preserved Initial/Revision2 overlays remain historical and unchanged.
Historical manifests 1 and 2 retain their original bytes, but their mutable
overlay entry no longer names the current reviewed revision; the preserved
snapshots retain that original content. They are not current verification
manifests.

## Required verdict merge

Two fresh, independent, peer-blind 5.6 Sol full reviewers returned GO on the
same exact final tuple. Both required originating Safety checks also returned
GO after retracing their actual counterexamples, including the removed
retirement capability. Complete reports were filed verbatim.

| Report | Verdict | SHA-256 |
|---|---|---|
| [Consistency 3](W2-AdmissionLifetimeRedesign-ReviewConsistency-3.md) | GO | f0bb7b451d78e0fbb69dd834601c94287a99fa2c11857f477367773f31632743 |
| [Safety 3](W2-AdmissionLifetimeRedesign-ReviewSafety-3.md) | GO | 889f3bfb13490217a456004ea052db545898e9d77e057b061ad2e4c639d799b2 |
| [Originating stopped Safety](W2-AdmissionLifetimeRedesign-OriginSafetyClosure-3.md) | GO | 2d0a0c9e9e46f4345a7a74a3819af50155bdf02a8c76a901faa0cedc7d6e88da |
| [Originating replacement Safety](W2-AdmissionLifetimeRedesign-OriginReplacementSafetyClosure-2.md) | GO | bc5307e64e5ef5640403e1548368e7ee7cc09f1cdcfa24ddb9f4c30026ab1430 |

[Review evidence manifest](W2-AdmissionLifetimeRedesign-ReviewEvidence.sha256),
five entries, has SHA-256
4f4931f516cdf117e2ab3a63176471f870c8a93f7acf706667be8d319ef20123.
No P0/P1/P2/P3 finding remains open on the composed design. No new architecture
root was reported after the final permitted correction. Replacement used
exactly two consolidated architecture remediation rounds; no automatic cap
reset or third correction was used.

Fresh full reviewers also reverified prior Consistency cases after the final
material state-grammar change; the prior focused Consistency closure remains
historical evidence, not a mismatched-tuple final verdict.

## What the review changed

The accepted design establishes whole-operation ownership rather than a
point-in-time admission check:

- exact-instance leases retain plan, generation and resource ownership through
  lowering, dispatch, adapter/fetch work, snapshot, assembly and publication;
- local close drains only its immutable resource descendants; migration alone
  drains admission across the qualified deployment;
- cancellation and non-killable workers retain typed containment and permits
  until authoritative quiescence, including reads without transaction IDs;
- issuer-private command/effect authorization is a proposed A11 extension;
  the public trusted context remains task-bound and claim-free;
- a single pre-zero queue barrier invalidates old buffered deliveries, rejects
  late enqueue and preserves active handoff counts;
- stop-the-world activation requires authoritative operator inventory plus
  physical legacy-access fencing, not a handshake or durable marker alone;
- active protocol epoch persists. No protocol retirement/reset/deactivation
  capability is offered; deployment decommissioning remains separate future
  work.

All earlier base provenance, result roles, canonical resource bounds, function
fingerprints, authored mapping and query/question cases remain preserved.

## Verification and unchanged boundaries

Manager independently inspected the full original/corrected overlay and final
changed ranges. Final recursive verification passed every entry with exact
counts 5/18/11/13/48/13/26 for review evidence, final tuple, replacement inputs,
stopped tuple, source, controls and accepted W1. Each reviewer verified its
tuple at START and END. No tuple movement was reported.

Accepted W1, source/test/grammar and control bytes remain unchanged.
No build, test suite, database, service, dependency install, Git or GWZ change
was performed in this design lane. This is not new executable, PostgreSQL,
async, crash, thread, supported-version or physical-fence evidence. The accepted
no-Git filesystem exception applies; no clean commit or landing is claimed.

## Next gate, not launch authority

The next proposed step is a separately authorized, scoped W1/A11 amendment
brief and review defining the structural result roles, lease/verifier/resource
contracts, nontransaction close knowledge and issuer-private worker-authority
extension together. Frozen W1/A11 cannot enable this design as currently
written.

An execution brief must assign the single integration owner and exact paths,
legacy fail-closed wiring, runtime/backend lifetime and deployment activation
ownership, ordering and evidence gates. Activation implementation and any
actual deployment activation require separate authority and independent review.
Implementation must prove the design with genuine backend/async/worker and
database evidence at its proper gates. W3 Surface and final P12 remain required.

This acceptance authorizes none of those amendments, builds, service changes,
credential rotations or implementation dispatches. External-write capture
stays deferred; unchanged grammar and `unenforced` are retained.

