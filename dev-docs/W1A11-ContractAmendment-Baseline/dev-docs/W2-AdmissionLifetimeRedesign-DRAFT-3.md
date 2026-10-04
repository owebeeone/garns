COMPLETE — final design-only correction 2 of 2 applied; writes stopped.

- Corrected overlay: [W2-AdmissionLifetimeRedesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W2-AdmissionLifetimeRedesign.md)
- Lines: 853
- SHA-256: `01257e07e7f8019c8af0afd3026aaff3b219fdb8611e5988eb87667563d6bb26`

Correction:

- Removed `ACTIVATION_RETIRED` and every retirement edge/capability.
- `ACTIVE(epoch)` now has no outgoing activation-state transition and persists across close, restart, migration, recovery, and binding non-reuse.
- Retirement/deactivation/reset/epoch-erasure requests refuse atomically without changing state, access fences, ownership, counts, buffers, A7 knowledge, or evidence.
- `ACTIVATION_INDETERMINATE` retains physical fencing until the existing authoritative restoration or activation-completion path resolves it.
- `ACTIVE_UNUSED` rollback remains unchanged.
- Added closure/static vectors for unsupported retirement requests and persistent active epochs.
- Replacement remediation count is now 2 of 2; no third architectural correction is authorized.

START and END verification passed:

- Inputs: 11/11, SHA `9ea191415990e258ce8926022cd6c83f01eb4ec1df0f29ca1acf397332f2991c`
- Stopped manifest: 13/13, SHA `5155fe376ffbc87c08816c691465f9925bf0c5b0e0008674d79a66e9bc3d5d36`
- Source: 48/48, SHA `b24732fba66b3b649927ef94fc9704abc82641572a90e9374f0bc4990ba981b5`
- Controls: 13/13, SHA `b57cb68cae2458623622311bbea640afb3f36dd342c56461cb94f61c36d0f085`
- W1: 26/26, SHA `95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`
- Preserved revision 2 remains SHA `28f7ca805242eef9cbcf2d709e1c5c80188f7fdd51fad83ee485ac1fe21943a4`
- Remediation plan 2 remains SHA `7929e939408e80696d98137214b1511d50fdda1807d72911bef0b33fae2dda8c`

Historical manifest2 was not changed or treated as current. No other file, source, test, contract, ADR, grammar, service, dependency, database, Git, or GWZ state was modified.

