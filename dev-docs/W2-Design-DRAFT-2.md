Consolidated remediation applied; writes stopped.

- Corrected design: [W2-QueryPlanningDesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W2-QueryPlanningDesign.md)
- Corrected SHA-256: `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`
- Initial preserved object verified: `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`
- Remediation plan verified: `53646ff9e5258c6e1e9d60cc094bd756bb13441afca21e5f7322d6ee957fab23`

Corrections by finding:

- Consistency P2-1: specified hidden identity/group/parent key names, types, assembly behavior, and five normative result vectors. The current W1 `ResultShape` lacks visibility/role semantics, so a reviewed W1 amendment is explicitly required before ordinary/grouped/nested executable plans; no silent W1 redefinition.
- Consistency P2-2: closed all reachable canonical schemas and registries; selected reconstructed existing `I.PathRef` as the sole path model; defined `Order`, `TieBreak`, defaults, authority requirements, subplans, ordering, uniqueness and schema-completeness vectors.
- Consistency P2-3: defined backend-neutral per-function fingerprinting, exact `same` semantics, dialect-version separation, mutation rules, and golden fingerprints for all nine current pure functions.
- Safety P2-1: specified runtime-owned deterministic rebuild-and-compare admission over the complete recursive envelope. The pure bridge issues no trust; the existing W1 Plan-consuming backend interface remains unchanged after runtime admission.
- Safety P2-2: defined `garns.plan-limits/1` with exact payload, nesting, string, identifier, node, edge, expression, subplan, result, function, parameter/default, depth and total-work limits; deterministic fail-fast precedence and exact/plus-one vectors are included.

Sorting was corrected to preserve inherited SQLite behavior: distinct rows receive no invented tie-break, while ordinary/grouped/rank/nested behavior follows the cited current lowerer.

Verification:

- 13/13 control inputs: verified.
- 48/48 source inputs: verified.
- 26/26 accepted W1 manifest entries: verified.
- No product source, tests, contracts, ADRs, grammar, legacy integration, Git, dependency, database or service state changed.

The design is explicitly not fully implementation-ready under current W1 bytes. Next action, if reviewers accept the architecture, is a separately scoped/reviewed W1 result-shape amendment plus an execution brief assigning runtime admission and legacy wiring ownership.

No finding is self-closed. STOP WRITES for manager pinning and fresh review.
