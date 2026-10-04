COMPLETE — revised W1 remediation draft is ready for fresh Code/State review.

Revised tuple aggregate:

`3dd854040ffbf58ad8992f57b755a3f8ebb790643ef8bf20e74ce4f7690a1eb6`

The inventory now contains 26 files: 16 ADR documents, 8 contract modules, and 2 contract-test files. Contract source was split into cohesive authority, semantic, operation, value, protocol, and state modules.

Finding closure candidates:

- Code P2-1: added required async governed mutation, schema inspection, migration lock/application, generation outcome, ledger replay and publication operations. Both backend descriptions retain the same surface and capability-refuse before fake adapter invocation.
- Code P2-2: added lossless `SemanticType` mapping for all inherited `TypeRef` dimensions and named ownership for nested result shapes.
- Code P2-3: replaced mutable arbitrary roots with immutable opaque canonical bytes plus format/digest. Plans carry world, IR digest, storage digest and generation; mismatches refuse before execution.
- Code P2-4 / State P2-5: authority now flows through ordinary open, acquire/release, execute, snapshot, transactions, mutations, migrations, ledger reads and subscription delivery. Privileged binding open is separately named.
- Code P2-5 / State P2-3: `ContextIssuer` validates the exact live registered instance. Copy, deepcopy, reconstruction, pickle, dataclass conversion, field replacement and deletion cannot mint or preserve authority.
- Code P2-6 / State P2-1: cancellation uses a closed phase/evidence grammar. Only not-started, confirmed rollback or authoritative abort evidence yields `KNOWN_ABORTED`; lost/failed/timed-out rollback remains indeterminate.
- State P2-2: publication records qualified identity and payload digest. Same identity/payload returns the original revision; conflicting payload refuses; identity results survive generation and compaction transitions.
- State P2-4: claims defensively normalize capabilities, scope, identities, validity and epoch without retaining mutable caller containers or hostile scalar subclasses.
- State P2-6: parameters, snapshots, deliveries, mutation values and ledger values use a recursively detached immutable algebra. Unsupported custom mutable values refuse.
- State P2-7: SQLite lifecycle now has an executable commit fence. Late commit requests after shutdown refuse; already-requested commits remain reconcilable. Nonquiescent close returns typed `UNRESOLVED` and retains containment instead of claiming a thread was killed.

Verification used this loop for CPython 3.11.14, 3.12.12, 3.13.12 and 3.14.3:

```sh
PYTHONWARNINGS=ignore::ResourceWarning \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="${LARK_ROOT}:src" \
"$py" -B -m unittest discover -s tests/contracts -t .

PYTHONWARNINGS=ignore::ResourceWarning \
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH="${LARK_ROOT}:src" \
"$py" -B -m unittest discover -s tests -t .
```

Every interpreter passed:

- Focused contracts: 26/26.
- Full discovery: 129/129, comprising 26 W1 tests and 103 inherited tests.

Additional checks:

- All five `tools/check_product.py` checks passed.
- All five inherited evidence-manifest entries verified.
- No `__pycache__` directories were created.
- Grammar SHA-256 remains `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`.

Limitations remain unchanged: these are pure contracts, reference models and conforming fakes—not database, thread-responsiveness, PostgreSQL, migration-atomicity or real fault-cut proof. All ADRs remain **PROPOSED FOR REVIEW**. This builder assessment does not close findings or authorize W2; the next gate is fresh peer-blind Code/State review on the exact revised tuple.
