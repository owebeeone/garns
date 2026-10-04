# Garns v9-6 operator decisions — D6a, D7 and D8

**Status:** binding/closed  
**Decision date:** 2026-10-03  
**Authority:** operator  
**Recorded by:** manager

## Governing reviewed tuple

These decisions are additive launch artifacts for the already accepted plan
tuple. They do not modify or replace the hash-pinned historical documents.

| Document | SHA-256 |
|---|---|
| `GarnsV9-6-PostgresAsyncImplementationPlan.md` | `11268a05330b993555f9b8d172f2aa89d882482c4fa73a921ff3fdaba3d7e512` |
| `GarnsV9-6-ProviderNeutralSeamAmendment.md` | `b99c43b50f5fe7a6ace8d5803ea0434d436b144041b996c7a754e8d88178cd01` |

The accepted amendment remains controlling wherever it strengthens the D7
seam, lifecycle, provenance or verification obligations below.

## D6a — supported Python range

**Decision:** Garns v9-6 supports CPython 3.11 and above.

- Package metadata must declare `requires-python = ">=3.11"` with no upper
  bound.
- The release matrix must test every stable CPython minor from 3.11 through
  the current stable release at the time of that Garns release.
- The initial W0 matrix must include 3.11, 3.12, 3.13 and 3.14. If a later
  minor is stable when W0 or W7 executes, it is added before that package may
  make a compatibility claim.
- A missing local interpreter is a provisioning task, not authority to narrow
  the declared range or skip its clean-environment evidence.
- Alternative Python implementations are unclaimed unless a later reviewed
  decision adds them.

This record is the signed Python support-range artifact required by D6a.

## D7 — in-process provider-neutral trust seam

**Decision:** Garns v9-6 implements an in-process, provider-neutral trusted
execution context. The host process is the security boundary. Authentication
of external processes and cryptographic credentials belongs to a separate
library or service adapter.

The boundary is:

```text
external credential or session
        |
        v
separate authentication library/service
        |  verifies signature, issuer, expiry and provider claims
        v
trusted in-process Garns context
        |
        v
Garns runtime
```

Binding consequences:

- Garns core does not accept raw provider tokens, serialized execution
  contexts or network authentication requests.
- Garns core does not perform provider discovery, key retrieval, signature
  verification, login, refresh or session management.
- A trusted host integration issues or resolves the in-process context through
  the privileged boundary frozen by A3/A11/W3. Public request data and ordinary
  database APIs cannot mint authority.
- The context carries immutable, request-bound normalized identity, scope,
  capability, writer, provenance and validity information required by the
  accepted amendment. Exact fields and lifecycle calls remain A3/A11/W3
  decisions.
- Execute, transaction, subscription and capture entry points derive authority
  from that context. Caller-supplied values cannot widen or replace it.
- Counterfeit, expired, invalidated, missing or conflicting authority refuses
  before effect at the boundaries required by the accepted amendment.
- A future cryptographic adapter may validate an external credential and issue
  a local context, but it is a separate, reviewed package. No named identity
  provider is part of v9-6.
- The design does not claim that Python objects protect against malicious code
  already executing inside the trusted host process. That process is trusted
  by definition.

This record is the signed seam-only artifact required by D7. It narrows the
deployment boundary without weakening the accepted provider-neutral contract.

## D8 — one convergent implementation

**Decision:** Garns v9-6 has one canonical product implementation. Multiple
builders may contribute concurrently only through frozen interfaces and
non-overlapping write ownership; there are no competing whole-product builds.

### Root allocation

| Purpose | Allocated root | Rule |
|---|---|---|
| Canonical v9-6 product | `/Volumes/projects/limbo/datascad/garns-v9-6/` | The only product root; create and register it through `gwz`, never by editing `gwz.conf/` |
| Ratified v9-5 input and evidence | `/Volumes/projects/limbo/datascad/garns-v9-5/` | Read-only during W0 and all later v9-6 work |
| API research | `garns-v9-6/research/api-docs/` | Non-mergeable research handed to the W3 owner |
| PostgreSQL codec research | `garns-v9-6/research/postgres-codecs/` | Non-mergeable research handed to the W4 owner |
| Capture research | `garns-v9-6/research/capture/` | Non-mergeable research handed to the W6 owner |
| PostgreSQL service tooling | `garns-v9-6/tools/postgres/` and `garns-v9-6/tests/support/postgres/` | Product-support tooling owned by the admitted A10 sub-lane |

W0 alone may write the entire new product root while materializing the layout.
After W0, the package and sub-lane boundaries in section 8 of the accepted
plan govern. In particular, the shared plan, public API, transaction, revision
and replay protocols each have one writer and one manager/integration owner.

Independent reviewers attack the same integrated bytes. Because no competing
whole builds exist, there is no whole-build comparison or selection gate.

This record is the signed delivery-shape and concrete root-allocation artifact
required by D8.

## Launch-state effect

| Decision | Result |
|---|---|
| D6a | **Binding/closed** — Python `>=3.11` |
| D7 | **Binding/closed** — in-process provider-neutral seam only |
| D8 | **Binding/closed** — one convergent implementation |

D6a and D8 no longer block W0. D7 no longer blocks A11, although A11 must
still freeze the exact trusted-context protocol and pass the accepted review
gates. D4, D5 and D6b remain open and must close before W1 hands off its
accepted A1–A15 tuple.
