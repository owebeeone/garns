# Garns v9-6 governed write scope amendment — Consistency-axis review

**Review object:** `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md`, binding operator scope decision and architecture draft for W1 review, SHA-256 `9ab01f08a4f95627dcf163159debc5f5a1b392fe7f2ea72b090df49453b70386`  
**Baseline:** companion future-project brief `c566097019a44937171f888641b4ad9b574c39b3a0c10cf90c78a624b5e2cf41`; historical plan `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`; provider-neutral seam amendment `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01`; D6a/D7/D8 decisions `079517aa59cced254b45dcb0f3268fa0e2e9beed59796792beaa67256df2764f`; D4/D6b decisions `94b9e50cd0e4752ece180fd25188b2f3c4ec93992aba8b30083676bf8b1185ce`. Sources were read directly from the pre-initial-commit product root under the explicit no-clean-commit claim. Start and end digest checks matched exactly.  
**Date:** 2026-10-03  
**Axis:** Consistency — internal coherence, agreement with the controlling document graph, exact supersession, satisfiable gates and unstated impacts. Independent, adversarial and read-only. The Safety axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0, P1, P2 or P3 findings.

---

## 0. Evidence base

The review read and line-audited:

- `dev-docs/GarnsV9-6-GovernedWritesScopeAmendment.md`, lines 1–131.
- `dev-docs/GarnsExternalWriteCapture-ProjectBrief.md`, lines 1–81.
- `dev-docs/GarnsV9-6-PostgresAsyncImplementationPlan.md`, especially constraints and scope at lines 64–167, W1 at 254–289, W6/W7 at 438–510, gates and verification at 599–650, failure/observability/documentation requirements at 672–765, review rules at 767–811, and the decision register at 813–859.
- `dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment.md`, including its supersession boundary, trusted-context rules, capture actor model, W6/W7 extensions, verification matrix, dependency graph and closure tests.
- `dev-docs/GarnsV9-6-ProviderNeutralSeamAmendment-Acceptance.md`, including the accepted tuple and remaining historical launch blockers.
- Both operator-decision records, including their deliberately historical statements that D5 remained open.
- `dev-docs/W0-ACCEPTANCE.md`, `dev-docs/GarnsV9-6-W0-ExecutionBrief.md`, `dev-docs/W0-REPORT.md`, `AGENTS.md`, `../AGENTS_GWZ.md`, and `docs/PRODUCT_LAYOUT.md`.
- The review-loop skill and canonical reviewer-prompt template.

Inspection used only `cat`/`sed`/`rg`/`nl`/`wc` and `shasum -a 256`. No build, test, installation, file write or Git mutation was performed.

The exact six-document tuple was hashed before substantive inspection and again after it. Both checks returned the supplied digests.

## 2. Invariant analysis

### D5 closure and precedence

The historical records genuinely leave D5 open: the original plan’s decision register requires selection of a first W6 branch, and the D4/D6b record repeats that status. The reviewed amendment does not mistake those preserved historical statements for current authority. Its precedence clause explicitly supersedes only the open D5 status and release requirements for external capture (lines 24–27), then closes D5 as “no external-capture branch in v9-6” without selecting triggers or logical decoding (lines 29–34). This is a valid additive decision artifact and does not rewrite accepted historical evidence.

### A1–A15 closure remains complete and scoped

The amendment preserves all ADR identifiers, so the parent P1 requirement that A1–A15 close remains satisfiable. A2/A3, A4, A5, A11, A12, A14 and A15 receive explicit revised obligations at lines 78–86; A1, A6–A10 and A13 remain required at line 88. The changed scopes match the original ADR concerns:

- A4 retains governed transaction identity, commit-safe ordering and replay while removing only external-source ordering.
- A5 becomes an explicit deferral/non-claim record rather than a speculative detector or adapter design.
- A11 retains governed execution, transaction, subscription, provenance, expiry, counterfeit and disclosure requirements while deferring external processor/source/admin concerns.
- A12 retains migration locking, mixed-version safety and governed ledger-generation interpretation.
- A14 is narrowed from external-writer capture controls to the still-required governed deployment privilege/RLS and Garns-caused effect-coverage boundary.
- A15 remains unchanged for governed replay and retention.

The explicit dependency-preservation instruction at lines 88–91 prevents the scoped ADRs from becoming merely documentary placeholders.

### W6/P6 deferral and W7 topology

The new path `W0 → W1 → W2 → W3 → W4 → W5 → W7` is internally consistent. W6 has no assignment or merge obligation, and P6 must be reported deferred rather than passed (lines 93–101). W7 consumes accepted W0–W5 tuples, the scoped A1–A15 tuple and this amendment, expressly without a W6 tuple (lines 95–98).

This precisely supersedes both the parent W7 dependency and the provider-neutral amendment’s strengthened W7 dependency. The otherwise stale `docs/PRODUCT_LAYOUT.md` W7 row is also identified by name as superseded while ownership paths remain unchanged (lines 112–114). Dormant W6 and capture-research ownership therefore does not create an active writer or release dependency.

### Provider-neutral identity obligations

The amendment separates capture-only identity obligations from governed ones without weakening the accepted trust seam. It defers the provider-neutral amendment’s W6 extensions, external-actor checks, capture-only matrix cells and W7 consumption of W6 counterfeit/claim/ack evidence, while explicitly retaining governed W3/W7 trust, lifecycle, disclosure and named-provider-absence checks (lines 102–105). A11 independently retains governed provenance, expiry, counterfeit and disclosure requirements (line 83).

Mixed verification clauses remain classifiable: execute, transaction and subscription cases survive; capture acquisition, claim, source attribution, reconciliation and acknowledgement cases are deferred. The text does not defer the underlying immutable request-bound context, commit reconciliation, subscription validity or secret-minimization invariants.

### Retained gates and Surface review

The amendment keeps P0–P5 and P7–P12 for their governed claims, including independent final Code/State review and later Surface review at the public API freeze (lines 99–101). This agrees with the parent plan’s P12 definition and lines 804–811. It also states that no new public API names are frozen. The reviewed object therefore neither prematurely triggers nor silently removes the Surface gate.

### Governed side effects and external-write non-claims

The supported-write contract is coherent with live, ledger and replay requirements. It excludes unmanaged external writes from guarantees, but does not use that exclusion to lose effects caused by Garns itself: supported cascades and triggers must be represented in the ledger/footprint contract or refused before effect (lines 55–58). This preserves the parent’s rollback, commit publication, live equivalence and provenance requirements.

The privilege statement is also exact: deployment must restrict unmanaged access, but shared credentials cannot distinguish Garns from arbitrary SQL, and no defense against a trusted administrator or compromised host is claimed (lines 43–46). Documentation and release evidence must carry these restrictions and non-claims (lines 128–131).

### Grammar, code and evidence preservation

The amendment requires inherited W0 grammar, capture code, tests and baseline evidence to remain preserved (lines 122–126). This agrees with W0’s byte-identical grammar and generated-evidence records. Preservation is not confused with a shipping claim: legacy capture surfaces must be classified at W1/W7, and release material must neither advertise nor enable unverified external capture. Later retirement must be explicit and preserve historical evidence.

### Future-project boundary

The companion brief is non-blocking and non-speculative in the relevant sense. It records candidate mechanisms for a later comparison but selects neither, creates no repository, launches no agent, assigns no package location and freezes no capture interface (lines 72–78). Its evidence section treats historical W6/P6 and capture-specific tests as inputs to reassess, not inherited acceptance (lines 58–70). It therefore describes future work without smuggling a seam, implementation obligation or release blocker back into v9-6.

## 3. Risks and next action

No consistency defect meets the finding threshold. The remaining risk is execution drift: W1 could accidentally copy historical capture obligations into ADRs or W7 could treat P6 as PASS. The amendment already supplies falsifiable controls against both through explicit scoped A1–A15 records, deferred-gate reporting, exact dependency construction and release documentation requirements.

The next action is to include this exact amendment and companion brief in W1’s independent architecture review, then freeze and accept the scoped A1–A15 tuple before any downstream handoff.
