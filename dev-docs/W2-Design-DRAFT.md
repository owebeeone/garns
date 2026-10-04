W2 design draft completed and writes stopped.

- Sole write: [W2-QueryPlanningDesign.md](/Volumes/projects/limbo/datascad/garns-v9-6/dev-docs/W2-QueryPlanningDesign.md)
- Design SHA-256: `a7d6b1dc751568a917cd4592a422b5a0985042cda52433ec78e67b96f6a7dd18`
- Length: 450 lines
- Control manifest verified: `b57cb68cae2458623622311bbea640afb3f36dd342c56461cb94f61c36d0f085`
- 48-file source manifest verified at start and end: `b24732fba66b3b649927ef94fc9704abc82641572a90e9374f0bc4990ba981b5`

The draft specifies the immutable relational/result algebra, existing-expression reuse, canonical `FrozenPlanRoot`, validation and authority ordering, SQLite lowering, question-only footprints, exhaustive tests, proposed W2 files, and exact legacy integration/ownership gaps.

Sources read include workspace/product instructions, checkpoint, accepted parent plan and amendments, operator and governed-write records, W0/W1 acceptance, complete W1 manifest, A2, product layout, split-files guidance, the pinned source tuple, grammar, compiler IR/read resolution/types/function registry, storage, SQLite lowering, engine/live/footprint consumers, W1 contracts, and inherited tests/evidence inventory.

Limitations are explicit: design only; no self-acceptance, implementation launch, source/test/contract mutation, PostgreSQL/async/runtime claim, or legacy call-site wiring. The fixed nested-owner marker is called out for Consistency review; rejection would require a reviewed W1 contract amendment.

STOP WRITES for manager pinning and independent review.
