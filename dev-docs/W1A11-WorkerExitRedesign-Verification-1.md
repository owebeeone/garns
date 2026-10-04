# W1/A11 worker-exit replacement — manager verification 1

**Date:** 2026-10-04
**Scope:** filesystem integrity and review filing; no prospective/source acceptance

The manager read the complete 737-line/45,357-byte initial design in three
nontruncated ranges (1–250, 251–500, 501–EOF). It has 14 numbered sections and
26 Markdown fences. The manager filed the drafter's complete stop-writing
testimony and all returned review reports verbatim.

## Independently reproduced guard results

From the product root, before design correction:
- review MANIFEST-1: 88/88;
- initial Inputs: 19/19;
- stopped source MANIFEST-3: 71/71;
- ReadOnly: 111/111;
- ProductGuard: 614/614.

All `shasum -a 256 -c` commands exited 0, with no failed entries.
Revision1's derived VERIFY-from-product-root map also verifies 88/88; RemInputs-1
verifies 13/13. Only initial design/DRAFT paths are rebased to the archive;
the other frozen inputs stay in place. Original MANIFEST-1 remains byte-identical.

## Filed evidence and verdict

- OriginStateClosure-1: prospective design GO; source findings remain OPEN.
- ReviewConsistency-1: NO-GO four P2s.
- ReviewSafety-1: NO-GO two P2s.
- RemPlan-1 merges six blocking IDs into five roots.

Independent convergence: both full axes found the unbounded neutral lineage
and receipt-retention path. The origin review's narrower GO does not override
the full blockers. No finding is self-closed.

Correction1 is authorized only for the single design file. Fresh full dual
reviews and same-origin closure are required after the revision is pinned.
No source/test/ADR edit, actual database/runtime/planner build, test-success
closure claim, Git/GWZ mutation, network or deployment occurred in manager
verification. Tests of the known stopped source would not prove the new design.

