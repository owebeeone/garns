# World and Target Alternatives

Requirement: authors can see the semantic world, generated languages/API styles and
persistence destinations without confusing them. Choosing PostgreSQL is not declaring
a different meaning from SQLite. API async behavior is distinct from adapter strategy
and from SQLite's durability setting of a similar name.

Each option preserves a semantic-world digest separately from build/deployment
identity. Durability, writer authority and isolation remain promises, not optional
tuning. Multiple targets mean separate deployments unless explicitly designed otherwise;
none of these options provides cross-store transactions or replication.

## T1 Separate world, build and deployment declarations

```text
world Catalog { modules catalog durability durable writers governed scope deployment }
build PythonApi for Catalog { language python style async }
deployment Local for Catalog { backend sqlite location env CATALOG_DB }
deployment Server for Catalog { backend postgres location env CATALOG_DB }
```

Move generated targets out of world; retain existing deployment responsibility.
Compiler resolves references and verifies each selected target's capabilities against
the world. Selecting a build/deployment is explicit; there is no last-definition wins.

Valid: same world with two alternative deployments. Refusal: a deployment cannot
provide required atomicity, or two artifacts target the same output name. Future
Python sync and async builds are separately named, not ambiguous variants.

Cost low/medium, mainly IR/configuration separation and artifact identity. Fits any
module model. Concern: world-facing discovery requires an assembled summary across
declarations; provide a resolved-target view. Migration can largely extract existing
generated entries mechanically. No need to put runtime secrets in source.

## T2 Explicit sections associated with a world

```text
world Catalog {
  model { modules catalog durability durable writers governed scope deployment }
  generate { PythonApi: python async }
  persist { Local: sqlite at env CATALOG_DB; Server: postgres at env CATALOG_DB }
}
```

One author-facing composition, three typed sections. The model section alone defines
semantic-world identity; nested configurations have separate identities and validation.
Persistence entries are named alternatives, with explicit selection for execution.

Valid: inspect one declaration to find all targets. Refusal: backend tuning in model,
an ambiguous default deployment, or duplicate artifact names. A reusable module
cannot secretly select an application's destination through import side effects.

Cost medium, straightforward normalization to the same separate IR records as T1.
Best fit to the operator's desire for world-visible targets. Larger applications
may need referenced configuration fragments to avoid giant files; those fragments
must have explicit merge/conflict rules, never ambient inheritance. Migration maps
old world/deployment sources into sections without changing promises.

## T3 Named reusable target profiles

```text
profile AsyncPython { api python async }
profile DurableLocal { persistence sqlite; requires durable }
world Catalog { modules catalog guarantees DurableGoverned }
assembly LocalCatalog { world Catalog; apply AsyncPython, DurableLocal }
```

Profiles are typed parameterized target bundles, not unrestricted configuration maps.
The assembly derives all artifacts after resolving explicit profile parameters.
Conflicting single-valued settings refuse; there is no priority based on file order.
Multiple named output variants remain possible.

Valid: several worlds reuse the same API packaging profile. Refusal: incompatible
profiles choose two engines for one named deployment, or weaken the world's guarantee.
Defaults must appear in the resolved plan and be pinned by profile version.

Cost medium/high, benefits a larger deployment estate. Fits M2/M3 profile signatures;
introduces indirection for one small application. Evolution needs profile-diff impact
across assemblies, not just a schema migration. Does not authorize implicit physical
names: bindings remain explicit inputs or separately reviewed generated artifacts.

## T4 Explicit target applications

```text
world Catalog = CatalogModel<Content>
artifact PythonApi = PythonAsync<Catalog>
store Local = SQLite<Catalog, LocalBinding>
store Server = PostgreSQL<Catalog, ServerBinding>
```

Treat code generation and persistence as typed applications of target constructors
to a semantic world. Constructors declare capabilities and outputs; they are not
database modules inheriting into the domain. Dependency analysis derives build order
and invalidation. Distinct applications have explicit identities.

Valid: one world supplies several generated projections with separate bindings.
Refusal: wrong binding world/version, missing guarantee, or circular artifact dependency.
No declaration executes a connection open merely by being resolved.

Cost high, unifies with M4 explicit linking but requires a typed artifact graph.
Useful if multiple output families become central. Risks turning a data language into
a general build system; restrict constructors to declared compiler/adapter kinds.
Migration records semantic origin separately from artifact dependency changes.

## Comparison

| Option | Gates and derivation | Best property | Concern | Cost |
| --- | --- | --- | --- | --- |
| T1 | P/P/P; world-to-target validation | Smallest migration | Targets dispersed | Low/medium |
| T2 | P/P/P; section normalization and validation | Clear one-place view | Large configurations need references | Medium |
| T3 | P/P/P; typed profile composition | Reuse across deployments | Defaults and override surprise | Medium/high |
| T4 | P/P/P; artifact dependency derivation | Uniform target application | Build-language scope creep | High |

No target is implemented by these examples. All candidates retain async-only current
API scope and accepted adapter obligations. Capability admission, target conflict,
semantic digest stability and generation-path collision are the common proof cases.
Evidence: [world/deployment grammar](../../grammar/garns.lark),
[direction](../../docs/GARNS_DIRECTION.md), [accepted scope](../W1-ACCEPTANCE.md).
