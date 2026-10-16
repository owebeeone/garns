# Whole Language Example Sets

All source blocks here are proposed notation, not files accepted by the current
parser. They illustrate semantic decisions and deliberately do not fix a grammar.
No code block has been executed. The one executed baseline probe is documented
separately in [Baseline.md](../Baseline.md).

[Contextual binding and companion effects](ContextualBindingAndCompanionEffects.md)
adds a controlled A/B/C comparison: manual wiring, contextual module binding, then
companion-effect derivation. It includes resolution procedures, expected expansions
and refusal cases. A role-based binding variant additionally derives provider choice
from purpose, domain and context, with explicit missing/ambiguous-provider behavior.
It does not replace the four whole-language candidates below.

| Set | Combination | Main question |
| --- | --- | --- |
| [A](A-Incremental.md) | R1 C1 B1 T1 V1 M1 O1 | How far can completed existing constructs take us? |
| [B](B-ExplicitContracts.md) | R1 C2 B2 T2 V2 M2 O2 | Can a small semantic core derive behavior without hidden policy? |
| [C](C-ContractComposition.md) | R3 C3 B3 T2 V3 M3 O3 | Can one contract/composition model serve larger reusable domains? |
| [D](D-ExplicitAssembly.md) | R2 C2 B2 T4 V4 M4 O4 | Is broader engine derivation worth a more explicit model and planner? |

Every set describes the same Pyrocat meanings and exercises the same cases below.
Shared [operation laws](OperationLaws.md) are requirements, not an executable helper
library. When an example abbreviates an evidence check, those laws spell it out.

## Common domain contract

| Concept | Required fields and relationships |
| --- | --- |
| Catalog | Name unique in the world |
| Document | Name unique within catalog; change policy; catalog reference |
| Revision | Positive number unique per document; content; format, normalization and validation identities; content/acceptance fingerprints; document reference; immutable |
| RevisionEvidence | Owner revision plus evidence role unique together; target revision and expected acceptance fingerprint; immutable |
| Proposal | Reference unique per document; exact candidate and format identities; actor, reason and time; document and optional exact base; immutable |
| ProposalEvidence | Owner proposal plus role unique together; target revision and expected fingerprint; immutable |
| Decision | Proposal reference unique; accepted/equivalent/discarded disposition; actor, reason, time; result revision present exactly for accepted/equivalent; immutable |
| SourceObservation | Reference unique per revision; source bytes, fingerprint, provenance, actor and time; revision reference; append-only |

Base and result must refer to the same document as their proposal. Required evidence
roles are present exactly once; pins never mean latest. Current revision and pending
proposal are derived facts, not additional independently writable fields.

The specimens show the common fields most relevant to each alternative rather than
repeating the entire domain contract verbatim. The table above supplies all omitted
field obligations. These are design examples, not complete executable applications.
World module lists are also abbreviated: all imported dependencies must belong to
the selected world, as required by the baseline. No specimen grants cross-world
references or implicitly changes that closure-admission rule.

## Relationship microcase

The equivalent semantics must be expressible in each candidate's relationship form:

```text
Evidence.owner -> Revision: required, target deletion restrict
OwnedNote.owner -> Revision: required, target deletion cascade
Bookmark.target -> Revision: optional, target deletion detach
ExternalNote.target -> Revision: optional, unenforced
Evidence unique by owner and evidence_role together
```

Deleting a referenced Revision is blocked by Evidence. With that blocking evidence
absent, deleting it removes OwnedNote owners and clears Bookmark.target atomically.
ExternalNote has no automatic existence/deletion guarantee; it may retain an unresolved
reference. Making Bookmark.target required while keeping detach is rejected.
The same evidence_role can occur for different owners, but not twice for one owner.
Other invariants may still forbid a deletion even when its reference actions permit it.

## Fixed case set

| Case | Required observation |
| --- | --- |
| E1 relationships | Restrict blocks referenced deletion; cascade removes owners; detach clears optional references and refuses required ones; unenforced is explicit; owner/role uniqueness is joint |
| E2 value rule | Positive revision reused in unrelated carriers; zero input/default/migration value refused |
| E3 companions | Two lower/upper instances remain distinct and both inherit lower <= upper |
| E4 names | A::ID and B::ID coexist; imported Entry still uses its original ID |
| E5 modules | Content type, intent, predicate and module supplied; two named instances have deliberate distinct identities |
| E6 document edits | Keep, null, remove, false, zero, exact decimal, unknown fields and original bytes retain distinct meaning |
| E7 acceptance | First, changed and equivalent acceptance; concurrent base conflict; accept/discard conflict; field authority and evidence pins preserved |
| E8 another domain | Reserve stock with guarded version and available amount; no artificial Pyrocat-specific runtime primitive |
| E9 targets | Same model, alternative SQLite/PostgreSQL destinations, async Python surface; future sync is design capacity only |

The cases were drawn from the operator's requirements and existing GARNS contracts.
They were visible during design, so they are not held-out validation or an independent
oracle. Counterexamples below are proposed tests, not observed passing tests.
