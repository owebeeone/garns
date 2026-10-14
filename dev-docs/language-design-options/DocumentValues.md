# Document Value Alternatives

Required meaning: finite recursive null, Boolean, exact number, Unicode text,
ordered sequence and unique-text-key mapping. Omission differs from explicit null;
false and zero are values. Mapping order and numerical spelling do not change
meaning; sequence order does. Unknown fields survive edits. Original bytes are
separate observations, not the canonical value. No option equates this with JSONB.

The word intent below means a GARNS declaration; an evaluation scenario is called
a use case to avoid confusing the rubric's separate use of that word.

## V1 One exact document scalar with typed access operators

```text
intent content: DocumentValue
query member_presence { show content.lookup("note") }  # Missing | Present(Value)
operation edit { input patch: DocumentPatch }
```

Add a closed recursive scalar to the value universe plus a small typed lookup/update
algebra. `lookup` returns a presence sum; Present(Null) is not Missing. Patch entries
are Keep, Remove or Set(value); an omitted patch entry means Keep. ByteBlob stores
observations. Exact decimal normalization is versioned and never uses binary float
as an intermediate.

Valid: set note to Null while leaving another unknown member unchanged. Refusal:
duplicate object keys, nonfinite numbers, malformed Unicode or a value beyond declared
bounds. Format validation remains a separate pure contract, not the carrier schema.

Cost medium/high; codecs, operators, limits and canonicalization are real work, but
carrier IR changes remain relatively small. Strong fit with incremental A. Weakness:
member types are not statically known without explicit narrowing; generic queries
can devolve into many guarded path operations. Adapters may use blobs or native
documents only if all advertised predicates and exactness semantics are preserved.

## V2 Structural value schemas with open extensions

```text
value Subject {
  name: Text required
  note: nullable Text optional
  extras: open DocumentValue
}
intent content: map<Text, Subject>
```

Declare known shapes while retaining unknown members in a lossless extension map.
Presence and nullability are independent. A schema field is absent, present-null
if permitted, or present-value. A structural value is not B2's flat intent bundle:
it is a nested value with defined equality and projection semantics.

Valid: typed query of subject.name and round-trip preservation of an unfamiliar
member. Refusal: extras collides with a declared name, a wrong typed field is hidden
in extras, or removal of a required field. Open extras have no implicit edit authority;
Pyrocat operations preserve them unless their format explicitly allows modification.

Cost high; recursive shape IR, generated types and migration of shape refinements.
Pairs well with C2 refined types and M2 signatures. It removes repetitive narrowing
but requires a declared schema for detailed research. Exact numbers and canonical
identity still need the same primitives as V1. Evolving an unknown field into a
known one validates existing values instead of silently coercing them.

## V3 Versioned format contracts and typed projections

```text
format CatalogDocument version 1 {
  value DocumentValue
  projection subjects: sequence<Subject>
  preserves unknown_members
  canonicalization ExactDocumentV1
}
intent content: CatalogDocument
```

Keep the recursive value and give it a named interpretation contract. One declarative
projection description derives typed research surfaces; an external format adapter
may implement bounded codecs but cannot mutate catalog state. The raw value remains
authoritative. Projections are derived, versioned and not independently editable.

Valid: a subject query follows the interpretation version pinned on its revision.
Refusal: adapter returns a projection inconsistent with its source fingerprint,
changes interpretation under the same version, or cannot preserve unknown fields.
Projection reconciliation must run under acceptance atomicity if materialized.

Cost high; explicit format boundary and independent codec/projection evidence needed.
Fits C3/M3 and state-transition operations. Without a defined projection algebra this
would merely hide imperative interpretation behind a name; that version fails the
meaningful-derivation gate. The viable option includes inspected projection expressions
and a separately identified, hermetic codec boundary. Complex formats remain a risk.

## V4 Explicit recursive value model

```text
value Value = Null | Bool(Boolean) | Number(ExactNumber) | Text(Text)
            | Sequence<ordered Value> | Object<unique Text => Value>
intent content: Value
projection SubjectNames from Object entries ...
```

Represent the document algebra explicitly in the semantic model, with generated
visitor, construction and projection APIs. Values form trees; physical sharing is
an adapter optimization, not observable identity. Sequences carry order; objects
carry unique keys; a missing entry has no node. Original bytes remain separate.

Valid: traverse or transform any node without loss of unfamiliar structure. Refusal:
cycles, two entries with the same key, unordered sequence data, or accidental use of
storage node identity as value equality. A patch still distinguishes Keep/Remove/Set.

Cost very high for ergonomic bulk APIs and bounded traversal; particularly costly
if lowered naively into many rows. Fits relational/rule-oriented D without making
SQL tables the model. Exact reconstruction and efficient large-value operations
must be demonstrated. It offers maximal inspectability at the cost of exposing more
structural machinery to authors; generated conveniences cannot change semantics.

## Shared boundaries and comparison

Define exact number domain, canonical algorithm, negative-zero treatment, Unicode
policy and depth/size limits before implementation. Proposed meaning equates decimal
spellings of the same finite mathematical value, including signed zero; source bytes
preserve spelling. No Unicode normalization should be silently introduced. Concrete
resource limits are capability profiles, not reasons to truncate values.

| Option | Gates and derivation | Best property | Concern | Cost |
| --- | --- | --- | --- | --- |
| V1 | P/P/P; typed document operators and codecs | Small domain surface | Runtime path narrowing | Medium/high |
| V2 | P/P/P; recursive shape validation/projections | Typed known fields plus retained unknowns | Structural-type machinery | High |
| V3 | P/P/P; declared format projections | Versioned research interpretations | Escape-boundary fidelity | High |
| V4 | P/P/P; algebra-generated visitors/projections | Explicit complete value model | Authoring and storage expansion | Very high |

The current Opaque type is not any of these contracts. All four preserve the same
test vectors: omitted/null/false/zero, decimal spellings, ordered arrays, unknown
fields, source formatting and oversized input refusal. Large-input qualification
must include the roughly 100 MB inventory; no performance claim is made here.
See [baseline](Baseline.md) and [type implementation](../../src/garns/types.py).
