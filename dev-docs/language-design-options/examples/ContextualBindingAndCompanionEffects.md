# Contextual Binding and Companion Effects Comparison

Status: proposed Garns notation and design procedures, 15 October 2026. These specimens are not accepted by the current parser and have not been executed. They compare the same intended semantics under different divisions of author and engine responsibility. No measured correctness or evaluator score is claimed.

References: [vision](../../GarnsVision.md), [reassessment](../../LanguageDesignVisionReassessment.md), [common domain](README.md), and [operation laws](OperationLaws.md).

## What changes between the specimens

| Specimen | Module connections | Mutation connections |
| --- | --- | --- |
| A | Author binds each evidence port | Author enumerates all atomic effects |
| B | Engine binds evidence ports under a selected world rule | Same authored effects as A |
| B-role | Engine selects providers by semantic role, domain and declared context | Same authored effects as A and B |
| C | Same contextual binding as B | Engine expands declared companion-effect rules |

A to B isolates module binding. B to C isolates effect derivation. All three preserve the same authority, identity, atomicity, evidence and retry obligations. The examples first compare module assembly, then use stock reservation to show complete effect rules without hiding the expansion behind a domain helper. A final acceptance example applies the same mechanism to the existing Pyrocat domain.

B-role is an additional binding-only comparison. B distributes an explicitly chosen provider across matching ports; B-role derives the provider choice as well. C's effect mechanism can be combined with either binding variant independently.

The keywords `binding_rule`, `effect_contract` and `establish` are illustrative. Their specified procedures matter more than these spellings.

## Part one Contextual module binding

### Shared requirement and provider declarations

The existing common domain supplies Revision and its exact acceptance fingerprint. This signature exposes the relevant identity and value roles; it does not create new carrier identities.

```text
signature EvidenceModel {
  export resource Revision immutable
  export member Revision.acceptance_fingerprint: AcceptanceFingerprint
}

module Versioned<type Content, intent Key, predicate Valid(Content)> {
  input module Evidence: EvidenceModel
  # ProposalEvidence.target and RevisionEvidence.target refer to Evidence::Revision.
  # All other carriers and laws are the common domain contract.
}

module CatalogRecords = Versioned<CatalogValue, names::ID, ValidCatalog>
module ResearchRecords = Versioned<ResearchValue, names::ID, ValidResearch>
```

Content, key intent and validator remain supplied explicitly in every specimen. This comparison removes only the repeated evidence-port bindings. Distinct named instances create distinct local carrier identities; their shared key argument retains its supplied intent identity.

Observations and ReviewedObservations below are existing module instances satisfying EvidenceModel, with different qualified Revision identities. They are not interchangeable merely because both satisfy the signature. Their implementation and data are unchanged between specimens.

### A Author binds every connection

```text
world CatalogWorld {
  modules CatalogRecords, ResearchRecords, Observations
  bind CatalogRecords.Evidence = Observations
  bind ResearchRecords.Evidence = Observations
}
```

The author declares two individual connections and the admitted world membership. The engine checks signature compatibility and closure, resolves the two Revision target identities and derives compilation order. Adding a third Versioned instance requires another binding even though the same evidence-source policy applies.

### B Author selects a rule and its context

```text
binding_rule WorldEvidence {
  context evidence_source: module EvidenceModel
  for each input module port requiring EvidenceModel in this world {
    bind port to context.evidence_source
  }
}

world CatalogWorld {
  modules CatalogRecords, ResearchRecords, Observations
  context evidence_source = Observations
  apply WorldEvidence
}
```

The author declares the policy once, chooses the world's evidence authority once and activates the policy in a bounded scope. The engine discovers applicable ports and produces the same two connections as A. A third instance admitted to this world is covered by the same rule without a new per-port binding.

This is rule-based distribution of an explicit provider choice. The context names the intended provider; the engine derives which requirement sites it satisfies. It removes repeated bindings but does not derive the provider from its semantic role. Moreover, matching EvidenceModel alone establishes structural compatibility, not that every compatible port intends the same evidence authority. B is suitable only where that uniform policy is actually intended. The B-role variant below addresses the missing semantic distinction.

For another world, the author can select ReviewedObservations as its evidence source while instantiating fresh local consumers. That uses the same module definitions and binding rule with a different declared context. It is not a physical remapping of the same persistent consumers: changing their evidence provider changes a semantic reference target.

### Proposed resolution procedure

1. Fix the named module instances, world membership, selected rules and context. No directory scanning, file-order precedence or runtime discovery participates.
2. Enumerate the finite set of module input ports in those instances. Ordinary imports are not eligible ports. Private dependency closure remains present but cannot introduce undeclared world members.
3. Match each port by required signature identity and declared kind, not by its spelling. Check the selected provider against that signature, including required obligations.
4. Collect binding proposals from explicit bindings and applicable rules. Identical proposals to the same qualified provider identity coalesce. Distinct targets for one port refuse; explicit syntax does not silently override a rule.
5. Refuse unbound required ports, inadmissible providers and dependency cycles outside the admitted assembly model. Preserve consumer-instance identity and supplied-provider identity separately.
6. Produce the resolved binding graph with rule/context provenance and include its semantic dependencies in evolution comparison.

An intentional exception requires narrowing the rule's scope or declaring a separately governed context. It cannot depend on declaration order.

### Expected resolved explanation for A and B

```text
CatalogRecords.Evidence -> Observations
  target carrier: Observations::Revision
ResearchRecords.Evidence -> Observations
  target carrier: Observations::Revision

A origin: two explicit world bindings
B origin: WorldEvidence + CatalogWorld.evidence_source
Consumer identities remain distinct in both cases.
```

This is the expected explanation, not captured compiler output.

### Module boundary cases

| Case | A | B |
| --- | --- | --- |
| Add a third eligible consumer | Add an individual binding | Rule derives its binding; resolved graph reports the addition |
| Two compatible provider modules are admitted | Each explicit binding chooses a provider | Context chooses one; mere availability does not select either |
| Context source is absent | Not applicable; explicit port bindings remain required | Refuse the required context; do not select the only available module implicitly |
| Context names incompatible provider | Signature failure at binding validation | Same signature failure, traced through context and rule |
| Two rules choose different providers for one port | Conflicting explicit bindings refuse if present | Refuse conflict; no priority or last-rule winner |
| Reorder declarations | Same graph | Same graph |
| Change source after data exists | Semantic reference change requires evolution review | Same obligation, with all rule-derived consumers identified |
| Providers have same exported names | Qualified identities remain different | Same; signature matching does not merge identities |

### B-role Meaning and context determine provider choice

An evidence role identifies the purpose of a dependency, not a concrete provider. A domain identifies the governed body of evidence. Review status distinguishes the evidence contract required by this use. These are explicit semantic facts; a provider's name or physical database cannot establish them.

The following alternative declarations describe the same consumer instances as A and B, rather than additional simultaneous instances. For comparison, A and B's intended provider is assumed to meet these same requirements; spelling out requirements here does not authorize different acceptance guarantees.

```text
role ResearchEvidence
role ArchiveEvidence
domain CatalogEvidence
domain OtherEvidence
enum ReviewStatus { raw, reviewed }

module Versioned<type Content, intent Key, predicate Valid(Content)> {
  input module Evidence: EvidenceModel {
    requires role ResearchEvidence
    requires domain context.evidence_domain
    requires review context.required_review
  }
  # Same carriers, references and operation laws as the shared model.
}

provider Observations {
  module Observations
  offers EvidenceModel
  role ResearchEvidence
  domain CatalogEvidence
  review reviewed
}
provider RawObservations {
  module RawObservations
  offers EvidenceModel
  role ResearchEvidence
  domain CatalogEvidence
  review raw
}
provider Archive {
  module Archive
  offers EvidenceModel
  role ArchiveEvidence
  domain CatalogEvidence
  review reviewed
}
provider OtherObservations {
  module OtherObservations
  offers EvidenceModel
  role ResearchEvidence
  domain OtherEvidence
  review reviewed
}

binding_rule EvidenceByMeaning {
  for each EvidenceModel input port with declared semantic requirements {
    candidates = admitted providers in this world satisfying
                 the port's signature, role, domain and review requirements
    bind port to the unique candidate
    otherwise report missing or ambiguous provider
  }
}

world CatalogWorld {
  modules CatalogRecords, ResearchRecords,
          Observations, RawObservations, Archive, OtherObservations
  context evidence_domain = CatalogEvidence
  context required_review = reviewed
  apply EvidenceByMeaning
}
```

Provider declarations associate existing module instances with checked export contracts and admitted semantic claims; they do not create fresh copies. CatalogRecords and ResearchRecords retain the shared explicit Content, Key and Valid arguments. In this variant their evidence requirements capture their owning world's context when resolved. A module reused under another world context is resolved as that world's declared instance, not rebound dynamically during a call.

The author has not named Observations as either port's target or as the world's selected source. Observations is the only admitted provider satisfying all four requirements. RawObservations fails review, Archive fails role and OtherObservations fails domain, even though all export a compatible Revision shape. The engine derives both target bindings from those facts.

Role names and domains are qualified identities, not text labels compared by similarity. Domain equality is exact; a broader-scope provider does not qualify automatically. Review matching here is exact enum equality, not inferred trust ranking. Signature satisfaction uses the existing checked obligations. These restrictions make the selection procedure finite and reproducible without general semantic inference.

Declaring `review reviewed` cannot prove that a source was actually reviewed. Admission must establish which trusted configuration may assert that claim and what evidence its contract requires. Provider metadata does not grant caller authority, authenticate identities or replace exact revision-pin validation.

### Expected role-based explanation

```text
Requirement: CatalogRecords.Evidence
  signature EvidenceModel
  role ResearchEvidence
  domain CatalogEvidence from CatalogWorld.evidence_domain
  review reviewed from CatalogWorld.required_review
Candidates:
  Observations       qualifies
  RawObservations    rejected: review raw does not match reviewed
  Archive            rejected: role ArchiveEvidence does not match ResearchEvidence
  OtherObservations  rejected: domain OtherEvidence does not match CatalogEvidence
Result: CatalogRecords.Evidence -> Observations
ResearchRecords.Evidence resolves by the same rule and context.
```

This is an expected derivation trace, not an observed compiler run. The intended concrete graph is the same as A and B; the source information from which it is derived differs.

### When more than one provider qualifies

Suppose ReviewedObservations is also admitted with signature EvidenceModel, role ResearchEvidence, domain CatalogEvidence and review reviewed. Both it and Observations satisfy the requirement, but their Revision identities and datasets remain distinct.

The default rule refuses resolution with both qualified provider identities and the requirement that failed to distinguish them. It does not choose the first declaration, a familiar name, the newest source or an arbitrary provider. It does not merge them into a set: each port requires one module identity.

There are two distinct ways to resolve the ambiguity:

- **Add a genuine semantic discriminator.** If the domain distinguishes canonical accepted research from corroborating research, declare that distinction on providers and require canonical evidence in the consumer contract. The engine can then select the unique provider satisfying the stronger requirement. Inventing `preferred` merely to conceal a concrete choice would add indirection rather than useful meaning.
- **Make the concrete choice explicitly.** Narrow the admitted provider set for this assembly or add a separately scoped source selection. That deliberately returns some responsibility to the author. It is appropriate when the choice is real and no reusable semantic rule determines it.

A declared precedence policy is another possible design, but is outside this unique-match specimen. It would need to define why its ordering is legitimate for the evidence contract; deterministic ordering alone does not make two different authorities interchangeable.

| Admitted qualifying providers | Resolution |
| --- | --- |
| None | Missing-provider diagnostic before model admission; list failed requirements |
| Exactly Observations | Derive both consumer bindings to Observations |
| Observations and ReviewedObservations | Ambiguous-provider diagnostic; neither binding is chosen |
| Same provider instance exported through two aliases | One candidate by qualified instance identity; aliases do not create ambiguity |
| Two distinct instances with identical contracts | Two candidates; equal metadata does not collapse data identity |
| Two providers qualify, but only one is permitted by the domain's canonical-evidence rule | Derive that provider after checking the additional requirement |
| A newly added provider makes an old unique match ambiguous | New generation refuses resolution; an already admitted runtime keeps its pinned graph |
| A replacement leaves a unique match with a different provider identity | Report a semantic binding change and require evolution admission; do not silently redirect stored references |

The procedure extends B's bounded enumeration and conflict checks: form candidate sets from checked semantic requirements, require a unique provider for every port, then validate the complete graph and its dependency cycles. An empty or ambiguous set cannot be repaired by silently changing requirements. Explicit binding proposals remain subject to semantic requirements and rule conflicts; they are not overrides that bypass the contract.

### What the role-based variant adds

| Responsibility | B selected-source rule | B-role semantic matching |
| --- | --- | --- |
| Consumer meaning | EvidenceModel compatibility plus uniform assembly intent | Signature plus evidence purpose, domain and review requirement |
| World context | Concrete provider identity | Domain and review requirement |
| Provider declaration | Membership and compatible exports | Membership, compatible exports and admitted semantic claims |
| Engine derivation | Which ports receive the named provider | Which provider qualifies for each port, then the concrete connections |
| Multiple compatible providers | Context already names one | Semantic requirements distinguish them, or resolution reports ambiguity |

This is stronger contextual derivation, but not knowledge invented by the compiler. The author states requirements and provider meaning once; the engine computes their connections within declared context. Its benefit grows when those facts serve multiple consumers and worlds. For a one-off choice with no meaningful reusable distinction, a direct binding may be clearer.

## Part two Companion effects

### Shared stock model and guarantees

```text
type PositiveQuantity = Integer where self > 0

resource Stock {
  available: Integer
  version: Integer
  invariant available >= 0
}
resource Reservation immutable {
  link stock -> Stock { deletion restrict }
  quantity: PositiveQuantity
}

govern establishment of Reservation by StockReservation
```

Fresh reservation identity is allocated under the stable operation retry identity. `before` reads the protected operation snapshot. The `govern` declaration associates Reservation establishment with the stock law defined in C below, for all specimens. B writes that law's effects and obligations manually; C requests their expansion. For this bounded comparison, admission checks exact normalized obligation/effect templates after typed substitution, not general logical equivalence. Public callers cannot bypass the declared operation to create reservations or change protected stock members. These proposed surface restrictions must be enforced on every admitted write route, not just generated convenience methods.

### B Author enumerates the atomic effects

This operation is also A's mutation specimen; module assembly is the only difference between A and B.

```text
operation Reserve(s: Stock, expected: Integer, qty: PositiveQuantity) {
  authority reserve(s)
  require s.version = expected and s.available >= qty
  effects atomic {
    change s {
      available = before(s.available) - qty
      version = before(s.version) + 1
    }
    create r: Reservation(stock=s, quantity=qty)
  }
  returns r
}
```

The author connects the reservation to the stock and writes both stock assignments at every operation site expressing this behavior. The engine derives type validation, the protected dependency set, effect consistency and the admitted transactional execution plan. Source order does not determine effect order.

### C Author declares the companion law once

```text
effect_contract StockReservation {
  on establish fresh r: Reservation(stock=s, quantity=q) {
    authority reserve(s)
    require before(s.available) >= q
    companion change s {
      available = before(s.available) - q
      version = before(s.version) + 1
    }
  }
}

operation Reserve(s: Stock, expected: Integer, qty: PositiveQuantity) {
  require s.version = expected
  effects atomic using StockReservation {
    establish fresh r: Reservation(stock=s, quantity=qty)
  }
  returns r
}
```

The operation states the requested domain fact and its caller-supplied expected state. The selected contract supplies the authority requirement, availability guard and stock changes. The author still connects this particular reservation to its intended stock: that is domain intent. The repeated connection from creating a reservation to its required stock effects moves into the reusable law.

This variant has more total source for a single use because the rule must be defined. Its benefit must be judged across reuse and the ability to change one law consistently. It adds a derivation capability, not automatic token savings in every specimen.

### Proposed expansion procedure

1. Type-check the operation and selected contract against the resolved model. Match the contract's pattern by Reservation identity and named member roles; do not match arbitrary same-name records.
2. Assign each explicit `establish fresh` occurrence a stable logical effect identity under the operation's retry identity. Bind the pattern variables to that occurrence's typed expressions.
3. Expand matching contracts into additional authority obligations, guards and effects. Conjoin obligations; a contract cannot remove an operation guard or grant authority.
4. Compute closure before runtime effects. For this contract the expansion is finite: it adds one Stock change and no new Reservation establishment. More general contracts require a finite expansion argument; unbounded fresh-effect production refuses.
5. Normalize by effect and target identity. The same originating effect reached through multiple dependency paths expands once. Distinct reservation establishments remain distinct even if their member values are equal. Refuse conflicting writes; do not silently sum or reorder them.
6. Derive the protected read/write set and dependency plan. Validate the final affected state within one private atomic boundary under an admitted adapter strategy.
7. Retain provenance from the operation occurrence through each contract to every derived obligation and effect. Pin the resolved contract meaning to replay and evolution metadata.

Companion rules are compile-time plan derivation, not database callbacks or post-commit triggers. Their effects cannot escape the initiating operation's authority, footprint or atomic boundary. This final-state validation proposal retains the amendment requirement in the shared operation laws.

### Expected expansion of C

```text
input validation: qty satisfies PositiveQuantity
authority: reserve(s)
protected guards:
  before(s.version) = expected
  before(s.available) >= qty
effects:
  s.available := before(s.available) - qty
  s.version := before(s.version) + 1
  fresh r := Reservation(stock=s, quantity=qty)
return: r, after successful outcome is established
origins:
  expected-version guard and reservation: Reserve
  authority, availability guard and stock changes: StockReservation
```

This is the same intended normalized operation as B. It does not fix SQL statement order, lock syntax or physical names. The adapter must protect the expected-state and availability guards through commit, or refuse admission.

### Concrete reservation walkthroughs

| Input and protected state | Expected result in B and C |
| --- | --- |
| available 10, version 4; expected 4, quantity 3 | available 7, version 5; one reservation for 3 |
| available 2, version 4; expected 4, quantity 3 | Refuse; stock unchanged and no reservation |
| available 10, version 5; expected 4, quantity 3 | Expected-state conflict; no effects |
| Two requests expect version 4 | At most one commits against version 4; the other conflicts |
| Same retry identity and same full intent after success | Recover the same reservation/outcome; no second decrement |
| Same retry identity, different quantity | Intent conflict; no new effects |
| Explicit available assignment conflicts with companion assignment | Reject the effect conflict; no source-order precedence |
| Two fresh reservations target the same stock in one operation | This narrow contract refuses competing stock assignments; batching needs a declared aggregation contract |
| Commit request loses its connection | Reconcile authoritative outcome; do not infer rollback or establish another reservation |

Removing the selected contract removes automatic expansion, but does not remove the model's `govern` obligation. Admission refuses an operation whose normalized plan lacks the required guards, authority or stock effects. An operation may supply them explicitly as B does. `using` makes the derivation dependency visible; it is not an opt-out from integrity. The final spelling of the governance declaration remains open.

## Part three Acceptance companions in the existing domain

The stock example establishes the mechanism. For Pyrocat acceptance, use the exact candidate value, format, normalization, validation identity and evidence pins described in the shared operation laws. Content equality alone does not establish acceptance equivalence.

The comparison below uses a semantic effect fact `AcceptProposal`. It is an operation-plan term, not a new stored record or an assertion that the proposal has already been accepted.

```text
effect AcceptProposal {
  proposal: Proposal
  expected: optional Revision
  actor: Actor
  reason: Text
  time: Timestamp
  result: Decision
}

effect_contract ProposalAcceptance {
  on establish a: AcceptProposal {
    let p = a.proposal
    let current = before(current(p.document))
    authority accept(p.document)
    require pending(p)
    require p.base is a.expected and current is a.expected
    require validated_exactly(p)
    require every pin in p.evidence has an admitted role,
            exact target identity and matching target acceptance_fingerprint

    case current present and acceptance_identity(p) = current.acceptance_fingerprint {
      companion create d: Decision {
        proposal = p; disposition = equivalent; result = current
        actor = a.actor; reason = a.reason; time = a.time
      }
    } otherwise {
      companion create r: Revision {
        document = p.document
        revision_number = if current absent then 1 else current.revision_number + 1
        content = p.content
        format_identity = p.format_identity
        normalization_identity = p.normalization_identity
        validation_identity = p.validation_identity
        content_fingerprint = content_identity(p)
        acceptance_fingerprint = acceptance_identity(p)
      }
      companion for each pin in p.evidence create e: RevisionEvidence {
        owner = r; evidence_role = pin.evidence_role
        target = pin.target; expected_acceptance_fingerprint = pin.expected_acceptance_fingerprint
      }
      companion create d: Decision {
        proposal = p; disposition = accepted; result = r
        actor = a.actor; reason = a.reason; time = a.time
      }
    }
    yield a.result = d
  }
}

operation Accept(p: Proposal, expected: optional Revision,
                 actor: Actor, reason: Text, time: Timestamp) {
  effects atomic using ProposalAcceptance {
    establish a: AcceptProposal(proposal=p, expected=expected,
                                actor=actor, reason=reason, time=time)
  }
  returns a.result
}
```

The actor, reason and time are provenance inputs subject to validation. Actor does not establish authority. `validated_exactly` and identity expressions have the meanings in the shared operation laws; they are not host callbacks or current builtins. The closed predicate algebra still needs formal specification.

In B, the case partition and all Revision, RevisionEvidence and Decision effects belong to the operation body, as in [the existing Candidate B example](B-ExplicitContracts.md). In C, the reusable contract defines that topology once. The operation selects the semantic event and supplies its inputs; the engine derives the case, companion facts, result binding, dependencies and protected obligations from the contract. It cannot infer this law merely from the presence of a RevisionEvidence carrier.

The finite evidence loop is bounded by the admitted proposal manifest. Its role uniqueness and exact required-role coverage are validated before effects. Expansion creates only declared effect kinds and no recursive AcceptProposal. Multiple companion contracts must not produce competing terminal decisions; normalization or admission must refuse that conflict.

Derived fact identities use the initiating operation identity, contract occurrence and branch; evidence instances additionally use their unique evidence role. Reordering manifest entries cannot allocate different logical facts. Replay pins the expanded intent and rule version; changing a contract cannot reinterpret a recorded retry. Direct creation of Revision or Decision must satisfy the same governing acceptance/discard obligations, whether manually stated or derived. Selecting a contract is not a route around those obligations.

| Scenario | Expected derived effects in B and C |
| --- | --- |
| No current revision | Revision 1, its exact evidence pins, one accepted Decision |
| Same full acceptance identity as current | One equivalent Decision referencing current; no new revision or evidence |
| Same content, changed evidence pins | New revision with new acceptance fingerprint, exact pins and accepted Decision |
| Validation covers different evidence | Refuse before effects |
| Accept races Discard | One terminal Decision; the loser leaves no partial revision or evidence |
| Evidence provider changes in the world | Reassess target identities and compatibility through evolution; never reinterpret existing pins as the new provider's data |

The current/pending checks, evidence reads and final effects are protected together. Runtime calls authorize at accepted boundaries; result publication, cancellation and uncertain commit retain the shared laws. All derived writes contribute to ledger, question footprints and live routing. Only committed changes become visible; compile-time expansion is not itself a live event.

## What the paired comparison establishes

| Question | A | B | C |
| --- | --- | --- | --- |
| Where is the evidence provider chosen? | Each port binding | Once in world context | Once in world context |
| Who enumerates consumer-to-provider connections? | Author | Engine | Engine |
| Who defines reservation/acceptance meaning? | Author in each operation | Author in each operation | Author in reusable effect contracts |
| Who connects domain effects to their companions? | Author in each operation | Author in each operation | Engine by selected, required contracts |
| Who determines physical execution? | Adapter under the contract | Same | Same |
| What remains explicit? | Concrete bindings and effects | Domain context and effects | Domain context, semantic effects and reusable laws |

B gains contextual assembly without requiring desired-state mutation. C gains companion-effect derivation without a general solver or automatic provider discovery. Neither requires every resulting connection to be declared by hand.

The next evidence should compare complete authoring and repair tasks, including the shared rule definitions, explanations, conflicting contexts, omitted companion laws and rule-version changes. Review the specified procedures independently before implementing a harness. These examples establish a comparison to test, not that the proposed derivation is already correct or preferable in every domain.
