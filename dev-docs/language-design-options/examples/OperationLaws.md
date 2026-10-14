# Shared Operation Laws

These laws constrain all four candidates. They expose the work abbreviated by
names such as validated_exactly or acceptance_identity in source specimens.
They are domain requirements, not current GARNS builtins.

## Pure values and observed state

- Candidate content is a finite exact document value under a versioned format.
- Content fingerprint covers canonical content; acceptance fingerprint covers
  content, format, normalization and validation identities and sorted evidence
  roles with exact target revisions and acceptance fingerprints.
- A validation result names that entire candidate/manifest, validator identity and
  findings. It cannot be reused for a different candidate or dependency set.
- Current(document) is the highest accepted revision for that document, or absent.
  Pending(proposal) means no terminal Decision exists for that proposal.
- Authority is supplied through GARNS's trusted context. A caller-supplied actor
  string is provenance input to validate, not proof of permission.

## Propose

Require proposal authority on the document, an admitted change policy, an exact
expected base (or explicit absence), valid candidate shape and admitted evidence
roles. Preserve protected evidence and unknown fields unless an authorized format
operation expressly permits their replacement. Record an immutable proposal and
its pins atomically. Editing it creates another proposal; validation changes no
accepted state. Whether a stale-base proposal may be stored for research is a
separate policy; these specimens require its base current at submission.

## Accept

Require acceptance authority, a pending proposal, its exact base still current,
and successful validation of the exact candidate and pinned evidence. Validate
target existence, acceptance identity and role compatibility within the protected
operation read set. Do not silently refresh pins to newer target revisions.

There are two disjoint outcomes:

1. No current revision, or full acceptance identity differs: create the next revision
   (1 for first acceptance), all revision evidence, and one accepted Decision.
2. Full identity equals current: create an equivalent Decision pointing to current;
   do not create a redundant revision. Unchanged content alone is insufficient.

All guards, identity allocation, immutable facts and terminal disposition belong
to one atomic operation. A unique next number is not enough: protect the expected
current state and absence of a Decision against concurrent changes. In a relational
adapter that may require locking or serializable execution; the language declares
the guarantee, not the mechanism. An adapter unable to enforce it refuses admission.

## Discard and observe

Discard requires its authority, pending status and exact proposal identity; it
records one discarded Decision with no result. Accept and discard cannot both win.
Observation appends original bytes and provenance only after correspondence to the
selected revision is established under its format contract. Different formatting
does not silently create different accepted meaning.

## Failure and delivery

Every effectful call carries stable retry identity plus full intended meaning.
Same identity/same intent recovers the recorded outcome; changed intent refuses.
Known aborted attempts may retry only under accepted GARNS rules. Unknown completion
after commit request requires authoritative reconciliation, never assumed rollback.
Return values become successful only once the accepted contract establishes success;
generated API convenience cannot manufacture certainty.

New effect batches propose final-state validation inside a private atomic boundary.
Changing current per-mutation invariant timing needs an explicit runtime amendment.
Authorization is checked at accepted runtime boundaries, including before effects
and commit; every admitted route enforces immutable data and allowed operations.

## Non-Pyrocat case

Reserve(stock, expected_version, quantity): require reservation authority, positive
quantity, matching version and sufficient availability. Atomically decrement
availability, advance version and create a reservation; return its reference.
Two requests cannot oversell the same stock. All four operation models must express
this without built-in knowledge of catalogs, revisions or proposals.

## Counterexample walkthroughs

| Case | Required refusal or outcome |
| --- | --- |
| Two accepts start from revision 7 | One advances to 8; the other fails its protected expected-state guard |
| Accept races discard | One terminal Decision; losing operation conflicts without partial revision |
| Same content, changed evidence pin | New acceptance identity and revision, not false equivalence |
| Validated proposal replaced with another | Exact candidate identity mismatch before effects |
| Input omits a protected field | Preserve it; omission does not authorize deletion |
| Caller writes actor=administrator | No authority gained |
| Connection fails after commit request | Outcome unknown until reconciled; no invented successful retry |
| Referenced document changes incompatibly | Affected invariant validation or immutable-target rule prevents invalid accepted state |

These are reasoned requirements. No candidate currently has a passing execution
harness for them. The accepted authority/retry contracts are baseline obligations,
not proof of these proposed operation surfaces.
