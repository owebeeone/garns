# Garns Vision and Design Decision Principles

Status: working draft capturing the operator discussion of 15 October 2026. A reference for design decisions; not an accepted language specification or implementation authorization.

## Purpose

Garns should let an author describe application data meaning, guarantees and permitted interactions, while the system derives the machinery needed to realize them. Applications should interact through domain operations and live results without reconstructing storage layouts, query plans or transaction protocols.

The central design question is: **How much work can Garns derive from a domain declaration without requiring the author to anticipate its realization?**

This vision guides the reconsideration of the DSL and the method used to design it. Existing implementation discoveries are evidence to learn from. Accepted internal contracts constrain work in their scope, but do not establish that the current language organization is the best possible one.

## Declarativity and useful omission

A declaration should state the distinguishing intent and allow the engine to derive the rest under defined rules. Brevity matters when it removes redundant decisions and wiring while preserving understandable meaning. Short spelling alone is not the objective.

**Explicit connection rules do not require explicit enumeration of every connection.** The language defines how elements can connect; an author supplies the intent, constraints and context needed for the engine to derive the applicable connections. Those rules may belong to the language, a reusable declaration or a declared assembly policy. They need not be repeated at every use.

Context, composition and generation may determine both which elements connect and how the connection is realized. A reusable declaration can therefore leave these decisions open until the relevant context is known. Requiring concrete wiring earlier can reduce its expressive power: the author must supply decisions that the engine could otherwise derive, and one declaration can no longer adapt across the same range of contexts.

For example, using a bounds bundle should introduce its companion values and preserve their shared ordering constraint. The author should not have to restate the fields and law at every use. The engine must retain their origin and explain the resolved result.

As a conceptual example, a reusable module could require a revision source without naming a concrete provider. A declared assembly rule could bind that requirement to a compatible provider in the selected world during generation. The same module could then be used in different worlds with different providers, preserving the required contract. The author declares the requirement and any necessary selection constraints; the engine derives the individual binding. This illustrates a design capability to evaluate, not accepted Garns syntax or implemented behavior.

The derived connections must be inspectable, with an explanation of the rules and context that produced them. Inspectability is an obligation on the engine's output, not a requirement for the author to enumerate that output in the source. Where the rules do not determine an admissible result, the engine must report the unresolved choice or apply a selection procedure defined by the contract; it must not guess silently.

Contextual interpretation must itself have defined semantics. A declared context may select a different binding or realization; accidental import order or an undocumented generator choice must not determine meaning. Domain guarantees remain binding unless the model explicitly declares a semantic variation.

## What authors should be able to rely on

Reusable declarations carry their guarantees through use, composition and specialization. Qualified identity, constraints and dependency closure survive even when a dependency is not exposed as a local name.

Authors can inspect what the engine derived and why, including the declaration and use sites responsible for a field, constraint, connection or effect. Explainability supports rich derivation rather than requiring authors to write out the resolved program.

Values, identity, presence, relationships and permitted changes have meanings independent of a particular storage engine. Operations preserve declared authority, atomicity and final-state guarantees. Live results reflect committed changes according to their declared contract. Evolution accounts for the continuity of data and declarations across generations.

## Backend independence with semantic fidelity

Backend independence means preserving observable guarantees through supported realizations. It does not promise that every backend can implement every declaration.

An explicit physical binding separates domain identity from physical representation. Adapter algorithms and capabilities must supply the execution guarantees; a mapping file alone cannot supply concurrency, atomicity or live-delivery semantics.

Alternative representations, including embedded documents, are valid only when they preserve required identity, sharing, references, updates and evolution behavior. Unsupported combinations must refuse at the earliest meaningful boundary rather than approximate silently.

PostgreSQL remains the primary production direction and SQLite a supported secondary runtime under existing scope decisions. Additional backends are future design possibilities. This vision makes no new implementation or portability claim.

## LLM authoring as a design objective

Garns should support reliable LLM authoring through precise semantics, discoverable contracts, useful diagnostics and inspectable derivation. This does not require every declaration or connection to be flat, local or fully expanded.

Claims that one syntax improves LLM accuracy require comparable authoring tasks and evidence. Evaluate semantic mistakes, omitted requirements, repair effort and context cost as well as successful parsing. No syntax guarantees correct definitions on the first attempt.

## How to make design decisions

Begin with representative complete scenarios: the application's intended outcome, the minimum information the author should provide, the work the engine should derive and the guarantees the result must preserve. Include counterexamples and evolution scenarios early.

Define domain meaning and permissible contextual variation before freezing an IR representation. Develop candidate representations and surface forms together, using complete scenarios to expose missing concepts. Equivalent resolved outputs do not imply equivalent authoring burden or reuse.

For each candidate, follow its consequences through static semantics and identity, physical realization, live dependencies, authority and concurrency, and evolution. Revisit earlier choices when these interactions reveal a defect; dependency ordering is a guide, not a reason to close foundational questions prematurely.

Use the Declarative API Evaluator to distinguish gap richness, generativity and correctness. Preserve its evidence requirements and distinction between design-stage projections and measured outcomes. A feature that avoids errors by excluding legitimate needs has a coverage cost. Correctness alone does not establish useful declarativity, and greater derivation alone does not establish a better design.

Compare surviving alternatives across these dimensions and declared floors rather than choosing solely for explicitness, brevity or resemblance to an existing language.

## Questions at a decision point

1. What legitimate intent does this choice let the author express?
2. What must the author state, and what can the engine derive?
3. Does the choice unnecessarily require individual connections or fix their realization before the relevant context is known?
4. Are the connection rules and selection procedures defined, and can the engine explain each derived connection without requiring it to be handwritten?
5. Do composition and specialization preserve identity and guarantees?
6. What are the consequences for storage, live results, concurrency and evolution?
7. Which misuse is prevented or detected, and which valid intent is excluded?
8. What evidence supports the claimed benefit, and what remains projected?

## Decisions that remain open

This vision does not select a whole-language candidate, a taxonomy of declaration tiers, a module mechanism, an operation notation or an IR layout. It does not decide whether Garns needs separate dialects, components or products. Any separation should follow demonstrated differences in meaning or responsibilities.

The provisional preference for Candidate B in the existing exploration remains a proposal to reassess against these principles, particularly its treatment of contextual derivation and author-specified wiring.

## Related design records

- [Language design exploration](LanguageDesignExploration.md)
- [Language change register](LanguageChangeRegister.md)
- [Baseline audit](language-design-options/Baseline.md)
- [Current program checkpoint](CurrentProgramCheckpoint.md)
- [Product direction](../docs/GARNS_DIRECTION.md)

The concept taxonomy and subsequent method proposals supplied during the discussion are working inputs, not accepted decisions.
