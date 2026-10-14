# GARNS Design Option Index

Status: design exploration, not accepted language syntax or working compiler support.
Every code block in this directory is illustrative unless labelled current GARNS.

| Area | Four alternatives |
| --- | --- |
| [Relationships](Relationships.md) | R1 inline policies; R2 named relationships; R3 relationship contracts; R4 integrity rules |
| [Value constraints](ValueConstraints.md) | C1 intent invariants; C2 refined types; C3 predicate contracts; C4 constraint theories |
| [Intent bundles](IntentBundles.md) | B1 traits; B2 typed expansion bundles; B3 module exports; B4 companion rules |
| [World and targets](WorldAndTargets.md) | T1 separate declarations; T2 world sections; T3 reusable profiles; T4 target applications |
| [Document values](DocumentValues.md) | V1 document scalar; V2 structural values; V3 format contracts; V4 explicit value graph |
| [Parameterized modules](ParameterizedModules.md) | M1 specialization; M2 module signatures; M3 constrained inclusion; M4 explicit linking |
| [Mutation contracts](MutationContracts.md) | O1 bounded compounds; O2 effect contracts; O3 state transitions; O4 desired-state reconciliation |

Read [the combined comparison](../LanguageDesignExploration.md) after the individual
areas. [Baseline](Baseline.md) separates existing behavior from proposed changes.
[Examples](examples/README.md) compares the same model under four combinations.

## Reading the assessments

The three declarativity gates are explicit ordering, inspectable descriptions and
meaningful engine derivation. `P/P/P` means all three have a specified design argument,
not measured compiler conformance. Every option below has that projected gate result
under its stated restrictions. An implementation violating those restrictions would
lose that classification. The entries are intentionally not assigned numerical scores.

Correctness remains unproved for all new designs. Each file names refusal examples
and decision procedures that a future compiler/runtime must implement. The common
operation laws and evaluator provenance are recorded in the combined comparison.

Costs are relative design judgments: low, medium, high or very high compared with
the existing implementation. They are not time estimates. No option is free merely
because its spelling resembles current GARNS.
