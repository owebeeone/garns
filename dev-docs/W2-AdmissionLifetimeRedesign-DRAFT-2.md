COMPLETE — consolidated design-only remediation 1 applied; writes stopped.

- Corrected overlay: [W2-AdmissionLifetimeRedesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W2-AdmissionLifetimeRedesign.md)
- Lines: 825
- SHA-256: `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`

Resolved:

- M1: issuer-private, exact-command/effect worker authorization; public `TrustedContext` remains task-bound; separately reviewed A11/W1 amendment explicitly required.
- M2: closed local resource hierarchy and immutable ancestry separated from deployment generation states; ordinary close affects descendants only, while retained permits remain globally visible.
- M3: one authoritative pre-zero queue barrier handles queued buffers and concurrent late refresh enqueue exactly once.
- M4: finite stop-the-world activation with authoritative operator inventory and physical database/file access fencing; durable state alone is insufficient. Closed activation transitions cover fresh deployments, timeout, indeterminate recovery, unused rollback, first open, and post-open retirement.

The original operation-lifetime closure and all stopped-base closed cases remain preserved. Replacement remediation count is 1 of at most 2; stopped history remains intact.

START and END verification passed:

- Inputs: 11/11, SHA `9ea191415990e258ce8926022cd6c83f01eb4ec1df0f29ca1acf397332f2991c`
- Stopped manifest: 13/13, SHA `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`
- Source: 48/48, SHA `b24732fba66b3b649927ef94fc9704abc82641572a90e9374f0bc4990ba981b5`
- Controls: 13/13, SHA `b57cb68cae2458623622311bbea640afb3f36dd342c56461cb94f61c36d0f085`
- W1: 26/26, SHA `95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`
- Preserved initial overlay remains SHA `ee7c62ae3250d21008bccd41961ff6ed0896df1c0ed5e8881a7bacd855d3c638`
- Remediation plan remains SHA `ae071e535cd9164737d353244c8a9c7083fa6e0e8d94bf77a83391cfbcd67d49`

Historical manifest1 was not changed or treated as current after the mutable overlay changed. No other file, source, test, contract, ADR, grammar, service, dependency, database, Git, or GWZ state was modified.

