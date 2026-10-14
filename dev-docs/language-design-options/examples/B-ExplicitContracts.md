# Candidate B Explicit Semantic Contracts

Choices: R1 C2 B2 T2 V2 M2 O2. Proposed notation throughout. Prefer explicit semantic
identities and finite derivation over implicit overrides or a general solver.

## Model and reuse

```text
type PositiveRevision = Integer where self > 0
value Subject {
  name: Text required
  note: nullable Text optional
  extras: open DocumentValue
}
bundle Bounds {
  component lower: Integer
  component upper: Integer
  invariant lower <= upper
}
signature EvidenceModel {intent ID; resource Revision}
module Versioned<type Content, intent Key, predicate Valid(Content), module E: EvidenceModel> {
  intent revision_number: PositiveRevision
  intent content: Content
  resource Document {use Key {key}}
  resource Revision immutable {
    use revision_number {key}
    use content
    link document -> Document {deletion restrict key}
  }
  association RevisionEvidence immutable {
    use evidence_role {key}
    link owner -> Revision {deletion restrict key}
    link target -> E::Revision {deletion restrict}
  }
  resource Proposal immutable {
    use proposal_reference {key}
    use content
    link document -> Document {deletion restrict key}
    link base -> Revision {deletion restrict optional}
    invariant base absent or base.document is document
  }
  resource Decision immutable {
    use disposition
    link proposal -> Proposal {deletion restrict key}
    link result -> Revision {deletion restrict optional}
    invariant result absent or result.document is proposal.document
    invariant (disposition = discarded) iff result absent
  }
  resource Window {use Bounds as opening; use Bounds as closing}
}
module Public = Versioned<map<Text, Subject>, names::ID, ValidSubjects, Observations>
module Private = Versioned<map<Text, Subject>, names::ID, ValidSubjects, Observations>
```

Structural Subject values are nested values. Bounds expands flat carrier members;
the two mechanisms are explicitly different. Key passes its intent identity and
constraints, not only Text. Required EvidenceModel members are checked before
specialization; extra exports remain unselected. Full provenance and remaining
carrier declarations are as specified in the shared domain contract.

## Reads, writes and targets

```text
query history of Revision {
  given selected: Document
  where document is selected
  show revision_number, acceptance_fingerprint
  order revision_number
}
operation Accept(p: Proposal, expected: optional Revision) {
  authority accept(p.document)
  require pending(p) and p.base is expected and current(p.document) is expected
  require Valid(p.content) and validated_exactly(p)
  effects atomic {
    case acceptance_identity(p) equals identity_of(expected) {
      create d: Decision(proposal=p, disposition=equivalent, result=expected)
    } otherwise {
      create r: Revision(document=p.document, number=next_number(expected), content=p.content, ...)
      create pins: RevisionEvidence for each pin in p.evidence {owner=r, target=pin.target, ...}
      create d: Decision(proposal=p, disposition=accepted, result=r)
    }
  }
  returns d
}
operation Discard(p: Proposal) {
  authority discard(p.document)
  require pending(p)
  effects atomic {create d: Decision(proposal=p, disposition=discarded, result=absent)}
  returns d
}
world CatalogWorld {
  model {modules Public durability durable writers governed scope deployment}
  generate {Api: python async}
  persist {Local: sqlite at env CATALOG_DB; Server: postgres at env CATALOG_DB}
}
```

The two cases are exclusive by an explicit value comparison; absent expected never
matches an acceptance identity. Ellipses denote the fields in the shared operation
laws, not inferred unrestricted copying. Data references derive ordering; lexical
effect order carries no hidden meaning. A conflicting assignment fails validation.

## Same cases through this candidate

| Cases | Expression and consequence |
| --- | --- |
| E1 | Local deletion semantics with explicit constraint explanation; standalone unenforced never implies cascade. |
| E2/E3 | PositiveRevision constructor rejects zero; bundle origin/instance qualifies opening::lower and closing::lower with both predicates. |
| E4/E5 | Signatures plus namespace aliases avoid ID collision; explicit instantiation distinguishes model identity from reusable supplied intent identity. |
| E6 | Optional nullable note has three states; Remove is distinct from Set(Null). Open extras are preserved and protected by operation authority. |
| E7 | Finite effects derive revision/pin/decision dependencies; shared laws constrain concurrency, replay and evidence. |
| E8 | Reserve declares stock.available -= quantity, stock.version += 1 and create reservation under expected-version guard; overlapping updates refuse. |
| E9 | World sections expose alternatives without changing the semantic-world digest. |

## Where it succeeds and strains

The non-Pyrocat operation uses the same mechanism:

```text
operation Reserve(s: Stock, expected: Integer, qty: PositiveQuantity) {
  authority reserve(s)
  require s.version = expected and s.available >= qty
  effects atomic {
    change s {available = before(s.available)-qty, version = before(s.version)+1}
    create r: Reservation(stock=s, quantity=qty)
  }
  returns r
}
```

`before` refers to the protected operation snapshot; it never depends on effect order.

The common cases have clear static bindings and inspectable effect dependencies.
Its principal costs are three new semantic mechanisms: refinement closure, module
signatures and effect planning. They can share predicate/type IR rather than separate
interpreters. Scope must resist growing into general theorem proving or graph solving.
Projected gates pass; implementation complexity and diagnostics remain unmeasured.
