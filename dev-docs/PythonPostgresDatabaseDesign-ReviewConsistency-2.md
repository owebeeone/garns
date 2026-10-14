# Python PostgreSQL Database Design: Consistency Review 2

**Verdict: NO-GO**  
**Date:** 2026-10-11  
**Axis:** Consistency  
**Stage:** Design-stage dual gate; replacement reviewer, independent and read-only.

## Object and Evidence

Repository: member `garns` in workspace `garns-wz`.  
Exact revision: `f1adc67a4d9c9fbe6b1177e23f10f5eef186cb31`.

Reviewed committed objects:

- `dev-docs/PythonPostgresDatabaseDesign.md`, controlling DRAFT.
- `dev-docs/PythonPostgresApiWalkthrough.md`.

Additional revision evidence: `dev-docs/PythonPostgresDatabaseDesign-Vectors.json`.

Prior-round inputs: `dev-docs/PythonPostgresDatabaseDesign-ReviewConsistency-1.md` and `dev-docs/PythonPostgresDatabaseDesign-RemPlan-1.md`.

| Boundary Check | Start | End |
|---|---|---|
| `git rev-parse HEAD` | Requested revision | Same requested revision |
| Input manifest verification | All 18 entries OK | All 18 entries OK |

I read the manifest-listed working-tree authorities: the acceptance records, composed W2 documents, worker-exit manifest, listed ADRs and backend protocols. Historical Git versions were not substituted for these authorities. Acceptance precedence was applied only within the recorded accepted scopes.

Process instructions read: repository `AGENTS.md`, workspace `AGENTS_GWZ.md`, and the review-loop skill.

Current source inspection corroborated the distinction between public orchestration and existing backend protocols, the mutation fields, and inherited engine-owned stamps. Dirty implementation work was not treated as an accepted extension.

No files, services or Git state were changed. No tests, builds, database or network operations were performed. No current-round peer report or prompt was accessed. Vector digests were inspected, not independently recomputed under the restricted command allowance.

## Prior-Finding Closure

I replace the previous Consistency reviewer and independently retraced each original counterexample.

| Prior ID | Original Counterexample | Revised Evidence and Disposition |
|---|---|---|
| P2-1 | Independent readers invent different binding nesting, codec keys and storage digests. | **Closed for the original counterexample.** Design lines 175–245 define the required discriminator, closed nested vocabulary, codec identifiers, constraint associations, normalization and digest bytes. The minimal binding vector supplies authored and normalized objects. Independent placement of codecs is no longer permitted. |
| P2-2 | Repeating an explicit stamped insert after acknowledgement loss can hash newly generated stamps and falsely conflict. | **Closed for the original counterexample.** Lines 293–340 fix the entire batch before effects, define tagged intent encoding, exclude generated stamps/defaults and induced effects, and resolve duplicates before reevaluating them. The broader encoding attack identifies a separate bounded gap below. |
| P2-3 | Repeated sub-limit statements or caller idle time evade an unspecified whole-transaction deadline. | **Closed.** Lines 82–105 define `operation_seconds=120`, start before acquisition, include caller idle time and prohibit renewal. Supervised expiry prevents new effects; cleanup has a separate budget without manufacturing abort knowledge. The supplied t=119 commit trace expires at t=120, not t=149. |

These are design-level closures, not claims that backend execution or fault tests passed.

## Changed-Range Analysis

The revision changes a shared public interface, so replacement full review is appropriate.

| Changed Surface | Consistency Attack |
|---|---|
| Design lines 55–67; walkthrough write sequence | `begin(identity, mutations)` plus `apply()` replaces incremental public mutation. This can orchestrate the existing internal `begin`/`mutate` protocol without silently changing its signatures. |
| Design lines 82–105 | Retraced the original deadline sequence and checked expiry against independent transaction knowledge and retained ownership. |
| Design lines 114–245 | Checked version dispatch, authored names, closed codec vocabulary, normalized storage identity and exact-value activation prerequisites. |
| Design lines 293–346 | Retraced stamp-independent duplicate recovery; attacked nested codec canonicalization feeding payload identity. |
| Design lines 372–413 | Checked privileged migration recovery placement, request/attempt binding, fenced availability and separation from transaction rollback/reconciliation. |
| New vector file | Inspected binding, omission/NULL/JSON-null, typed-value and mutation-order examples. JSON-null does not exercise JSON string escaping. |

## Findings

### P2-4: JSON Canonical Bytes Are Not Uniquely Defined Before Payload Hashing

**Classification:** New bounded codec-specification root. This does not require a new ownership model or architectural redesign.

**Location:** `dev-docs/PythonPostgresDatabaseDesign.md:150–154`, `:306–320`; vector file entries `payload-json-null` and `payload-exact-values`.

**Violated invariant:** A versioned codec whose output bytes participate in durable transaction identity must select exactly one byte representation for each admitted semantic JSON value. A4 requires repeated identity and payload to recover the original revision, not conflict because equivalent JSON was encoded differently.

**Evidence:** Section 4 fixes key order, numeric spelling and UTF-8 output, but specifies strings only through “standard JSON quote/control escapes.” It does not select between the standard short escape `\b` and the equivalent Unicode escape `\u0008`, or explicitly settle optional solidus escaping.

Section 6 then canonicalizes JSON documents through this codec and wraps the resulting bytes in a base64 atom. Its precisely specified outer ASCII JSON encoder cannot normalize differences already hidden inside that atom.

The existing JSON-null vector contains no string and therefore cannot resolve this ambiguity.

**Reproduction:**

1. Use `json-document-v1` for an Opaque field and supply a JSON string containing the backspace character.
2. Codec A emits the four bytes `22 5c 62 22`: JSON text `"\b"`.
3. Codec B emits the eight bytes `22 5c 75 30 30 30 38 22`: JSON text `"\u0008"`.
4. Both outputs preserve the same JSON value, are valid UTF-8 and use standard JSON control escapes. Both fit the stated bounds.
5. Their payload atoms are respectively `["bytes","IlxiIg=="]` and `["bytes","Ilx1MDAwOCI="]`.
6. Commit identity T through A, lose acknowledgement, then repeat T with the same caller JSON through B. The normalized payload bytes differ, so the draft's exact comparison refuses it as different intent.

No callback retry, database experiment or deferred implementation assumption is needed to demonstrate the two permitted encodings.

**Impact:** Processes claiming the same codec and payload versions can disagree on durable intent identity and detached JSON bytes. A legitimate duplicate can be refused after restart or an encoder replacement. This is a concrete interoperability/recovery defect, not demonstrated active corruption.

**Required correction:** Define the complete `json-document-v1` byte serializer: exact control-character escapes, hexadecimal case, optional escaping policy, compact separators, and trailing-newline policy. Specify that the same serializer governs input normalization and JSONB retrieval. Preserve the already stated exact-decimal and resource rules.

**Closure/regression:** Add byte-level vectors for backspace, form feed, newline, tab, quote, backslash, solidus, another control character, non-ASCII and non-BMP text. Include differently escaped inputs yielding identical canonical bytes and a nested object/array case. Record the resulting base64 atoms and payload bytes/digests. Retrace identity T across two independent encoders and require original-outcome recovery.

## Invariant Analysis

| Area | Result |
|---|---|
| Accepted W1/W2 composition | Base-plus-overlay precedence is preserved; no new false composition established. |
| Worker-exit acceptance | Reference-model acceptance is not promoted into production async, worker or database proof. |
| Public/backend API mapping | Fixed-batch public orchestration need not replace accepted internal mutation signatures. No driver-object escape is introduced. |
| Storage/version identity | Original binding-shape ambiguity is corrected. Codec-derived payload bytes remain inconsistent under P2-4. |
| Durable transactions | Atomic data, ledger, identity and revision coupling remains required. Generated stamps no longer affect caller-intent comparison. |
| Exact decimals | The additive artifact/result amendment remains an explicit activation prerequisite; legacy SQLite REAL is not claimed exact. |
| Lifetime and deadlines | Whole-operation ownership, nonrenewing transaction budget and independent cleanup/knowledge obligations remain coherent. |
| Migration recovery | Privileged recovery is available while ordinary admission is fenced; it neither repeats SQL nor accepts caller proof digests. |
| Activation and retirement | Operator-owned physical fencing remains required; the pending retirement edge is explicitly refused. |
| Generic design completion | Substantially improved, but the versioned JSON-to-payload interface still admits incompatible bytes. |
| Deferred scope | No finding demands Rust, external capture, Pyrocat or live backend implementation evidence. |

## Verdict and Cap

**NO-GO:** P2-4 remains open. The three original Consistency counterexamples are closed at design level.

The remediation plan records correction 1 of 2. This review finds no new architectural root; P2-4 is a bounded textual codec correction with golden-vector closure. It does not trigger the architectural STOP condition or reset the remediation cap.

I pre-commit to GO on a revision that resolves **P2-4** as specified, provided the reviewed tuple and pinned authorities remain stable and the correction introduces no conflicting contract change.
