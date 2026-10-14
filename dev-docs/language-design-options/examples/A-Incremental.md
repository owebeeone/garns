# Candidate A Completed Existing Constructs

Choices: R1 C1 B1 T1 V1 M1 O1. Proposed notation throughout. This keeps carrier/query
organization familiar and extends the existing trait and compound mechanisms.

## Model and reuse

```text
module Bounds {
  intent lower: Integer
  intent upper: Integer
  trait Pair { use lower use upper invariant lower <= upper }
}
module Evidence {
  intent ID: Text
  resource Revision { use ID {key} }
}
module Catalog<type Content, intent Key, predicate Valid(Content), module E> {
  intent revision_number: Integer { invariant value > 0 }
  intent content: Content
  intent reference: Key.type
  intent role: Text
  resource Document { use Key {key} }
  resource Revision {
    use revision_number {key}
    use content
    link document -> Document { deletion restrict key }
    immutable
  }
  association RevisionEvidence {
    use role {key}
    link owner -> Revision {deletion restrict key}
    link target -> E::Revision {deletion restrict}
    immutable
  }
  resource Proposal {
    use reference {key}
    use content
    link document -> Document {deletion restrict key}
    link base -> Revision {deletion restrict optional}
    invariant base absent or base.document is document
    immutable
  }
  resource Decision {
    use disposition
    link proposal -> Proposal {deletion restrict key}
    link result -> Revision {deletion restrict optional}
    invariant result absent or result.document is proposal.document
    invariant (disposition = discarded) iff result absent
    immutable
  }
  resource Window {
    carry Bounds::Pair rename {lower => opening_lower, upper => opening_upper}
    carry Bounds::Pair rename {lower => closing_lower, upper => closing_upper}
  }
}
module Public = Catalog<DocumentValue, names::ID, ValidDocument, Evidence>
module Private = Catalog<DocumentValue, names::ID, ValidDocument, Evidence>
```

Companion mapping introduces carrier roles, not newly invented intent meanings.
The two catalog instances have different resource identities. Evidence::Revision
retains its original identity as an argument. The additional Catalog, ProposalEvidence
and SourceObservation contracts and provenance fields follow the shared domain table.
`immutable` is a proposed operation-admission rule, not implemented baseline syntax.

## Reads, writes and targets

```text
query history of Revision {
  given selected: Document
  where document is selected
  show revision_number, acceptance_fingerprint
  order revision_number
}
compound Accept(p: Proposal, expected: optional Revision) atomic {
  authority accept(p.document)
  require pending(p) and p.base is expected and current(p.document) is expected
  require Valid(p.content) and validated_exactly(p)
  step r = Revision.mint(from p, number=next_number(expected))
           when acceptance_identity(p) differs_from expected
  step pins = RevisionEvidence.mint(each p.evidence, owner=r) when r created
  step d = Decision.mint(proposal=p, result=r otherwise expected,
                        disposition=accepted if r created else equivalent)
  returns d
}
compound Discard(p: Proposal) atomic {
  authority discard(p.document)
  require pending(p)
  step d = Decision.mint(proposal=p, disposition=discarded, result=absent)
  returns d
}
world CatalogWorld { modules Public durability durable writers governed scope deployment }
build Api for CatalogWorld {language python style async}
deployment Local for CatalogWorld {backend sqlite at env CATALOG_DB}
deployment Server for CatalogWorld {backend postgres at env CATALOG_DB}
```

`from p`, exact validation and numbering abbreviate the fully enumerated shared
operation laws; a production design must define field mappings, not use reflective
copy-all. Module dependency closure must include Evidence and names in the world.

## Same cases through this candidate

| Cases | Expression and consequence |
| --- | --- |
| E1 | Inline deletion flags; key collection derives owner/role uniqueness. Unenforced remains standalone; required detach refuses. |
| E2/E3 | Intent predicate injected into every use; trait predicate rebound for each explicit role mapping. Zero/default and reversed bounds refuse. |
| E4/E5 | Explicit aliases to A::ID/B::ID; template substitution cannot capture local ID. Missing Evidence export fails at specialization. |
| E6 | DocumentValue lookup yields Missing or Present(Null/value). Patch Keep/Remove/Set is typed; byte observations separate. |
| E7 | Explicit conditional steps create complete revision/pins/decision. Guard protection and output delivery follow shared laws. |
| E8 | Reserve is a compound with guard, stock change and reservation mint steps; dependencies and transaction are explicit. |
| E9 | Separate build/deployment declarations keep semantic identity fixed. |

## Where it succeeds and strains

The non-Pyrocat operation uses the same mechanism:

```text
compound Reserve(s: Stock, expected: Integer, qty: PositiveQuantity) atomic {
  authority reserve(s)
  require s.version = expected and s.available >= qty
  step changed = Stock.change(s, available=s.available-qty, version=s.version+1)
  step r = Reservation.mint(stock=s, quantity=qty) after changed
  returns r
}
```

Lowest conceptual migration for current users; no need to redesign every carrier.
But repeated trait roles and effectful compounds still demand substantive IR changes.
Late template checking and step wiring cause more author burden than B. The design
does not automatically become more correct because it resembles current syntax.
Projected gates pass; runtime preservation, cross-object constraints and replay remain
unproved. A zero-invariant trait expansion is explicitly a failure, not permitted A behavior.
