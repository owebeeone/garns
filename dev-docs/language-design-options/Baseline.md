# GARNS Declarativity Baseline

This is a bounded source audit for the seven exploration areas, not a full runtime
correctness review. The inspected implementation is the working tree based on
commit 715b54e. Unrelated in-progress worker and PostgreSQL contract edits are not
treated as accepted language behavior.

## Existing strengths

GARNS already separates declarations, qualified semantic IR and authored physical
bindings. Intents centralize field meaning; references are typed; traits compose
fields; queries describe results; live questions have an intentionally closed,
bounded algebra. Evolution already distinguishes logical continuity from physical
renaming. These are valuable foundations, not scaffolding to discard automatically.

## Evidence and gaps

| Area | Observed baseline | Classification and source |
| --- | --- | --- |
| Relationships | Link target, deletion policy, optionality and combined key flags; explicit physical mapping | Implemented baseline; [grammar](../../grammar/garns.lark), [SQLite lowering](../../src/garns/lower_sqlite.py) |
| Constraints | Closed sets enforced; carrier invariants resolve; intent pattern/length are carried but unconsumed | Mixed implementation; [reference](../../docs/DSL_REFERENCE.md), [limitations](../../docs/LIMITATIONS.md) |
| Composition | Trait uses/links expand; conflicts and cycles checked | Implemented baseline; [resolver](../../src/garns/resolve.py) |
| Trait invariants | Invariant retained on trait but absent from consuming resource | Reproduced resolver defect below, not a language feature request |
| Cross-object invariants | Runtime checks the written carrier row after mint/change, not all affected dependent owners | Source inspection; [engine](../../src/garns/engine.py), method `_check_invariants`; no concurrent runtime proof here |
| World/targets | World includes semantic policies and generation targets; deployment selects engine and location | Existing grammar, mixed responsibility rather than absence |
| Values | Scalar intents, nominal newtypes, restricted type constructors; Opaque presence-only | Deliberate current restrictions, not a recursive document contract; [types](../../src/garns/types.py) |
| Modules | Named imports and aliases, qualified identity, acyclic import graph; no parameters | Implemented baseline plus genuine new design area; [reference](../../docs/DSL_REFERENCE.md) |
| Operations | Restricted/bulk/compound/alias IR validated; generated code iterates reads only | Explicitly unimplemented execution, not merely missing application declarations; [limitations](../../docs/LIMITATIONS.md) |
| Async/PostgreSQL | Accepted architecture and pure contracts are not production adapter proof | [W1 acceptance](../W1-ACCEPTANCE.md), [A2](../../docs/adr/A2-backend-contract.md) |

Paths in the final row are relative to this file: W1 acceptance is in the parent
developer-docs directory; ADRs live under the repository docs directory.

The current backend iteration deliberately preserved grammar and deferred full verb
execution and dormant declaration consumers. See
[the implementation plan](../GarnsV9-6-PostgresAsyncImplementationPlan.md) sections
on out-of-scope work and declaration completion. These are sequencing decisions,
not evidence that reusable constraints or operations are undesirable.

## Reproduced constraint propagation defect

Executed once with the existing parser/resolver, using an in-memory source string;
no database or source files were changed. The following is current GARNS syntax:

```garns
module trial "trait propagation probe" {
  intent lower : Integer "lower bound"
  intent upper : Integer "upper bound"
  trait Bounds "two bounds" {
    use lower
    use upper
    invariant lower <= upper
  }
  resource Window "bounded window" { carry Bounds }
}
world TEST "probe" {
  modules trial
  durability durable
  writers governed
  generated python
  scope deployment
  quarantine_retention 3
}
```

Observed resolved IR:

```text
trial.Bounds uses=2 invariants=1
trial.Window uses=2 invariants=0
```

`Resolver.resolve_carrier` copies uses/links; pending invariants contain only locally
declared predicates. `resolve_reads_and_invariants` does not add carried predicates.
The probe establishes missing IR propagation, not a measured database corruption.
All four bundle alternatives require this class of defect to be impossible or caught.

## Declarativity priorities

1. Make declarations trustworthy: consume enforced-looking constraints or refuse
   their unsupported use before effects. Adding syntax without consumers worsens this.
2. Let intent and composition rules retain their identity and invariants everywhere.
3. Specify allowed changes and atomic guards as data, not handwritten application checks.
4. Distinguish presence and values before choosing storage encodings.
5. Make generation/deployment choices visible without redefining domain meaning.
6. Preserve explainability as module specialization and derived effects grow.

Only the propagation probe was executed. No new runtime, generic-module compiler,
native database adapter, full suite or external language comparison was tested.
