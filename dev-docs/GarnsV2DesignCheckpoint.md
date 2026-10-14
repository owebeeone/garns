# GARNS v2 language design checkpoint

GARNS is being explored as a declarative language for defining database schemas,
access APIs, and the information needed to maintain live query results. The
working direction is composition through lightweight, parameterized modules,
with intents preserving the meaning and rules of data wherever it is used.

This checkpoint records the discussion through splitting the Geymsla example
into Projects, Documents, and Assembly and discussing their imports. It preserves
the reasons for decisions, the current example, and the questions needed to
resume. **The entire language design remains exploratory.** An accepted working
choice below is a direction for this exploration, not a released specification
or permission to implement it. “v2” names the specimen, not a product release.

The deliverable for this checkpoint is this document in `garns/dev-docs`.
The grammar, compiler, runtime, existing examples, and other repositories are
outside this checkpoint's edit scope. Geymsla, GYLD, GLADE, and the declarative
evaluator are reference material. Existing product implementation gates remain
separate; this discussion does not reopen or replace them.

## Product goal and design criteria

The author should describe a data system once and derive consistent storage and
access behavior. SQLite and PostgreSQL are the initial target databases. Other
SQL engines motivated the portability discussion but are not initial targets.

The language needs to describe entities and their data, references, primary and
composite keys, uniqueness, constraints, indexes, reads, and permitted changes.
Backend differences should have explicit mappings without forcing authors to
repeat the same meaning in database-specific definitions.

GLADE supplies the live application context: connected applications listen to
query results, and governed changes identify which results need updating. The
design must retain enough information about reads and writes to keep those
results correct. The exact query, mutation, dependency, and delivery contracts
were not designed in this discussion.

Reuse is central. An author should be able to select consistent identity schemes,
last-modified information, ranges with related bounds, or an entire access-control
subsystem. A component carries its data declarations, rules, and applicable
behavior together. It can be parameterized, instantiated repeatedly under
different names, composed with other components, and reused across databases.
This should reduce drift between otherwise similar tables and schemas.

Upgrades and downgrades are part of the eventual product story, especially when
a reusable component changes many consumers. Designing and implementing those
paths is later work. The immediate task is establishing the language concepts
and exercising them against a small real domain.

## Why the exploration changed direction

The starting material was the [language change register](LanguageChangeRegister.md),
the [exploration proposal](LanguageDesignExplorationProposal.md), and the
[language comparison](LanguageDesignExploration.md). The comparison provides
seven areas and four combined alternatives:

| Package | Example |
| --- | --- |
| A | [Incremental](language-design-options/examples/A-Incremental.md) |
| B | [Explicit contracts](language-design-options/examples/B-ExplicitContracts.md) |
| C | [Contract composition](language-design-options/examples/C-ContractComposition.md) |
| D | [Explicit assembly](language-design-options/examples/D-ExplicitAssembly.md) |

The user found these packages difficult to choose between. They vary several
decisions together, and some alternatives could be complementary mechanisms.
The discussion therefore moved to one authoring task and one semantic decision
at a time. No A–D package was selected wholesale.

We first inventoried the existing Lark language: modules and imports; types and
intents; uses and reusable groups; resources, events, associations, families and
members; links and deletion policies; rules; reads and operations; and world,
deployment, and evolution declarations. That inventory describes the explored
surface, not a requirement to preserve every construct. Parsing a declaration
also does not establish that its behavior is implemented.

### Research and evaluation approach

The language comparison considered how Rust separates structs and traits, how
Go composes structs through embedding, how ML-style parameterized modules compose
subsystems, and how constraint languages combine declarations. The useful
questions are about data, behavioral contracts, reuse, and parameterization;
there is no single “modern” replacement for a class that resolves all four.

[PLIERS](https://arxiv.org/abs/1912.04719) provided the user-centered design
method discussed: start with needs and natural expressions, develop mechanisms,
analyze their risks, refine them with small studies, and assess realistic tasks.
For this exploration, that means eliciting an example before supplying syntax,
asking what it should expand to, changing it, and testing the predicted result.

The user also supplied the
[Declarative API Evaluator](../../../bizscad/dev-docs/DeclarativeApiEvaluatorV2.md)
(the file's internal heading identifies version 3). Its relevance is the amount
of work derived from local declarations, composability, and the correctness of
that derivation. Requiring application-level wiring everywhere is not inherently
more declarative than deriving it from local sharing declarations.

These ideas guided the conversation; no numerical evaluation was performed.
LLM authoring needs its own fixed tasks, semantic checks, and edit/repair
evaluation. Human preference for a notation does not establish LLM reliability.

## Working language concepts

| Concept | Role in the emerging design |
| --- | --- |
| Module | Owns declarations and anchors composition, parameters, visibility, and dependencies. |
| Type | Defines the shape or representation of a value. |
| Intent | Defines reusable domain meaning, with a type, description, and applicable restrictions. An intent is not itself a stored value. |
| Use or role | Places an intent or value component in an owner; a local name distinguishes repeated occurrences. |
| Structured value | Groups members that can be addressed individually or manipulated as one value. |
| Resource | Declares a collection of identified records; current examples use this spelling rather than `table`. |
| Reference or link | Connects resources, with presence, identity, inverse, and deletion behavior where applicable. |
| Rule | States a condition or policy; `final` controls whether it may be overridden. |
| Read and operation | Describe access and permitted changes. Their revised syntax remains open. |
| Assembly | Combines configured modules into the intended database model. |

This is a conceptual inventory, not a final list of keywords. For example, it
does not settle whether all existing carrier kinds remain necessary, how
indexes are expressed, or how static queries and live questions fit the new
surface.

### Modules and intent ownership

The accepted direction is a module that can be empty, contain a single concept,
define a small component, or contain an entire subsystem. Its size is unrestricted,
but its names, parameters, dependencies, and exports still have boundaries.
Declaring a module should not by itself introduce runtime objects or tables.

The class analogy is useful for collections of declarations, inheritance, and
template parameters. A module instance configures part of a database model; it
does not automatically represent a row or runtime object.

**Concrete intents belong to modules.** They are not freestanding global
concepts. Vocabulary modules can own widely reusable intents, and domain modules
can own intents beside their resources. Public concepts can be referenced by
qualified names such as `ProjectConcepts.ProjectStatus`. Reusing or locally
aliasing an intent preserves its declaration identity and restrictions.

The user specifically corrected examples that returned to plain `id: type` and
`name: type` fields. Resources should select meaningful intents and inherit
their semantics. The local role name identifies an occurrence; the physical
column name is a backend mapping concern.

### Templates and structured values

The first exercise was a Sensor containing three instances of a Range component,
named `normal`, `warning`, and `alarm`. The user's natural expression was: give
an instance a name, select its template, supply parameters, and repeat.

The agreed logical access is `warning.lower` and `warning.upper`. **Range is
also a structured value**: its members can be passed or assigned together.
Physical storage might flatten those members into names such as `warning_lower`.
Neither a PostgreSQL composite representation nor an underscore mangling
algorithm was selected; collision handling and backend mapping remain open.

An intent parameter must preserve the supplied intent's meaning and restrictions,
not merely substitute its scalar type. The Range exercise supplied a Temperature
intent to both bounds and added a rule relating them. A reusable collection of
intents can therefore be a lightweight module; a collection of actual values,
such as a list of scores, remains a different concept.

The saved Geymsla example exercises intent parameters, typed constant and set
parameters, argument forwarding, and structured SourceLocation values. Passing
whole modules as parameters and selecting only parts of a module were discussed
as possibilities but have not been designed or demonstrated.

## Inheritance identity and visibility

We separated two independent questions: which instance is used, and who can
refer to it. Multiple inheritance assembles existing modules. Ordinary
inheritance in the specimen creates a separate instance; `shared` requests a
shared instance. Earlier wording included `singular` and explicit `distinct`.
The working examples use `shared` and omit a distinct modifier for ordinary
inheritance. A complete defaults policy has not been settled.

The user accepted this exploratory shape:

```text
private shared inherit Users as otherUsers
```

It selects a named shared Users instance and limits access through that path.
Different inheritance instance names can select different shared instances.
This differs from an alias for an imported definition or intent: changing a
local spelling does not necessarily create a new concept. The language must
make these meanings of naming precise.

| Visibility | Working meaning |
| --- | --- |
| Public | Exposes a declaration or inherited path to outside users of the module. |
| Protected | Allows the module and its inheritors to use the declaration/path without publicly exporting it. |
| Private | Permits internal use without exposing that path to unrelated modules or inheritors. |

Visibility is access to language declarations, not database authentication or
data confidentiality. `private shared` does not promise exclusive ownership.
Another permitted path to the same shared instance can expose its public
interface. That distinction raised the user's concern about surprising access
and shared mutation. Renaming `singular` to `shared` makes the consequence more
visible but does not resolve it by itself.

### The C++ diamond comparison and deferred boundaries

The C++ comparison established that virtual inheritance shares a base within
one most-derived object. Private inheritance restricts a path; another public
virtual path can expose the same base's public interface. It does not expose
the base's own private members or make separate objects share globally. This
behavior is documented in
[Microsoft's access-control discussion](https://learn.microsoft.com/en-us/cpp/cpp/member-access-control-cpp?view=msvc-170#access-control-with-multiple-inheritance).

The research discussion distinguished intentional mixed-path behavior from
historical compiler access-checking defects. Related discussions suggested
composition or distinct types/template specializations to limit sharing,
including this [discussion of virtual-base sharing boundaries](https://stackoverflow.com/questions/29863672/limit-object-sharing-of-virtual-base-classes-in-c).
They did not establish an adopted replacement C++ rule.

An explicit enclosing sharing scope was proposed during our discussion. The
user observed that the simple example could already be expressed with a
separate ordinary instance. Two separately instantiated groups, each sharing
internally, would be a more meaningful boundary test. Whether ordinary module
instantiation supplies that boundary remains open.

**The user chose to stop pursuing that issue for now**, keep the inheritance
and named shared-instance syntax, and move on. Explicit sharing-scope syntax
and friends are not accepted requirements. The precise merge key, parameter
compatibility rules, and treatment of conflicting shared declarations remain
unresolved. Shared identity must not be inferred from similar table shapes.

## Rules and scoped overrides

The initial proposal separated invariants from overridable rules. The user
pointed out that both are rules and accepted **`rule` and `final rule`** instead.
`final` means non-overridable. It does not determine when a rule runs or change
a validity condition into a different kind of condition.

The agreed working distinction is:

```text
rule ceiling: upper <= 100

override rule Sensor.warning.ceiling:
    upper <= 150

override rules Sensor.warning {
    rule ceiling: upper <= 150
}
```

These are illustrative override forms, not executable grammar. A plain rule
adds a condition; a named override replaces a named inherited rule at a
specified scope. The plural `override rules` explicitly replaces the
overridable rule set at that scope. Omitting a name from singular `override rule`
must not silently mean replace everything. An unnamed ordinary rule adds a
condition.

Final rules cannot be removed or replaced by either form. Scope-wide replacement
is not permission to erase every nested rule. Exact name resolution, override
conflicts, and interactions with specialized templates still need specification.
When specialization only changes a number, a template parameter may be simpler
than overriding a predicate.

In the current specimen, validity rules constrain the resulting transaction
state on every admitted mutation path. Finality and validity are separate
axes. The example does not yet define a general system of rule effects,
scheduling, or lifecycle transitions.

## Choosing Geymsla as the real example

GYLD's decision and evidence model, GLADE's identity and key-management material,
and Geymsla's document inventory were considered. The third project name was
clarified to **Geymsla**, with the
[investigation document](../../../geymsla-wz/dev-docs/GeymslaInvestigation-Rev1.md)
as its source. That investigation remains open and leans toward PostgreSQL;
the specimen does not commit Geymsla to SQLite.

The user chose **a small Geymsla example without expanding into GYLD**. We
started with files, checkout locations, and content hashes, then added document
state and a hierarchy of projects. Search engines, embeddings, GYLD decision
processing, and production ingestion remain outside the example. A future
reference to published decisions could supply provenance without importing the
decision engine, but that integration was not selected.

### Project lifecycle decisions

The user selected these states:

```text
Draft, Approved, InProgress, Finished, Abandoned
```

Each project has its own explicit completion decision. Terminal descendants
permit parent completion; they never cause it automatically. A Finished
project must have every descendant either Finished or Abandoned. Draft,
Approved, and InProgress descendants block it. Abandonment satisfies the
prerequisite without being counted as successful completion.

The working rule covers all descendant depths, excluding the project itself.
An abandoned intermediate project cannot hide an unfinished descendant. A leaf
can be explicitly completed. The example also imposes an acyclic parent relation.

The validity condition applies after changes, including reopening, insertion,
and reparenting. Reopening a descendant below a Finished ancestor requires a
resulting state in which the ancestor is no longer Finished, potentially by
changing both in one transaction. No automatic reopening cascade was chosen.
Rules for abandoning a parent, and the full permitted transition graph, remain
open beyond the conditions above.

The reusable template is `ProjectHierarchy`, parameterized by an identity intent,
a state intent, a completed value, and a set of terminal values. Geymsla supplies
ProjectId, ProjectStatus, Finished, and `{Finished, Abandoned}`. Constants must
satisfy the supplied state intent. This makes the template carry meaning as well
as configurable policy.

### Documents and file occurrences

The user asked to record document currency, completion, a completion date, and
project membership. The specimen separates three things:

| Resource | Meaning |
| --- | --- |
| Document | A logical document, identified independently of its byte contents, belonging to a project. |
| FileOccurrence | A document observed at a checkout-relative location, with a content hash. |
| Classification | At most one current state record for a document, recording currency and completion. |

The current **specimen choices**, rather than a fully accepted document lifecycle,
are currency values Unknown/Current/Superseded, completion values Open/Finished,
and a timestamp present exactly when completion is Finished. Reopening clears
that current timestamp; historical completion events are not modeled. Missing
classification means unclassified, not implicitly Current or Finished.

Currency and completion are independent: a finished document can later be
superseded. Neither filenames, hashes, nor modification times silently determine
these facts. Project completion is not automatically derived from its documents.

`SourceLocation` is a structured value containing checkout and path. Its proposed
key semantics make the pair unique, without making either member individually
unique. Equal content hashes do not merge document identities: a live document
and a separately classified snapshot may contain equal bytes. Multiple file
occurrences can also refer to the same logical document.

## Saved specimen and intended expansion

The original combined `Geymsla.garns-v2.txt` was replaced, at the user's request,
by exactly three files under `dev-docs/geymsla-garns-v2`:

| File | Declarations |
| --- | --- |
| [projects.garns-v2.txt](geymsla-garns-v2/projects.garns-v2.txt) | ProjectConcepts, ProjectHierarchy, GeymslaInventory |
| [documents.garns-v2.txt](geymsla-garns-v2/documents.garns-v2.txt) | DocumentConcepts, FileConcepts, SourceLocation, DocumentCatalog, FileInventory, DocumentState |
| [assembly.garns-v2.txt](geymsla-garns-v2/assembly.garns-v2.txt) | Geymsla, NamedCatalogExample, review cases and open questions |

There are eleven module declarations and nine concrete intents. All concrete
intents are module-owned. The main assembly currently reads:

```text
module Geymsla {
    public shared inherit GeymslaInventory as inventory
    public inherit FileInventory<DocumentConcepts.DocumentId> as files
    public inherit DocumentState<DocumentConcepts.DocumentId> as document_state
}
```

FileInventory and DocumentState each request the same protected shared
`DocumentCatalog<Identity>` as `documents`. That catalog requests the shared
GeymslaInventory as `inventory`. The main assembly directly requests that same
inventory. The intended expansion is therefore **one Project, one Document,
one FileOccurrence, and one Classification resource**.

The saved example uses protected catalog paths so inheritors can build on them.
Earlier spoken descriptions called these paths private; the file's current
protected declarations are the specimen to review.

`NamedCatalogExample` is a separate review exercise, not inherited into Geymsla.
It privately inherits two shared catalogs named `working` and `comparison`.
The expected result is two distinct Document resources and one shared project
inventory. Changes to one catalog do not create matching documents in the other.

The example now exercises intent and value parameters, forwarding parameters
through inheritance, structured values, multiple inheritance, repeated shared
dependencies, named independent instances, all three visibility levels, and
final rules. It does not yet exercise a useful positive override, module-valued
parameters, selective inclusion, or actual read and mutation declarations.

### Imports and the current file discrepancy

The user noticed that the split originally had no imports. The discussed
proposal gives Assembly these imports:

```text
import "./projects.garns-v2.txt" (GeymslaInventory)
import "./documents.garns-v2.txt" (
    DocumentConcepts,
    DocumentCatalog,
    FileInventory,
    DocumentState
)
```

Documents in turn imports GeymslaInventory from Projects. Relative paths are
resolved from the importing file. An import makes selected definitions available;
inheritance creates or combines model instances. Imports do not create tables,
grant access to private members, or require callers to import each hidden
dependency. A definition retains its own dependency bindings. Direct and
transitive imports should refer to the same definition.

**At checkpoint inspection, Documents contains its import, but Assembly contains
neither of the two imports above.** Assembly still says that file loading/import
syntax is not selected, and Documents points to Assembly for import semantics
that are not there. This differs from the final voice-session report that the
imports had been added. The reason is unknown; the current bytes were preserved.
The proposal is recorded here so the next edit can reconcile the example without
losing the discussion. Import grammar remains exploratory regardless of that
file discrepancy.

## Review cases and remaining decisions

The saved review cases describe expected semantics, not executed language tests.
They check one shared catalog across two branches, distinct checkout/path keys,
equal hashes without identity merging, separate named catalogs, visibility, and
rejection of final-rule replacement. Further useful exercises are:

1. Finish children and verify the parent stays unchanged until explicitly finished.
2. Try to finish an ancestor with an open grandchild under an abandoned child.
3. Reopen or reparent a child under a Finished ancestor, both alone and with the
   necessary ancestor changes in the same transaction.
4. Supply incompatible template arguments to the same named shared dependency
   and inspect the diagnostic rather than silently choosing one.
5. Copy a structured value and verify member rules and its cross-member rule remain
   applicable; test a physical-name collision separately.

The main unresolved language questions are:

| Area | Next decision |
| --- | --- |
| Templates | Parameter kinds and contracts, argument equivalence, defaults, and checking intent-dependent constants. |
| Composition | Shared identity resolution, collisions, incompatible declarations, and override conflicts. Broader sharing boundaries remain deliberately deferred. |
| Names and visibility | Visibility defaults, inherited name lookup, and the distinction between local aliases and named instances. |
| Imports | Exact file/module syntax, exported names, resolution, and diagnostics. |
| Values | Whole-value assignment, optional structures and members, collections, and physical layout mappings. |
| Rules | Binding names, override targets, scope-wide replacement, rule diagnostics, and quantification semantics. |
| Resources and links | Key/unique/index declarations, reference typing, inverse relations, and deletion policies across composition. |
| Reads and changes | One useful query and one governed mutation, transaction boundaries, validity checks, and eventual live-result dependencies. |
| Assembly and targets | Separation of model semantics from deployment choices and backend capabilities. |
| Evolution | Changes to component instances and future upgrade/downgrade paths. |

No new implementation requirement follows solely from this list. Add constructs
when a concrete example requires them, rather than expanding Geymsla to exercise
every theoretical feature.

## Evidence limits and follow-up findings

The specimen explicitly says it is not accepted by the current GARNS grammar.
The discussion did not implement parsing, SQL generation, runtime enforcement,
or migrations for this syntax. Earlier file-split and import checks were textual
checks, not language execution. The review cases remain expectations to test
when an implementation is separately authorized.

Two documentation mismatches need a later reconciliation:

| Finding | Evidence and impact | Suggested follow-up | Blocks this checkpoint |
| --- | --- | --- | --- |
| Assembly import proposal is missing from disk | Assembly lacks imports and retains the pre-import note; Documents contains a project import and refers to missing Assembly semantics. Readers cannot follow the latest proposed file composition from the files alone. | Restore or reconcile the discussed imports and explanatory notes in a separately scoped example edit. | No |
| The earlier bundle direction differs from the new structured-value decision | L3 of LanguageChangeRegister explicitly excludes nested structured values; the later Range discussion and SourceLocation specimen require a structured value. Readers could mistake the older direction for the latest choice. | Reconcile the change register and relevant option documents with this checkpoint before treating them as a unified specification. | No |

The existing grammar still uses its existing constructs, including invariant
syntax. That is an implementation/design distinction, not itself a compiler bug.
The A–D documents also remain historical alternatives; they were not rewritten
or selected during this checkpoint.

## Where to resume

First reconcile the Assembly imports and read the three-file specimen as one
model. Confirm the intended four resources and shared identity paths before
adding more features. Then define one concrete operation and one read, for
example recording a file occurrence and listing a project's documents, followed
by a project-status change that exercises the completion rule.

For each exercise, record the author's intended meaning, the derived resources
and behavior, one failing case, and the diagnostic that would make it easy to
repair. Resolve the language decisions exposed by that task. Keep grammar and
runtime implementation as a separate authorized step once the semantics are
concrete enough to test.
