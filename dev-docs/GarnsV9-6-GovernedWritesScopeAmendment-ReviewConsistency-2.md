# Garns v9-6 governed write scope amendment — Consistency-axis focused re-verdict

**Review object:** `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md`, revised architecture draft, SHA-256 `d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe`  
**Baseline:** companion future-project brief `c566097019a44937171f888641b4ad9b574c39b3a0c10cf90c78a624b5e2cf41`; historical plan `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`; provider-neutral seam amendment `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01`; D6a/D7/D8 decisions `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f`; D4/D6b decisions `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce`. Sources were read directly from the pre-initial-commit product root. Start and end digest checks matched exactly.  
**Date:** 2026-10-03  
**Axis:** Consistency — changed-range coherence and agreement with the controlling contract graph. Independent, adversarial and read-only. The current Safety re-verdict remains peer-blind; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0, P1, P2 or P3 findings. The bounded clarification preserves the prior Consistency GO.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| None | The initial Consistency review reported no findings. Safety P2-1 is outside this axis’s closure authority. | The complete changed range was checked for contradictions and regressions against the controlling tuple. | No prior Consistency finding to close |

## Changed-range analysis

The remediation plan records one accepted Safety finding and one consolidated correction. The revised object changes only the governed-effect invariant and its A12/A14 consequences:

- Lines 55–59 broaden accounting from database-side effects of a governed mutation to all bound-data effects of every supported Garns operation, explicitly including schema management, migration DML/backfills, DDL conversions and induced cascades or triggers.
- Lines 60–64 define the admissible metadata-only generation case and require an ordered typed generation/refetch-required outcome before incompatible readers or cursors continue with stale state.
- Lines 66–71 make the three required W1 classifications and closure tests explicit while leaving real-database proof to later implementation gates.
- Lines 97–98 carry those rules into A12 and A14.

No change affects D5 closure, capture deferral, API shape, package ownership, backend support, identity, W6/P6 status, W7 dependencies, P12, Surface review, grammar or evidence preservation. The correction is a bounded invariant clarification, not a new interface or a new architectural root cause.

## 0. Evidence base

The focused review read:

- The complete revised amendment at lines 1–144.
- `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-RemPlan.md`, lines 1–18.
- The unchanged five-document tuple.
- Relevant parent-plan clauses for rollback and pre-effect refusal, migration and schema ownership, A12/A14/A15, W4/W5, P3/P5/P7/P9/P10, the migration verification matrix, replay cursor expiry/refetch and later implementation review.
- Relevant provider-neutral clauses to ensure the new effect wording did not alter trust, validity or capture-only deferrals.
- `docs/PRODUCT_LAYOUT.md` to verify package ownership remains unchanged.

Inspection used only `rg`, `sed`, `nl` and `shasum -a 256`. No build, test, installation, file write or Git mutation was performed. The exact tuple matched at both review boundaries.

## 2. Invariant analysis

### Effect accounting is now exhaustive without reintroducing external capture

The new rule is expressly limited to effects of supported Garns operations. It therefore closes the schema-management gap without extending guarantees to raw SQL, other services or administrative edits, which remain outside live/history guarantees at lines 47–54.

Migration DML, backfills, DDL conversions, cascades and triggers now have one consistent outcome grammar: atomically represented in the governed ledger/footprint/revision contract, or refused before effect. This agrees with the parent plan’s rollback suppression, earliest meaningful pre-effect refusal, W4 migration execution and P3/P5 requirements.

### Metadata-only transitions are distinguishable and falsifiable

The exception is not a label that implementations may assert freely. A12 must prove both absence of bound-row changes and absence of changes to observable retained-query values or result shapes. If reader or cursor compatibility does not hold, ordered typed generation/refetch-required termination is mandatory before stale continuation.

That rule agrees with the retained snapshot/watermark, cursor-expiry, refetch and schema-generation safety contracts. It neither permits silent continuation nor requires a fabricated data revision where no observable data effect occurred.

### The three W1 cases are satisfiable at the document gate

Lines 66–71 provide direct closure cases for:

1. metadata-only generation transition;
2. migration DML/backfill;
3. DDL conversion/cascade changing bound rows.

Each case has a binary, testable result: evidenced accounting/transition or pre-effect refusal. W1 owns classification and contract/state tests; later packages own real-database execution proof. This respects the existing W1/W4 separation rather than demanding implementation evidence from an architecture package.

### A12 and A14 remain within their retained scopes

A12 still owns migration locks, compatibility, mixed-version safety and ledger-generation interpretation. Adding transition classification and stale-continuation prevention is a direct refinement of that scope.

A14 still owns governed deployment privilege/RLS and effect coverage. Extending it from ordinary writes to supported schema-management operations and induced effects closes an omission without restoring external-writer roles, capture-source tamper controls or W6.

### No downstream gate contradiction was introduced

P3 can test supported migration shapes, P5 can test live continuity and refetch, P7 can test authored schema provenance, P9 can require reproducible evidence, and P10 can test operational migration behavior. P6 remains deferred because none of the new cases concerns an external capture source or worker.

P12 and the later Surface gate remain unchanged. No user-facing API name or compatibility surface is frozen by the clarification.

## 3. Risks and next action

No new consistency risk crosses the finding threshold. Implementation could still misclassify a data-changing migration as metadata-only, but the revised proof conditions and named W1 cases make that error falsifiable rather than permitted.

The next action is for the Safety reviewer to verify its original P2-1 counterexample on this exact tuple. If Safety also reports GO, W1 should encode the three classifications in A12/A14 contracts and state tests before handoff.
