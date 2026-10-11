# Python PostgreSQL Database Design: Consistency Review 1

**Verdict: NO-GO**  
**Date:** 2026-10-11  
**Axis:** Consistency  
**Stage:** Design-stage dual gate; independent, read-only review.

## Object and Evidence

Repository: member `garns` in workspace `garns-wz`  
Exact revision: `b2b8b158b76f0fe6e07eb5f009d6397bb653689b`

Reviewed committed objects:

- `dev-docs/PythonPostgresDatabaseDesign.md`
- `dev-docs/PythonPostgresApiWalkthrough.md`

The database design is the controlling draft. Locations below refer to these documents at the exact revision above.

Boundary verification:

| Check | Start | End |
|---|---|---|
| `git rev-parse HEAD` | Exact requested revision | Same revision |
| `shasum -a 256 -c dev-docs/PythonPostgresDatabaseDesign-Inputs.sha256` | All 18 entries OK | All 18 entries OK |

I read every listed input as working-tree authority, including the acceptance records, composed W2 design, worker-exit manifest, listed ADRs and backend protocols. Additional source inspection covered manifest-listed storage and mutation/value contracts. Historical Git content was not substituted for pinned working-tree authorities.

Process instructions read: repository `AGENTS.md`, workspace `AGENTS_GWZ.md`, and the review-loop skill.

No files were modified. No tests, builds, database operations or network operations were performed. No current-round peer report or prompt was accessed. The reported 293-test baseline was not independently rerun.

## Findings

### P2-1: Binding-v2 introduces a version without defining its interoperable document shape

**Classification:** Architectural interface-definition root.

**Location:** Database design lines 99–106, 128–137 and 176–181; walkthrough lines 11–12.

**Violated invariant:** An explicitly versioned, authored storage interface must define which documents are valid and how they acquire stable storage identity. Unknown-key rejection requires a closed key vocabulary.

**Evidence:** The design introduces `garns.storage/2`, per-column codecs, constraint names, indexes and configurable codec bounds, but provides no closed document schema. It does not specify the version discriminator, nesting, required fields, scalar codec identifiers, constraint-to-semantic-key association, or canonical storage-digest encoding.

The legacy reader cannot supply these definitions: `src/garns/storage.py:140–147` checks a `schema` discriminator, and its `engine` object names ledger/generation/revision tables at lines 180–187. It has no version-2 codec/index representation.

**Reproduction:** Give independent compiler and backend implementers the proposed binding for one Integer column and one `json-document-v1` column. One places codec metadata inside each column mapping; another uses a separate codec map. Both satisfy the prose. Each rejects the other's keys, despite advertising the same binding version. They can also produce different storage digests from the same intended mapping.

**Impact:** The first preparation/provisioning workflow cannot be authored unambiguously. Compiler, provisioner and runtime compatibility depends on new interface decisions made during implementation, contradicting the stated completion of the generic database-definition design.

**Required correction:** Define a closed binding-v2 schema, including version dispatch and legacy behavior, exact codec names, name/constraint/index associations, bound overrides and defaults, and canonical digest rules. Include a complete minimal authored example.

**Closure/regression:** Supply accepted binding bytes and their expected normalized representation/storage digest. Add design vectors for missing/unknown fields, unsupported codecs, name collisions, constraint association, bounds overrides and version dispatch. Independently derived readers must agree on acceptance and digest.

### P2-2: Payload canonicalization is deferred only for callbacks, although explicit transactions already require it

**Classification:** Architectural durable-identity contract root.

**Location:** Database design lines 198–211; walkthrough lines 45–51.

**Violated invariant:** A4's same-identity/same-payload rule requires a stable definition of payload identity for every governed transaction, not merely transactions with automatic retries.

**Evidence:** Lines 198–203 promise original-outcome replay and conflicting-payload refusal. Lines 205–211 correctly distinguish planned mutations from actual effects, but defer their canonical encoding until callback retries and explicitly state that default one-attempt transactions are unaffected.

The current mutation contract supplies kind, carrier, identity and frozen values; the publication contract carries a payload-digest string. Those structures do not define transaction-payload bytes or whether generated stamps and induced effects participate in that digest.

**Reproduction:** Commit an explicit transaction with identity `T` and an insert whose stamp is generated during execution. After losing the acknowledgement, repeat `T` with the same caller-supplied mutation. An implementation hashing effective stamped values computes a different payload; one hashing the authored mutation computes the same payload. The draft supplies no default-path rule selecting the latter or another precise representation.

This sequence uses no callback and no automatic retry.

**Impact:** The initial usable slice cannot consistently deliver its promised duplicate-identity behavior across restart or implementations. It may reject a legitimate duplicate as a conflict. No active corruption is demonstrated, so this is P2 rather than P0.

**Required correction:** Define or explicitly gate a versioned payload encoding for the initial explicit-transaction path. Specify mutation ordering, omission versus NULL, typed values, generated defaults/stamps, induced effects, and the encoding version retained with durable identity records. Callback retries may remain deferred.

**Closure/regression:** Provide exact payload bytes/digests for representative explicit transactions. The same identity and caller payload must recover the original revision despite newly evaluated stamps; changed payload and semantically significant mutation ordering must refuse. Include restart and encoding-version compatibility vectors.

### P2-3: The promised total operation deadline has no default or lifetime definition

**Classification:** Bounded configuration-contract root.

**Location:** Database design lines 81–89; walkthrough lines 22–25 and 34–39.

**Violated invariant:** The declared finite whole-operation bound must be materialized from a defined configuration value and measured over a defined lifetime. Finite per-phase limits do not establish a finite transaction-wide deadline.

**Evidence:** All six phase timeouts have defaults. The additional “operation absolute monotonic deadline” has no duration default, configuration field, derivation rule or start point. None of the proposed operation signatures supplies it.

**Reproduction:** Open a runtime using the documented defaults, begin a transaction, then execute ten mutations taking twenty seconds each. Every mutation satisfies the thirty-second statement limit. A backend that resets phase deadlines permits the entire sequence; another imposing an invented thirty-second transaction budget refuses it. For a transaction spanning separate `begin`, `mutate` and `commit` calls, the draft does not determine which behavior is correct.

**Impact:** The same default API invocation has incompatible timeout behavior, and implementations cannot verify the claimed total bound without inventing interface semantics.

**Required correction:** Specify the total budget's configuration key, finite default or deterministic derivation, start point, propagation across explicit transaction calls and retries, and expiry outcome. State how caller idle time and separate cleanup budgets interact with it.

**Closure/regression:** Provide a deterministic timeline using defaults that identifies the exact expiry point across acquire, multiple mutations and commit. Verify that repeated sub-limit statements and retry attempts cannot reset the total deadline, while cleanup retains its separate bounded budget.

## Invariant Analysis

| Area attacked | Result |
|---|---|
| Accepted W1/W2 composition | The draft explicitly preserves the base-plus-overlay composition and acceptance precedence. No new false-composition finding established. |
| Worker-exit scope | Reference-model acceptance is not represented as production worker, async or database proof. |
| Admission and lifetime | Whole-operation ownership, contained uncertainty and local-close versus deployment-drain distinctions are preserved by reference. |
| Activation and retirement | Operator-owned physical fencing is retained; the pending `CURRENT × NONE → RETIRED` operation is explicitly refused. |
| Durable publication | Atomic data/ledger/identity/revision coupling and missing-row nonfinality are preserved. Payload identity remains incomplete under P2-2. |
| Storage/version interoperability | Binding-v2's essential document and digest shape remains undefined under P2-1. |
| Exact decimals | The amendment-before-activation gate avoids claiming legacy REAL parity or silently changing W2 plan format. No implementation outcome was required here. |
| JSON semantics | SQL NULL versus JSON null, exact numeric parsing and resource bounds are stated. This does not close the binding-format gap. |
| Defaults and execution handoff | Phase defaults exist, but the additional total budget is undefined under P2-3. |
| Migration accounting | A12 classification, pre-effect refusal and deployment-wide draining remain requirements; no database proof is claimed. |
| Generic design completion | Not achieved: essential binding, payload-identity and deadline contracts remain decisions for later implementers. |

No finding is based on deferred Rust, external capture, Pyrocat schema or live backend implementation outcomes. The findings concern interface shape and consistency of the proposed initial slice.

## Verdict

**NO-GO.** P2-1, P2-2 and P2-3 remain open.

P2-1 and P2-2 are architectural interface-definition roots; P2-3 is bounded. Their correction can remain in design documents without authorizing implementation or altering accepted historical contracts, but requires a new exact review tuple and focused verification of the specified closure vectors.
