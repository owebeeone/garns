# Garns shared query planning design brief

**Status:** operator-authorized design and review only  
**Date:** 2026-10-03  
**Owner:** manager

The operator authorized a focused design for W2 after W1 architecture
acceptance. Produce one concrete, reviewable design for shared query planning,
compiler bridging and backend lowering. Do not implement it. No source,
contract, grammar, dependency, database/service or Git mutation is authorized.
The design itself must clear independent review before implementation begins.

## Accepted dependencies

Read workspace/product instructions and `CurrentProgramCheckpoint.md` first.
Read the full accepted implementation plan, provider-neutral amendment,
operator decisions, governed-write scope and their acceptance records. Later
additive records control their explicitly superseded historical clauses.

- W1 acceptance: `W1-ACCEPTANCE.md`, SHA-256
  `524175276f7de2fa44b11d0308aaef9d3ad7e1a869ab17cc0cd24b87dc60316d`.
- Complete W1 protocol/ADR/reference tuple:
  `W1-RegistryContainmentRedesign-MANIFEST-3.sha256`, SHA-256
  `95d4bef485bc5fb4dd19ffb29dc3a96ab4412ce96d2b93b7da873ce254107549`.
- Explicit accepted A2 dependency: `docs/adr/A2-backend-contract.md`, SHA-256
  `cf92142270bc706dbac320cfc448ab3b16e847b3ec3a2771cd711a0b0df3dac2`.
  Its draft header is superseded only by the additive W1 acceptance record.
- Frozen ownership: `docs/PRODUCT_LAYOUT.md`, SHA-256
  `b4211c5902e47f403fa8bccd15006b14a0737a8d4ac8c0e7691a7f52d7f6d971`.
- Qualified compiler IR: `src/garns/ir.py`, SHA-256
  `c9ff6977c10f4d583902678395422f3dc683b4e3b3d4248895f468481dbc3688`.
- Existing SQLite lowering: `src/garns/lower_sqlite.py`, SHA-256
  `ad8feac2496c51398f347c14ba7bf75340596ca40d63faedfe70d4bd260665ec`.
- Authored storage: `src/garns/storage.py`, SHA-256
  `bbea93fe9c1a1e0475cff4be9a65a0f364e42624fa908cadf3337d4cf4ce15b2`.
- Unchanged grammar: `grammar/garns.lark`, SHA-256
  `3a453f5ac7998dc6639593a9c01a1f0806b7b5f2b00afc8a8ed56e4db9f3d4e8`.

The W2 dependency is W1 plus explicitly accepted A2, not merely transitive W1.
Other accepted ADRs constrain authority, bindings, namespace, capability,
result, replay and generation integration; do not silently amend them.

## Exclusive draft ownership

One design owner may write only `dev-docs/W2-QueryPlanningDesign.md` with
apply_patch. Everything else is read-only; manager owns brief, manifests,
reports, remediation and acceptance. No competing draft, helper agent or
implementation. Return full draft testimony and stop writes for pinning.

Read the inherited compiler/type/function/read, storage, SQLite lowerer,
engine/live/footprint consumers and tests sufficiently to give exact source
references and an honest coverage inventory. Do not infer an implementation
from historical prose. Existing source remains read-only baseline evidence.

## Required concrete design

1. Specify immutable relational and result nodes, each field/invariant and
   their allowed composition. Account for every inherited Read, ShowTerm,
   Operand/Expr form, parameter/default/type dimension, cardinality, ordering,
   identity, optional/empty/grouped/windowed/nested/total/paged result behavior.
   Explicitly map current IR forms to nodes or an evidenced refusal; do not
   narrow inherited supported SQLite behavior to make the design easier.
2. Reuse the qualified semantic expression source without a second expression
   IR. Explain immutable detachment and how SQL lowerers consume the plan
   without parser nodes, resolved Read syntax, Loc data or compiler/backend
   dependency reversal. Account for function registry identity/semantics.
3. Concretely connect W2 nodes to W1 Plan/FrozenPlanRoot/ResultShape and origin:
   canonical encoding, version/digest verification, exact node registry and
   exhaustive consumers, decode/validate refusal, forged/mismatched root,
   binding/generation mismatch, stable diagnostic source attribution outside
   canonical meaning. No SQL, driver, scope claim or secret in the root.
4. One shared plan feeds one-shot query and question initial/refresh results.
   Query-only expressive features do not inherit question live restrictions.
   Only questions derive bounded footprints/routing/deltas. Explain how plan,
   recursive composition, footprint dependency and existing live consumers
   remain coupled without unrelated duplicated query semantics.
5. Define validation/capability/lowering/parameter-binding order and dependency
   direction. Preserve W1 runtime-owned authority: pure compiler validation
   cannot issue authority or replace effect/delivery checks. Static and dynamic
   unsupported nodes refuse explicitly before adapter I/O/effects, not fallback.
6. Describe SQLite lowering from the plan, safe identifiers and parameter
   binding, authored physical/storage/namespace provenance, deterministic
   root-first window/tie/rank/group/nested semantics. PostgreSQL lowerer is a
   future consumer, not SQLite SQL rewritten or a claimed implementation.
7. Name cohesive proposed files within existing W2-owned plan/plan_bridge/
   sqlite/lower and matching tests. Read split-files guidance; no broad
   relocation/refactor or ownership inference. Identify exact legacy call-site
   wiring needed outside W2 paths. Such writes require a reviewed explicit
   ownership amendment before implementation; a diagram is not authorization.
8. Give an ordered future implementation and falsifiable verification plan:
   exhaustive visitors/node-addition failure, bad-encoding/type/root attacks,
   SQLite differential rows/cardinality/refusals, shared-plan equivalence,
   rename metamorphisms, SQL identifier/parameter hostility, question footprint/
   scope/group/composition/window/delta/fold/neutral parity and dependency tests.
   State what tests/measurements cannot prove. Existing SQL/result evidence is
   a comparison baseline, not a fixture-dispatch implementation or sole detector.

Keep the design focused and implementable; use exact source citations and
compact tables where mappings are useful. Distinguish decisions from future
test obligations. Surface ambiguity requiring changed scope/contract rather
than silently resolve it through unauthorized work. Do not self-accept.

## Deferrals and gate

Pure compiler operations remain synchronous. Async runtime and real workers
are W3; PostgreSQL execution/real-server parity W4 and later. External capture,
cryptographic/provider integration, ORM/verb expansion, grammar redesign and
public API names/Surface remain out of this design's implementation scope.
Retain unenforced. W1 Code P3 stays assigned to W3, not this design repair.

Manager pins design plus this controlling brief and exact read-only inputs.
Review-loop skill requires two independent peer-blind document reviewers:
Consistency and Safety, operator-selected 5.6 Sol. All P0/P1/P2 block; reports
filed verbatim. One consolidated correction per round, at most two architecture
remediations, fresh reviewers after material change and originating closure.
User-facing API/grammar is not frozen here; W3 Surface remains mandatory.

SHA-pinned design review uses the accepted plan's no-Git exception and claims
no clean commit/landing. GO/GO accepts the design only. The manager records
acceptance and implementation launch requirements separately; this authority
does not launch the W2 implementation builder or modify accepted W1 bytes.
