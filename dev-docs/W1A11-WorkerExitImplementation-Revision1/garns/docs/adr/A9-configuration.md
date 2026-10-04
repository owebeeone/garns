# A9 — Deployment configuration and redaction

**Status: PROPOSED FOR REVIEW.** Depend on A3, A11, A13. Precedence is explicit
runtime trusted-host configuration > named environment values referenced by
`at env NAME` > authored deployment defaults; absent required values refuse.
Caller request data never supplies DSNs, authority, scope or capabilities.

Typed configuration includes backend, catalog/schema binding, pool min/max,
finite deadlines, read-only mode and secret references. Pool bounds default to
min 1/max 10; all timeouts must be explicitly materialized from documented
finite defaults. Secrets are resolved only at open, retained in a redacting
container, and excluded from repr, errors, logs, metrics and evidence.

Closure: W3/W4 publish the schema and hostile redaction tests; W7 ensures named
provider keys and external-capture keys refuse as unsupported.
