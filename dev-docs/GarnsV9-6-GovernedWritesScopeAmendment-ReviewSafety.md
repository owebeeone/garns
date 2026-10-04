# Garns v9-6 governed write scope amendment — Safety-axis review

**Review object:** `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md`, draft for W1 review, SHA-256 `9ab01f08a4f95627dcf163159debc5f5a1b392fe7f2ea72b090df49453b70386`  
**Baseline:** `/Volumes/projects/limbo/datascad/garns-v9-6`; SHA-pinned pre-initial-commit document review under plan §15 and `W0-ACCEPTANCE.md`’s explicit no-clean-commit claim. Sources were read directly from the working tree and verified by `shasum -a 256` at both start and end. No W1 implementation exists.  
**Companion:** `dev-docs/GarnsExternalWriteCapture-ProjectBrief.md`, SHA-256 `c566097019a44937171f888641b4ad9b574c39b3a0c10cf90c78a624b5e2cf41`  
**Historical plan:** `dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md`, SHA-256 `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`  
**Provider-neutral amendment:** `dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md`, SHA-256 `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01`  
**Operator decisions D6a/D7/D8:** SHA-256 `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f`  
**Operator decisions D4/D6b:** SHA-256 `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce`  
**Date:** 2026-10-03  
**Axis:** Safety — degraded and mixed-version paths, irreversible preconditions, disclosure, stuck states, fail-closed direction, and blast radius. Independent, adversarial, read-only. The Consistency axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks. No P0, P1, or P3 findings. I pre-commit to GO on a revision that resolves P2-1 as specified.

---

## 0. Evidence base

Read in full:

- `../AGENTS_GWZ.md`
- `AGENTS.md`
- `/Users/owebeeone/.claude/skills/review-loop/SKILL.md`
- its canonical `references/review-prompt-template.md`
- all six SHA-pinned tuple documents
- `dev-docs/W0-ACCEPTANCE.md`
- `docs/PRODUCT_LAYOUT.md`

Focused line evidence included:

- governed-write boundary and database-induced effects: scope amendment lines 36–58;
- retained durability, coordination, recovery, retention, and generation rules: lines 60–71;
- revised A2–A15 obligations: lines 73–91;
- release gates and exact external-only deferrals: lines 93–110;
- dormant inherited capture paths and release non-claims: lines 112–131;
- historical A4/A12/A15 decisions: plan lines 151–167;
- W1 transaction, reconciliation, cleanup, and refusal contracts: plan lines 254–287;
- migration execution and privilege inspection: plan lines 315–383;
- P2–P12 gates and verification matrix: plan lines 599–647;
- adversity, observability, P12, and Surface-review requirements: plan lines 670–735 and 794–811;
- provider-neutral disclosure and expiry rules: provider-neutral amendment lines 42–96 and 204–261;
- external-capture boundary and future evidence: project brief lines 11–78.

Inspection commands were limited to `cat`, `nl`, `sed`, `rg`, `wc`, `pwd`, and `shasum -a 256`. No build, test, installation, mutation, or file write was performed.

The start and end SHA tuples were identical and exactly matched the instructed tuple.

## 1. Findings

### [P2-1] Supported schema-management writes are admitted into the correctness boundary without an effect-accounting rule

**Location:** `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md` lines 40–42, 55–58, and 84–85; controlling plan lines 164, 325, 378, 606, and 637.

**Violated invariant:** Every supported operation that changes bound data must either atomically represent all resulting data effects in the governed ledger/footprint/revision contract or refuse before commit. Deferring external capture must not create an internal supported path whose effects bypass live history.

**Credible sequence:** The amendment says live correctness, ledger history, and replay remain guaranteed when bound data is modified through either supported governed paths **or supported Garns schema-management operations** (lines 40–42). It then explicitly requires effect representation or pre-effect refusal only for “a supported governed operation,” including cascades or triggers (lines 55–58). A supported migration can execute a data-changing conversion, backfill, constraint action, cascade, or migration DML through the async migration boundary. It satisfies the stated routing condition because it is a supported Garns schema-management operation, but the revised A12 obligation only preserves locks, mixed-version safety, and governed-ledger generation interpretation (line 84), while A14 speaks generally of effect-coverage boundaries (line 85). Neither clause says that schema-management data effects must enter the governed transaction/ledger/footprint contract or cause refusal before commit.

The historical plan confirms migration is an executable public boundary and supported backend operation (lines 325 and 378), but its migration verification row is limited to the supported subset and lock/rollout cases (line 637). P3 only requires execution of claimed migration shapes (line 606). Therefore W1 can conformingly define a supported data-changing migration whose database rows commit while no corresponding revision is published. Existing subscribers and replay consumers then retain a pre-migration view even though a fresh static query sees the changed committed state—the same split-brain outcome the amendment correctly rejects for external writes.

**Impact:** Concrete live/replay correctness loss through a Garns-supported path, with misleading compliance: deployment has excluded unmanaged writers, yet the documented guarantee still fails. The absence of external capture makes later discovery or repair less likely.

**Required correction:** Extend the effect-coverage rule at lines 55–58, or the revised A12/A14 obligations, to cover every supported Garns schema-management operation that can modify bound data. Require one of:

1. atomic governed ledger/footprint/revision representation of all induced row effects; or
2. a pre-commit refusal for data-changing schema operations outside the evidenced subset.

State that metadata-only migrations may use a separately defined generation transition only where W1 proves that no bound-data result can change without a corresponding governed revision/refetch outcome.

**Closure test:** At this document gate, trace three named cases through the revised obligations: a metadata-only generation change, migration DML/backfill, and a DDL conversion or cascade that changes bound rows. Each must be unambiguously classified as atomically represented, forced into a typed refetch/generation transition with no stale continuation, or refused before commit. W1 must then encode that classification in A12/A14 and the contract/state tests; later implementation evidence, not this document review, proves the database behavior.

## 2. Invariant analysis

The following attacks did not produce additional findings:

- **Govern-only condition and bypass honesty:** Lines 43–54 explicitly place credential custody, trusted-host restriction, and database privileges in the deployment precondition; acknowledge that the same database role cannot distinguish Garns from arbitrary SQL; disclaim protection against a trusted administrator or compromised host; and state that raw SQL can invalidate live/history guarantees. This avoids falsely claiming that a database role alone enforces provenance.
- **Database-induced effects from ordinary governed writes:** Lines 55–58 correctly keep supported cascades and triggers inside the ledger/footprint contract or require refusal before effect. P2-1 is confined to the separately admitted schema-management route.
- **Durable ledger, ambiguous commit, and reconciliation:** Lines 64–67 retain atomic mutation/ledger recording, durable transaction identity, known-abort/known-commit/indeterminate reconciliation, commit-safe publication, and replay. The historical P2/P4 gates and fault matrix remain applicable.
- **Multi-instance coordination:** It is expressly retained at line 66 rather than being accidentally treated as an external-capture feature.
- **Expiry, invalidation, and cleanup:** Revised A11 retains governed expiry, counterfeit, and disclosure requirements. The provider-neutral amendment still requires validity checks before each database effect and commit request, typed rollback before commit, preservation of reconciliation after a commit request, and bounded subscription cleanup. Capture-only expiry clauses are properly deferred with capture.
- **Disclosure:** Governed secret-minimization and named-provider-absence checks remain through lines 102–105 and the retained P2/W3/W7 requirements. Deferral is limited to capture actors and capture operations.
- **Mixed-version and generation safety:** Revised A12 expressly retains migration locks, mixed-version safety, and governed-ledger generation interpretation/retention. Pending external-capture state alone is deferred.
- **Stuck-state direction:** Bounded queues, retention, cursor expiry/refetch, transaction reconciliation, deadlines, cleanup, and observability remain required. The text does not convert capture claims or acknowledgements into governed runtime states.
- **Inherited capture surfaces:** Lines 122–126 preserve historical evidence while requiring W1/W7 to classify legacy surfaces so the release neither advertises nor enables unverified capture. A remaining compatibility surface must refuse unsupported before effect (line 80).
- **Gate precision:** P6 is explicitly “deferred/out of release scope,” never PASS. Capture-only matrix cells and external-source-only cases are deferred rather than credited. P0–P5 and P7–P12 remain required for governed claims.
- **Final independent review and public Surface review:** Lines 99–101 retain P12 and the Surface review at the later public API freeze. No public names are frozen by this amendment.
- **Future project containment:** The project brief selects no mechanism, creates no repository or ownership assignment, and imposes no speculative interface on v9-6. The amendment also forbids delaying W1 to design it.

## 3. Risks and next action

Residual risk below the finding bar is that operational separation ultimately depends on correct credential custody outside Garns; the amendment discloses this limitation and retains deployment privilege/documentation gates, so it is not a defect in the scoped architecture.

The single next action is a bounded amendment edit resolving P2-1 by bringing data-changing supported schema-management operations explicitly under effect accounting or pre-commit refusal, followed by a focused Safety re-verdict on the new digest.
