# Candidate C Contract Driven Composition

Choices: R3 C3 B3 T2 V3 M3 O3. Proposed notation throughout. This tests whether one
contract-and-inclusion model can support reuse across values, relationships and workflows.

## Model and reuse

```text
predicate Positive(n: Integer) = n > 0
predicate Ordered(lo: Integer, hi: Integer) = lo <= hi
module Bounds exports BundleShape {
  intent lower: Integer
  intent upper: Integer
  rule ordered = Ordered(lower, upper)
}
format CatalogDocument version 1 {
  value DocumentValue
  projection subjects: sequence<Subject>
  canonicalization ExactDocumentV1
  preserves unknown_members
}
relation_contract Evidence<Owner, Target> {
  reference owner: Owner required target_deletion restrict
  reference target: Target required target_deletion restrict
  value evidence_role
  unique owner, evidence_role
}
module Versioned<type Content, intent Key, predicate Valid(Content), module E: EvidenceModel> {
  include E select {ID, Revision} as EvidenceSource
  intent revision_number: Integer requires Positive(value)
  resource Document {use Key {key}}
  resource Revision immutable {use revision_number; use content: Content; reference document: Document}
  unique Revision by document, revision_number
  association RevisionEvidence satisfies Evidence<Revision, EvidenceSource::Revision>
  resource Proposal immutable {use content: Content; reference document: Document; reference base: optional Revision}
  resource Decision immutable {reference proposal: Proposal; reference result: optional Revision; use disposition}
  unique Decision by proposal
  state Pending(p: Proposal) = no Decision for p
  state Decided(p: Proposal) = one Decision for p
  resource Window {expand Bounds as opening; expand Bounds as closing}
}
module Public = Versioned<CatalogDocument, names::ID, ValidCatalog, Observations>
module Private = Versioned<CatalogDocument, names::ID, ValidCatalog, Observations>
```

References use R3 named policies; where the specimen abbreviates policy, its complete
contract is the shared domain table's restrict/required-or-optional rule. This is not
permission to infer deletion from a type name. Inclusion retains E's declaration
identities. Shape and invariant obligations are part of contracts, not prose promises.

## Reads, transitions and targets

```text
query history of Revision {
  given selected: Document
  where document is selected
  show revision_number, acceptance_fingerprint
  order revision_number
}
transition Accept(p: Proposal) from Pending(p) to Decided(p) {
  input expected: optional Revision
  authority accept(p.document)
  guard p.base is expected and current(p.document) is expected and validated_exactly(p)
  case full_identity_equals_current(p) {
    establish Decision(p, equivalent, current(p.document))
  } otherwise {
    establish r: Revision from exact_candidate(p) with next_number(expected)
    establish RevisionEvidence from p.evidence with owner r
    establish Decision(p, accepted, r)
  }
  atomic
  returns Decision for p
}
transition Discard(p: Proposal) from Pending(p) to Decided(p) {
  authority discard(p.document)
  establish Decision(p, discarded, absent)
  atomic
  returns Decision for p
}
world CatalogWorld {
  model {modules Public durability durable writers governed scope deployment}
  generate {Api: python async}
  persist {Local: sqlite at env CATALOG_DB; Server: postgres at env CATALOG_DB}
}
```

States derive from decisions, avoiding divergent status fields. Transition outcomes
are explicit complementary cases, not a solver choosing accepted versus equivalent.
Format projections, if materialized, are immutable effects of the same acceptance.

## Same cases through this candidate

| Cases | Expression and consequence |
| --- | --- |
| E1 | Relationship contract states cardinality, deletion and uniqueness; an unenforced contract cannot satisfy required existence. |
| E2/E3 | Positive and Ordered predicates instantiate through contracts; selected bundle cannot drop its ordered rule. |
| E4/E5 | Selective inclusion retains qualified identities; conflicting refinements refuse regardless of include order. |
| E6 | Format contract preserves exact recursive value and provides declared projections; adapter escape is separately evidenced. |
| E7 | Pending-to-Decided transition gate protects all terminal outcomes under the shared laws. |
| E8 | Reserve transitions a stock version with enough availability to its successor, establishes reservation; state need not be an enum. |
| E9 | Uses T2 sections, not a compulsory new target profile mechanism. |

## Where it succeeds and strains

The non-Pyrocat operation uses the same mechanism:

```text
transition Reserve(s: Stock) from Version(expected) to Version(expected+1) {
  input expected: Integer, qty: PositiveQuantity
  authority reserve(s)
  guard s.available >= qty
  establish s.available = before(s.available)-qty
  establish s.version = expected+1
  establish r: Reservation(stock=s, quantity=qty)
  atomic
  returns r
}
```

Version is a derived state predicate, not a second stored status. Admission checks
that predicate as well as the explicit guard.

Repeated domain patterns become reusable contracts, and legality of change is visible.
The cost is many contract checks and overlapping notions of inclusion, satisfaction
and refinement. General predicate implication and transition exhaustiveness cannot
be delegated to an unspecified solver. This candidate remains viable with exact
obligation matching and explicit case partitions; flexibility beyond that is unknown.
