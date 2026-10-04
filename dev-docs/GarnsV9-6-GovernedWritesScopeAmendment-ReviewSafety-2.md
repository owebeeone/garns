# Garns v9-6 governed write scope amendment — Safety-axis re-review

**Review object:** `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md`, revised draft for W1 review, SHA-256 `d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe`  
**Prior object:** SHA-256 `9ab01f08a4f95627dcf163159debc5f5a1b392fe7f2ea72b090df49453b70386`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`; SHA-pinned pre-initial-commit document review under plan §15 and `W0-ACCEPTANCE.md`’s explicit no-clean-commit claim. Sources were read directly from the working tree and verified by `shasum -a 256` at both start and end. No W1 implementation exists.  
**Companion:** `dev-docs/GarnsExternalWriteCapture-ProjectBrief.md`, SHA-256 `c566097019a44937171f888641b4ad9b574c39b3a0c10cf90c78a624b5e2cf41`  
**Historical plan:** `dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md`, SHA-256 `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`  
**Provider-neutral amendment:** `dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md`, SHA-256 `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01`  
**Operator decisions D6a/D7/D8:** SHA-256 `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f`  
**Operator decisions D4/D6b:** SHA-256 `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce`  
**Date:** 2026-10-03  
**Axis:** Safety — focused re-verdict of the original schema-management effect-accounting counterexample. Independent, adversarial, read-only. The other axis runs independently; nothing here relies on its current-round report. Filed verbatim by the lane owner as `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-ReviewSafety-2.md`.

**Verdict: GO** — original P2-1 is closed; zero open P0, P1, P2, or P3 findings. No new architectural root cause was found.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
|---|---|---|---|
| Safety P2-1 | Accepted: extend governed effect accounting to every supported schema-management operation and explicitly classify metadata-only transitions, migration DML/backfills, and DDL conversions/cascades | Yes. Amendment lines 55–71 impose atomic governed accounting or pre-effect refusal for all bound-data effects, constrain metadata-only transitions, prevent stale continuation, and name all three closure cases. Lines 97–98 make those rules explicit A12/A14 obligations. | Closed |

## Changed-range analysis

The remediation plan records one consolidated correction for Safety P2-1. The material changes are confined to:

- lines 55–59: effect accounting now covers every supported Garns operation, expressly including schema management, migration DML/backfills, DDL conversions, cascades, and triggers;
- lines 60–64: metadata-only generation transitions are allowed only when they change neither bound rows nor observable retained-query values/result shapes; incompatible readers and cursors receive an ordered typed generation/refetch-required outcome before stale continuation;
- lines 66–71: W1 must classify and test the three original closure cases, while real database proof remains assigned to later implementation gates;
- lines 97–98: revised A12 and A14 explicitly carry those classifications and effect-coverage rules into the ADR freeze.

These changes clarify the retained mutation boundary without adding an external-capture mechanism, public API, ownership reassignment, compatibility tier, or speculative future interface. They do not reopen the governed-write deferral decision or weaken any retained gate.

No changed clause introduces a new architectural root cause.

## 0. Evidence base

Read and checked:

- `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment-RemPlan.md`, lines 1–18;
- the complete revised governed-write amendment, with focused analysis of lines 36–71, 73–104, and 106–144;
- the unchanged controlling tuple previously examined, particularly historical plan lines 151–167, 254–287, 315–383, 599–647, 670–735, and 794–811;
- the provider-neutral amendment’s disclosure, expiry, cleanup, and executable-gate clauses;
- the external-write project brief, operator decisions, W0 acceptance, and product ownership map.

Inspection commands were limited to `nl` and `shasum -a 256`. No file, repository, build, test, or environment state was modified.

The exact six-document tuple matched at both start and end:

- revised object: `d68cb032bbaca0ec966b55c381e3a34c49b3a2edb46e39a3821fb0df3f7160fe`;
- companion: `c566097019a44937171f888641b4ad9b574c39b3a0c10cf90c78a624b5e2cf41`;
- historical plan: `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`;
- provider-neutral amendment: `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01`;
- D6a/D7/D8 decisions: `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f`;
- D4/D6b decisions: `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce`.

## 2. Invariant analysis

The original counterexample no longer survives the revised text:

1. **Migration DML/backfill:** A supported migration that updates bound rows is expressly within lines 55–59. It must atomically record every bound-data effect in the governed ledger/footprint/revision contract or refuse before effect. Lines 66–68 make this a named W1 classification and test, and line 97 carries it into A12.

2. **DDL conversion or cascade:** A supported conversion, cascade, or trigger-induced row change is also expressly covered by lines 55–59. Lines 69–70 require the same atomic accounting or refusal, while lines 97–98 bind the rule into A12 and A14. It can no longer conformingly commit changed rows while leaving live/replay state unchanged.

3. **Metadata-only generation change:** Lines 60–64 prohibit calling a transition metadata-only if it changes bound rows or observable retained-query values/result shapes. Where a reader or cursor is incompatible, generation publication must be ordered with a typed refetch-required outcome before stale continuation. Lines 66–67 require W1 to classify and test that case.

The corrected document therefore restores the safety invariant: no supported Garns path may create bound-data or observable retained-query changes that bypass governed revision accounting and continue silently as valid live/replay state.

The broader failed attacks from the initial review remain intact: credential custody and DBA bypass are honestly bounded; unmanaged SQL is outside guarantees; multi-instance coordination and ambiguous-commit reconciliation remain required; expiry and cleanup remain fail-closed; capture-only gates are deferred rather than passed; inherited capture surfaces must be classified and disabled or refused; and P12 plus the later public Surface review remain mandatory.

## 3. Risks and next action

Document acceptance still does not prove database behavior. W1 must encode the three classifications in A12/A14 and contract/state tests, and later implementation gates must supply the real SQLite/PostgreSQL evidence. The revised document states that separation correctly, so this is scheduled evidence rather than an open defect.

The Safety-axis next action is acceptance of the revised digest.
