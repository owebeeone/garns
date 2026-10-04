# Garns v9-6 — provider-neutral seam amendment

**Status:** draft for dual peer-blind review  
**Operator decision:** v9-6 uses a provider-neutral authentication seam; named
identity-provider integration is deferred  
**Amends:**
[`GarnsV9-6-PostgresAsyncImplementationPlan.md`](GarnsV9-6-PostgresAsyncImplementationPlan.md)
at SHA-256
`11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512`  
**Review trigger:** final Consistency finding P2-1 and bounded dependency finding
P2-2 in
[`ReviewConsistency-3`](GarnsV9-6-PostgresAsyncImplementationPlan-ReviewConsistency-3.md)  
**Date:** 2026-10-03

## 1. Scope and effect

This amendment creates a new review object after the parent plan exhausted its
architectural remediation allowance. It does not reopen or erase the parent
review history. Once this amendment receives same-tuple Consistency/Safety
`GO`/`GO`, the effective implementation plan is:

1. the parent plan at the exact digest above; plus
2. the replacements and clarifications in this amendment.

Where the two documents conflict, this amendment controls only the clauses it
explicitly supersedes. All other parent-plan requirements remain binding.

This amendment:

- closes D7 to a provider-neutral seam for v9-6;
- keeps production identity-provider implementation outside v9-6;
- prevents a named provider from being selected through an operator record
  without a separately reviewed implementation branch;
- makes W2, W7 and W8 ADR dependencies mechanically auditable; and
- extends the trusted-context contract with issuance, lifetime and disclosure
  rules and extends capture attribution/authorization at the A11/A14 seam; and
- otherwise does not change the grammar, `query`/`question` split, `unenforced`,
  qualified identity, storage provenance, async-only runtime direction,
  PostgreSQL-first direction, transaction outcomes, live semantics, capture
  durability/idempotency algorithms or any capture behavior outside that seam.

## 2. Binding provider-neutral seam decision

For v9-6, authentication ends at one provider-neutral trusted execution-context
boundary:

- The host application authenticates through a mechanism outside Garns.
- A trusted-host-only adapter issues or resolves a Garns context capability.
  Ordinary public callers cannot construct one from request data. A11 must
  choose and test an enforceable provider-neutral issuance mechanism; structural
  resemblance to the context's claims is never sufficient authority.
- Garns receives only an immutable, request-bound snapshot of normalized claims:
  opaque principal identity, allowed scope, capabilities, writer/audit identity,
  context identity, validity deadline and host invalidation state. Garns never
  receives the provider assertion from which the host derived those claims.
- The context capability is bound to its runtime/request ownership domain.
  Substitution across concurrent tenants, public construction, cloning with
  altered claims and post-issuance mutation refuse before effect.
- Public execute, transaction, capture and subscription operations derive or
  constrain scope, capabilities and writer identity through that context.
- A raw assertion-taking entry point, if retained, is internal or explicitly
  trusted-host-only, separately named, non-public by default and unreachable
  through the ordinary API.
- Garns v9-6 does not select, configure, call, validate tokens/sessions for, or
  implement lifecycle/revocation behavior for any named identity provider.
- Raw provider tokens, cookies, sessions, assertions, provider-specific claim
  objects and secrets remain entirely on the trusted-host side. The normalized
  Garns context has a redacted representation, is not generally serializable,
  and cannot expose those values through fields or callbacks.
- Provider credentials and raw assertions do not enter Garns-owned runtime
  objects, IR, generated artifacts, deployment declarations, configuration,
  exceptions, diagnostics, logs, traces, observability, fixtures, snapshots or
  evidence bundles.

### Context validity and invalidation

A11 defines one provider-neutral validity grammar independent of any identity
provider:

- every context has an immutable validity deadline and a host-controlled
  invalidation handle or epoch;
- Garns checks validity at runtime entry, before each database effect, before a
  commit request, before subscription delivery, before capture claim and before
  capture acknowledgement;
- the maximum stale interval is zero at those check boundaries; Garns does not
  promise continuous revocation between them;
- expiry/invalidation before a commit request causes typed refusal and rollback;
  invalidation after a commit request does not imply rollback and preserves the
  known-abort/known-commit/indeterminate contract and reconciliation path;
- an invalid subscription terminates with a typed authorization-expired outcome
  and bounded cleanup before another batch;
- an invalid capture context stops acquisition; an owned unacknowledged event is
  released or reconciled without acknowledgement unless its Garns revision is
  already known committed; and
- renewal produces a new context identity and never mutates an existing
  context in place.

### Capture actor model

Governed writes and externally captured writes have different actor sources:

- a governed write derives its writer/audit identity from its valid A11 context;
- an external event carries durable source-actor provenance derived by the
  selected A5 branch and mapped under the supported A14 role/RLS contract;
- the capture worker/service identity comes from its own A11 context and is
  recorded separately from the source actor when processor attribution is
  retained;
- a capture-administration context may authorize configuration or operation but
  cannot replace either the source actor or processor identity on an event;
- a capture caller cannot override source attribution; and
- missing, ambiguous or contradictory required source provenance refuses before
  acknowledgement.

A future named-provider integration requires a separately reviewed change
request with its own scope, owned paths, configuration/secrets contract,
lifecycle and outage/revocation states, security tests, documentation, release
gates and review tuple. It cannot be enabled by changing D7 or A11 alone.

## 3. Exact D7 replacement

The parent plan's D7 row is superseded in full by:

| ID | Decision and permitted outcomes | Status / owner | Pre-launch decision artifact | Dependants and due-before boundary | Later implementation / verification artifact |
|---|---|---|---|---|---|
| D7 | Authentication scope for v9-6: provider-neutral seam only; named-provider integration is not an admitted v9-6 outcome | Binding/closed: seam-only; operator | this accepted amendment | W1 A11 and W3; before A11 is accepted and W1 hands off | A11, W3 hostile-claim tests and P2; future provider work requires a separate reviewed change request |

The parent plan's statement that production authentication/identity-provider
implementation is out of scope is therefore unconditional for v9-6 rather than
an outcome D7 can promote inside this milestone.

## 4. Exact dependency corrections

The following parent-plan dependency clauses are superseded:

### W2

Replace:

> Dependencies: W1.

with:

> Dependencies: W1 and accepted A2.

A W2 builder prompt must name the exact accepted A2 artifact and W1 protocol
tuple; transitive reference to W1 alone is insufficient.

### W7

Replace:

> Dependencies: W0–W6.

with:

> Dependencies: accepted W0–W6 output tuples and the accepted A1–A15 release
> decision tuple.

The W7 launch check constructs its ADR tuple directly and refuses any missing,
superseded or contradictory release-relevant ADR.

### W8

Append to W8:

> Every W8 change request must enumerate the accepted ADRs it retains,
> supersedes or does not affect. Its builder prompt names those exact artifacts;
> it may not infer ADR dependencies transitively from the v9-6 release.

### W6

Replace the parent W6 dependency clause with:

> Dependencies: W4–W5 and accepted ADRs A4–A5, A11 and A12–A15. A5 must
> be closed to one branch before W6 implementation is assigned.

Append these W6 deliverables and exit criteria:

- durable source-actor provenance for the selected capture branch;
- separate source-actor, capture-processor and capture-administrator identities;
- A14 mapping from supported database role/session provenance to Garns
  writer/audit identity; and
- refusal before acknowledgement for missing, ambiguous, contradictory or
  caller-overridden source attribution.
- host-issued A11 capability verification on capture administration,
  acquisition, claim, revision creation, reconciliation and acknowledgement;
- refusal before each capture effect for a public structural copy,
  post-issuance mutation, cross-request/tenant substitution or counterfeit
  processor/administrator context; and
- proof that the known-committed reconciliation exception performs only the
  idempotent cleanup already authorized by the genuine committed operation. An
  invalid or counterfeit caller cannot use that exception to authorize a new
  claim, revision, administrative mutation or acknowledgement.

Two supported external roles processed by one service context must retain
distinct source attribution. A spoofed service/admin context cannot overwrite
the source actor. For one genuine external event, W6 must attempt every capture
operation with a structural copy, mutated once-genuine context, concurrent
tenant substitution, forged processor and forged administrator context. Each
counterfeit case refuses before acquisition, claim, revision, reconciliation,
administrative mutation or acknowledgement; only a genuine request-bound
context may reach the existing known-commit/idempotent reconciliation path.

## 5. Executable provider-neutral seam gates

The following requirements extend the named parent-plan packages and gates.

### W3 additions

W3 exit criteria additionally require:

- counterfeit contexts constructed through ordinary/public paths, altered
  structural copies, post-issuance mutation and concurrent-tenant substitution
  refuse before effect across execute, transaction and subscription;
- context expiry/invalidation is tested at every validity boundary, including
  before transaction entry/write/commit and before subscription delivery;
- only the normalized immutable claim envelope enters Garns; its representation
  is redacted and its raw provider source is neither accessible nor serializable;
- no named-provider SDK, token/session validator, issuer/JWKS/session
  configuration, provider-specific runtime branch or provider-specific test
  exists in W3 product paths; and
- provider-integration configuration keys refuse as unsupported rather than
  enabling a dormant path.

### P2 extension

P2 Async honesty and trust also requires executable proof of context provenance,
immutability, request binding, validity/invalidation, minimum disclosure and
absence of named-provider runtime/configuration surfaces. Passing only
conflicting-claim tests is insufficient.

### Verification-matrix additions

| Capability | Pure compiler | SQLite async | PostgreSQL | Concurrent PostgreSQL |
|---|---:|---:|---:|---:|
| Context provenance/immutability | contract/refusal derivation | counterfeit/mutation tests | counterfeit/mutation tests | tenant-substitution races |
| Context validity/invalidation | contract/outcome derivation | entry/effect/commit/subscription barriers | entry/effect/commit/subscription/capture barriers | invalidation races and commit reconciliation |
| Secret/assertion minimization | no secret-bearing IR/products | canary scan of success/failure outputs | canary scan of success/failure/capture outputs | trace/evidence scan under failures |
| Capture actor attribution | typed actor derivation | optional parity | source/processor/admin separation | multi-role events under one processor |
| Capture context provenance | contract/refusal derivation | optional parity | W6 counterfeit/mutation tests at admin/acquire/claim/revision/reconcile/ack | tenant-substitution races and known-commit cleanup |
| Named-provider absence | dependency/configuration schema check | unsupported-key refusal | unsupported-key refusal | — |

### W7 additions

W7 inventories runtime dependencies, configuration keys, generated/deployment
schemas, product source/tests and evidence outputs. Release refuses if it finds a
named-provider SDK, token/session validator, issuer/JWKS/session configuration,
dormant provider switch or provider-specific runtime/test path not introduced by
a separately accepted provider package.

W7 also consumes the W6 capture-context provenance evidence. P2 cannot close
from W3 context tests alone: the release tuple must show W6 refusal evidence for
every capture operation and show that no counterfeit or invalid context used
known-commit reconciliation to authorize a new acknowledgement or other effect.

Canary tokens, cookies, sessions and provider-specific fields are seeded through
the trusted-host adapter while success and failure paths exercise execute,
transaction, capture and subscription. W7 must prove that no canary appears in
Garns-owned objects, IR, generated or deployment output, configuration,
exceptions, diagnostics, logs, traces, observability, fixtures, snapshots or
evidence. The configuration schema must reject provider-integration keys.

## 6. Effective decision and dependency graph

The effective pre-implementation order is:

```text
closed D1, D2, D3 and D7
        +
open D6a and D8 close
        │
        ▼
       W0
        │
        ├── open D4, D5 and D6b close
        ▼
       W1 accepts A1–A15, including seam-only A11
        │
        ▼
W2 + A2 → W3 + A1–A4/A6–A8/A11 → W4 → W5 → W6 + A11
        │
        ▼
W7 + accepted A1–A15 release tuple
        │
        ▼
W8 only through a separately reviewed, explicit ADR-dependency request
```

Plan-document acceptance does not itself close D4, D5, D6a, D6b or D8. No
builder prompt is authorized until the decisions required by that package have
their named pre-launch artifacts.

## 7. Closure tests

The amendment is acceptable only if reviewers can establish all of the
following:

1. The seam-only D7 path completes W1–W7 without any named-provider code,
   credentials, configuration, lifecycle or tests, and W3/W7 executable gates
   reject synthetic provider code or config-only enablement.
2. Selecting a named provider is impossible inside the v9-6 decision graph; it
   requires a new reviewed change request and package.
3. A11 freezes a provider-neutral trust handoff before W3: ordinary callers
   cannot counterfeit, mutate or substitute contexts, and both direct hostile
   claims and counterfeit contexts are tested.
4. An ADR/package matrix built from explicit dependency clauses identifies A2
   for W2, accepted A1–A15 for W7 and request-selected ADRs for W8 without
   relying on transitive inference.
5. The effective parent-plus-amendment graph topologically sorts and does not
   reopen any prior P0/P1/P2 finding.
6. Expiry/invalidation at each stated barrier creates no new unauthorized
   effect or delivery and preserves indeterminate-commit reconciliation.
7. Canary provider assertions/secrets never cross the normalized seam or appear
   in any Garns-owned object or output.
8. Two external source roles processed by one capture service retain distinct
   source attribution; ambiguous or spoofed attribution refuses before
   acknowledgement.
9. W6 rejects structural copies, mutated contexts, tenant substitution and
   forged processor/administrator contexts before every capture effect, while a
   genuine context preserves source attribution and idempotent known-commit
   reconciliation. W7 consumes this evidence rather than inferring it from W3.
10. The amendment does not silently change any frozen v9-5 language or semantic
   rule.

The current document review proves that these requirements are complete,
ordered and falsifiable. W3/W6/W7 implementation reviews prove their executable
outcomes on shipped bytes; document acceptance alone never claims those future
tests have already passed.

## 8. Review and acceptance

This amendment is a document/scope decision and receives fresh peer-blind
Consistency and Safety review against the exact two-document tuple. Acceptance
requires both reports to say `GO` on the same parent-plan and amendment digests,
with no unresolved P0/P1/P2.

Exact public API names remain an A3/A11/W3 implementation decision, so this
amendment does not freeze a new user-facing surface and does not independently
trigger Surface review. The later public API freeze still requires the Surface
review mandated by the parent plan.

After GO/GO, the lane owner records acceptance in a separate synthesis document.
The parent plan remains immutable historical evidence; builders receive the
parent plan, this accepted amendment, the acceptance synthesis and the exact
decision/ADR artifacts required by their package.
