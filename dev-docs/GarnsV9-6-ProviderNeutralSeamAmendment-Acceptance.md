# Garns v9-6 provider-neutral seam amendment — acceptance synthesis

**Status:** **accepted at the exact two-document tuple below after
`ReviewConsistency-3` and `ReviewSafety-3` reported GO; this accepts the
provider-neutral seam and explicit ADR dependency corrections only**.  
**Date:** 2026-10-03  
**Lane owner:** manager synthesis

## Accepted tuple

| Document | SHA-256 |
|---|---|
| [`GarnsV9-6-PostgresAsyncImplementationPlan.md`](GarnsV9-6-PostgresAsyncImplementationPlan.md) | `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512` |
| [`GarnsV9-6-ProviderNeutralSeamAmendment.md`](GarnsV9-6-ProviderNeutralSeamAmendment.md) | `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01` |

The parent plan remains immutable historical evidence. The amendment controls
only its explicit D7, W2, W6, W7 and W8 replacements/extensions. Builders and
later reviewers must receive both documents at these exact digests plus the
decision and ADR artifacts required by their package.

## Final verdict merge

| Axis | Filed report | Verdict | Findings |
|---|---|---|---|
| Consistency | [`ReviewConsistency-3`](GarnsV9-6-ProviderNeutralSeamAmendment-ReviewConsistency-3.md) | **GO** | none |
| Safety | [`ReviewSafety-3`](GarnsV9-6-ProviderNeutralSeamAmendment-ReviewSafety-3.md) | **GO** | none |

Both reviewers independently verified the same exact tuple at the beginning and
end of review. No P0, P1, P2 or P3 remained, and neither found a new
architectural root cause.

## Review history

- Initial amendment:
  - [`ReviewConsistency`](GarnsV9-6-ProviderNeutralSeamAmendment-ReviewConsistency.md): GO
  - [`ReviewSafety`](GarnsV9-6-ProviderNeutralSeamAmendment-ReviewSafety.md): NO-GO, five P2
  - [`RemPlan`](GarnsV9-6-ProviderNeutralSeamAmendment-RemPlan.md)
- Remediation round 1:
  - [`ReviewConsistency-2`](GarnsV9-6-ProviderNeutralSeamAmendment-ReviewConsistency-2.md): NO-GO, one P2 and one P3
  - [`ReviewSafety-2`](GarnsV9-6-ProviderNeutralSeamAmendment-ReviewSafety-2.md): GO
  - [`RemPlan-2`](GarnsV9-6-ProviderNeutralSeamAmendment-RemPlan-2.md)
- Final focused re-verdict:
  - Consistency GO
  - Safety GO

The amendment used both permitted remediation rounds. Future implementation
defects are handled at their package review gates; a new architectural defect
in this amendment requires a new operator-authorized review object rather than
another amendment patch.

## Accepted provider-neutral contract

The accepted scope establishes:

- D7 is seam-only for v9-6. A named identity provider is not an admitted v9-6
  outcome and requires a separately reviewed future package.
- The trusted host authenticates externally and issues/resolves a provider-
  neutral Garns capability. Public request data cannot construct authority.
- Garns receives only immutable, request-bound normalized claims. Raw provider
  tokens, sessions, assertions and secrets remain outside Garns-owned objects
  and outputs.
- Context validity, invalidation and renewal have explicit effect, commit,
  subscription and capture boundaries without weakening three-way commit or
  idempotent capture reconciliation.
- Governed writer, external source actor, capture processor and capture
  administrator are distinct identities with fail-closed provenance.
- W3, W6, P2, the verification matrix and W7 contain executable counterfeit,
  expiry, disclosure, actor-attribution and named-provider-absence gates.
- W2 explicitly depends on A2; W7 explicitly consumes A1–A15; W8 changes must
  classify and name their ADR dependencies.
- Exact public API shape remains an A3/A11/W3 decision and must receive the
  later Surface review required by the parent plan.

## Remaining launch blockers

Acceptance of the document tuple is not authorization to start a builder.

Before W0:

- **D6a:** choose the supported Python version range.
- **D8:** choose one convergent implementation or multiple isolated whole
  builds, and allocate the corresponding product/research roots.

Before W1 can hand off its accepted A1–A15 tuple:

- **D4:** choose SQLite as a supported secondary runtime or test/development
  only.
- **D5:** choose the first PostgreSQL capture branch.
- **D6b:** choose the supported PostgreSQL version range.

No builder prompt is authorized until the decisions required by that package
have their named pre-launch artifacts.
