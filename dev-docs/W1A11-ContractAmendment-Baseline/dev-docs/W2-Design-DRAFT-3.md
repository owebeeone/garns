Final consolidated architecture correction applied; writes stopped.

- Corrected design: [W2-QueryPlanningDesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W2-QueryPlanningDesign.md)
- Final SHA-256: `0b8b77a00c1b2c2b9e8748ae6fa743140352b4c602c29f62d914635faf7af44e`
- Revision-2 snapshot verified unchanged: `db8a802f12b53d19675378b4673fa13c2f7cd70b11811b339045e23908467074`
- Final remediation plan verified: `8141d0e508314cbf6778fbdd5732aadbf97a116db7893aeffc4cd499b0c0be13`

Corrections:

- Replaced proof-stripping with an enforceable `AdmittedPlanHandle`/`PlanAdmissionVerifier` seam.
- Made a reviewed W1 protocol amendment an explicit prerequisite: execute, consistent snapshot and subscribe must accept handles only, with no bare-`Plan` overload or compatibility fallback.
- Defined exact-instance registry identity, opaque handles, verifier binding, cache keys, lifecycle epochs, migration invalidation, close/reopen behavior, cross-runtime rejection and raw-plan rejection.
- Covered query execution, initial snapshots, subscriptions, refreshes, nested children and total statements.
- Added fail-closed mixed-version migration ordering and `plan_admission_v1` handshake.
- Preserved compiler/backend dependency direction: the backend consumes only contract foundations and its bound verifier; the pure bridge issues no trust or authority.
- Reclassified resource ceilings as independently reachable, semantic-registry, derived/dominated, payload-intersecting or aggregate bounds.
- Replaced the impossible 200,000-edge witness with closed-algebra arithmetic for the 10,256 derived reference guard and reachable interaction/precedence tests.
- Retained all prior schema, result-prerequisite, function-fingerprint, ordering and query/question decisions.

Verification completed:

- 13/13 control inputs verified.
- 48/48 source inputs verified.
- 26/26 accepted W1 entries verified.
- Round-two reports and remediation plan read in full and hash-checked.
- No source, test, contract, ADR, grammar, legacy integration, Git, dependency, database or service state changed.

The design remains explicitly non-implementable under current W1 bytes. If accepted, the next prerequisite is a separately scoped and reviewed W1 amendment covering both structural result roles and the admitted-handle/verifier protocol, followed by an execution brief assigning runtime registry and legacy integration ownership.

No findings are self-closed. This was the second and final architecture correction; any further architectural blocker stops the lane for operator direction.

STOP WRITES for pinning and fresh review.
