COMPLETE — STOP-WRITES testimony

Edited only [W1A11-WorkerExitRedesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W1A11-WorkerExitRedesign.md).

Final object:

- SHA-256: `167f6ce726ba5908a01a270f98144731959587f671de43d72640c33eef685fcc`
- Size: 1,121 lines / 77,938 bytes
- Status: correction 2/2 design candidate; not accepted, no self-GO, no implementation authority.
- Manager may file these bytes as DRAFT-3.

Disposition:

- `Consistency-2 P2-1`: neutral commit now atomically consumes the candidate, updates cursor/span/replay, records refresh `SUCCEEDED`, and releases exactly once with no batch, buffer permit, or publication. Every known current-candidate error has an explicit unchanged-owner, quiescent terminal-release, or containment-until-stop disposition.
- `Consistency-2 P2-2`: current issued candidates exist only in charged operation records; committed replay is limited to `R == C`. Candidate or receipt identities absent from those bounded authoritative records uniformly return `RefreshRecordUnavailable`, without cursor/provenance reconstruction or side history.
- `Safety-2 P2-1`: specialized `settle_delivery_success` is the sole iterator-handoff final barrier, atomically committing publication, FIFO settlement, terminal success, and one release before exposure. Generic completion cannot bypass it. Non-success uses retirement/queued invalidation first, retains the active charge through exact worker-plus-iterator stop, then specialized terminal `REFUSED` settlement releases once.

Required causal evidence is explicit for:

- charged neutral success, replay, close/migration races, and quiescent/nonquiescent refetch;
- more than `R` commits with evicted, in-window, current, cross-registration, and counterfeit identities;
- last-permit handoff pauses before/after the single success commit against migration, close, fence, and receiver loss;
- all non-success causes, cleanup failure, replay/conflict, queued invalidation, and exact quiescent release.

The prior five stopped roots, six correction-1 IDs, finite `M` command ledger, body-before-cleanup primary ordering, receiver-loss handling, activation-bracketed membership, migration product, no-raw-`Plan`, task-bound claim-free context, unchanged result roles, parent-owned commands, one permit, and A7/quiescence separation remain preserved. No finding is claimed closed.

Complete correction-2 inputs read:

- RemPlan-2 `6f6ef5e31e7e2c488804a684337ad6f49db3ef7915d93a8a21eb5d8f78a1876e`
- RemInputs-2 `874a747171976fd383745e4cb23422f4e909118a532b40f9c743e935234a3993`
- Consistency-2 `740e14350efe532cce940c655ef4a03b76f9ffd46f96df353ef06503149d0dec`
- Safety-2 `6d3785cdcddeb3b0e1589e28da3ceba5ece4d328707fe4c8449b665658d5f3ff`
- All four Origin closure-2 reports, plus the controlling original instructions, skills, brief, accepted pair, ADRs, stopped reports, and relevant frozen code/tests already read for this continuous design task.

START and END guards passed:

- RemInputs-2: `25/25`, manifest SHA `874a7471…993`
- Revision-2 archive map: `100/100`, SHA `4d1cbcc6…34c`
- Revision-1 archive map: `88/88`, SHA `50550d3e…1e8`
- RemInputs-1: `13/13`, SHA `59896d17…347c`
- Original Inputs: `19/19`, SHA `46b37274…8a52`
- Frozen source MANIFEST-3: `71/71`, SHA `23db272c…424`
- ReadOnly: `111/111`, SHA `185e748c…8d`
- ProductGuard: `614/614`, SHA `6446ccb2…818`

The historical MANIFEST-2 was not checked against changed live design bytes; its 100-entry Revision-2 product-root archive map was used as required.

Inspection used only `rg`, `sed`, `nl`, `cat`, `diff`, `wc`, and `shasum`; edits used `apply_patch`. No source, tests, ADRs, accepted documents, reports, manifests, archives, Git/GWZ state, network, service, database, bytecode, generator, or runtime implementation was changed or invoked.

Production executor ordering, locks, async/thread behavior, databases, durability, crash recovery, physical/cross-process fencing, provenance, credentials, activation, packaging, public W3 surface, and deployment remain explicitly deferred. The next authorized action is manager pinning and independent focused Consistency-2/Safety-2 re-verdict plus originating retracing—not implementation.
