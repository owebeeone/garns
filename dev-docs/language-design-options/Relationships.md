# Relationship Design Alternatives

Requirement: express reference identity, target deletion, absence and joint
uniqueness without requiring database concepts. Current `end` defaults to restrict;
detach requires optional; all key flags together form one uniqueness rule.
Standalone unenforced is distinct from a deletion action.

The examples use a Decision pointing to Proposal and RevisionEvidence identified
by owner plus role. SQL foreign keys are one adapter strategy, never the definition.

## R1 Inline link policies

```text
link proposal -> Proposal { deletion restrict key }
link result -> Revision { deletion detach optional }
use evidence_role { key }
link owner -> Revision { deletion restrict key }
```

Keep the existing model and improve its vocabulary. Qualified links resolve as
today; the compiler gathers all key participants after expansion. Deletion refers
to the target: cascade removes owners, detach clears references, restrict refuses.
No source order determines behavior. Unenforced references explicitly lack existence
and target-deletion guarantees; combining them with a deletion action refuses.

Refusal: required result plus detach. Valid case: optional result detached when its
target is deleted, provided resulting invariants still hold. A valid but duplicate
owner/role pair refuses even if each field individually appears elsewhere.

IR largely unchanged; adapters enforce the declared action or refuse capability.
Expose a resolved-key explanation so authors see the combined uniqueness rule.
Migration cost low for spelling, medium for end-to-end enforcement. Best with B1/B2;
expansion must not accidentally merge unrelated keys. The implicit joint-key grouping
is compact but surprising for multiple independent uniqueness requirements.

## R2 Named relationship declarations

```text
relationship DecisionProposal {
  owner Decision as proposal
  target Proposal
  cardinality exactly_one
  target_deletion restrict
}
unique Decision by proposal
unique RevisionEvidence by owner, evidence_role
```

Relationships are first-class named facts outside carrier bodies. The endpoint role
introduces a reference-valued member; named uniqueness separates identity constraints
from the reference itself. The compiler builds an adjacency model and generated
accessors; no independent duplicate inline link is permitted.

Refusal: two relationships introduce Decision.proposal without aliases, or detach
on exactly_one. Valid case: a zero_or_one result role with detach. Preserve standalone
unenforced as a relationship mode, not as an action. Unknown targets are admissible
only under that mode; present targets retain the declared logical reference type.

New relationship IR can lower to existing link primitives for simple cases. Named
constraint identities help diagnostics and migration; moving an inline link needs
an explicit continuity map. Cost medium. Fits M4 linking and O4 relation-oriented
effects. Concern: reading one carrier requires following external declarations;
tooling must show the assembled view. More typing is not automatically more declarative.

## R3 Reusable relationship contracts

```text
relation_contract OwnedEvidence<Owner, Target> {
  reference owner: Owner required target_deletion restrict
  reference target: Target required target_deletion restrict
  value evidence_role
  unique owner, evidence_role
}
association RevisionEvidence satisfies OwnedEvidence<Revision, Revision>
```

Define recurring relationship patterns once and instantiate them with types and
roles. Contracts retain invariant and uniqueness identity through substitution.
Applying a contract expands its members and obligations, not a separate nested
entity. Explicit aliases are needed for repeated instances.

Refusal: an implementation weakens required target existence or forgets the joint
uniqueness guarantee. Valid case: two associations reuse the owner/role pattern with
different owner types. A separate optional-reference contract permits detach;
unenforced is a different contract that cannot satisfy enforced existence.

IR records instantiation origin plus expanded links/constraints; adapters consume
the expansion. Migration tracks contract-version effects at every use. Cost high,
especially if added beside another incompatible template system. Best with M2/M3
and B3; avoid inventing a second kind of module parameter. Good reuse for large models,
less useful for one-off links; a bad shared contract has a wide impact.

## R4 Named integrity rules over typed references

```text
link proposal: ref Proposal
rule decision_target: every Decision.proposal resolves
rule one_decision: unique Decision(proposal)
rule evidence_identity: unique RevisionEvidence(owner, evidence_role)
on target_deleted(Revision): detach optional references selected by ResultRole
```

Separate reference shape from a closed set of named integrity rules. This is not
an arbitrary trigger language: admit existence, uniqueness and explicit deletion
actions only. Unenforced omits existence by an explicit exemption; accidental rule
omission is rejected by a requirement that every link states a reference policy.

The compiler normalizes rules to a constraint graph and detects conflicting delete
policies before execution. Refusal: both restrict and cascade apply to the same role;
required references cannot be detached. Valid case: one rule applies a policy to an
explicit named collection of roles. Action order is derived from the dependency
graph; cycles or inconsistent resulting constraints refuse, not first-rule wins.

Cost high. Useful with C4/B4 if one shared rule algebra exists; difficult with implicit
inheritance and open-ended selectors. Evolution needs explicit membership diffs so
a newly selected role cannot silently acquire cascade. Its advantage is model-wide
policy reuse; its risk is hidden reach and harder local explanation.

## Comparison and proof obligations

| Option | Declarativity gates | Strongest benefit | Principal concern | Relative cost |
| --- | --- | --- | --- | --- |
| R1 | P/P/P: link resolution and joint constraint derivation | Local, familiar, minimal change | Implicit joint-key grouping | Low/medium |
| R2 | P/P/P: endpoint assembly from named declarations | Visible relationship identity | Fragmented authoring | Medium |
| R3 | P/P/P: typed contract expansion | Reusable relationship semantics | Contract/template machinery | High |
| R4 | P/P/P: closed rule graph normalization | Shared model-wide policies | Nonlocal action scope | High |

All are design arguments, not implemented checks. For each, qualify restrict,
cascade, detach, missing required targets, standalone unenforced, joint-key conflicts
and deletion-induced invariant failures. Delete closure and ledger effects must
remain within one governed transaction. Do not select solely by source brevity.

Current evidence: [grammar](../../grammar/garns.lark), [resolver](../../src/garns/resolve.py)
`resolve_link`, and [reference](../../docs/DSL_REFERENCE.md) Links. No known historical
decision requires the word end rather than deletion; its rename is a proposal.
