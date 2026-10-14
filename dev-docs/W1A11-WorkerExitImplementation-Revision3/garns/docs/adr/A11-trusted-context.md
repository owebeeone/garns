# A11 — Provider-neutral trusted execution context

**Status: PROPOSED FOR REVIEW.** Depend on A3, A7. A runtime-owned issuer
registry creates an immutable opaque `TrustedContext` that is only an empty,
exact-instance identity handle. It contains no claims, identifiers, issuer or
registry back-reference. The issuer registry alone retains detached normalized
principal, writer, qualified allowed scope, capabilities, context identity,
validity deadline, host invalidation epoch and the genuine current runtime-task
object. The handle is non-serializable, generically represented,
and valid only for the issuing runtime/owner. Structural copies, mutation,
cross-tenant substitution and caller overrides confer no authority. Validation
requires the exact live registered instance. Copy, reconstruction, dataclass
conversion, reinitialization and serialization refuse. Traversing caller-visible
handle attributes, slots and diagnostic representations reaches no claim data.
Claims are defensively detached and normalized in the trusted registry, and an
unregistered reconstruction or a handle presented to another issuer refuses.

One runtime-owned authority supplies monotonic time, current host epoch and
current task identity from providers injected only at trusted setup. Ordinary
open, pool acquire/release, execute, snapshot, transaction, mutation, migration
and ledger replay carry only the opaque context; callers cannot submit time,
epoch or owner values. Raw binding open is separately named trusted-host-only.

Subscription itself is not iterable. It creates one concrete authority-bound
iterator from a context; every `__anext__` validates immediately before reading
and again after any awaited read before returning rows. Expiry, invalidation,
wrong/child task, exact-context invalidation or close during the await refuses
or terminates without delivery. Renewal closes the old iterator and creates a
new binding; it never mutates or silently rebinds stale iteration. There is no
parallel authority-free delivery method.

Validity is checked at entry, before every database effect, before commit
request and before each subscription delivery. Maximum staleness is zero at
those boundaries, not continuously. Expiry before commit rolls back/refuses;
after commit request it preserves A7 knowledge and reconciliation. Renewal is a
new identity. Reconciliation authority permits only observation and idempotent
cleanup of the original transaction, never new effects.

Raw tokens, sessions, provider objects and cryptography remain outside Garns.
No named-provider configuration exists. Closure: W3 counterfeit, owner race,
expiry and canary-disclosure tests; W7 scans all outputs. Public issuance names
remain for W3 Surface review.
