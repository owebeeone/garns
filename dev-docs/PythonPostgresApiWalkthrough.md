# Python database API walkthrough

**Status:** proposed user-facing surface for separate cold review; not executable.
**Scope:** Python static reads, governed writes and schema management.

The compiler defines the schema and reads; the runtime opens an existing store.
There is no synchronous database API and no general raw-SQL entry point.

## Prepare and provision

1. Author GARNS sources and explicit physical storage binding.
2. Call `compile_database(sources, binding)` to validate and prepare artifacts.
3. An administrator creates the database and provisions trusted-host credentials.
4. Open `Provisioner` using `await Provisioner.open(prepared, host=privileged_host)`.
5. Use `await provisioner.inspect(context=context)` to inspect the namespace.
6. Use `await provisioner.ship(context=context)` to install into an empty owned
   namespace or verify an exactly matching installation. It does not drop/rebuild.
7. Always call `await provisioner.aclose()` and inspect its close outcome.

Host configuration and trusted contexts come from the host integration, not
user request dictionaries. Credentials never appear in prepared artifacts.
Configuration defaults: pool 1-10 connections; acquire 10 seconds, statement
30, commit 30, cleanup 10, shutdown 30, migration lock 30. All limits are finite
and overridable by trusted configuration. Operation deadlines cap attempts;
cleanup has its separate bounded budget.

## Read and write

Open with `await Runtime.open(prepared, host=host_config)`; open validates schema
and generation but does not install or repair them. Execute a qualified read:
`await runtime.execute(read_qid, parameters, context=context)`.
The result is detached typed data, not a cursor or connection.

For a write, begin with a caller-supplied stable qualified transaction identity:
`tx = await runtime.begin(identity, context=context)`.
Call `await tx.mutate(mutation)` for typed insert/update/delete operations.
Call `await tx.commit()` explicitly and inspect its outcome; merely reaching
the end of a Python block does not commit. On failure before commit, request
`await tx.rollback()` and inspect that outcome too. A context manager does not
silently turn failed cleanup into success. Nesting and sharing the transaction
with another task are unsupported. No savepoints are exposed.

## Know whether it committed

Commit/rollback knowledge is KNOWN_COMMITTED, KNOWN_ABORTED or INDETERMINATE.
Only known commit carries its durable revision. Cancellation, timeouts and
connection loss are not evidence of rollback. If uncertain, preserve identity
and call `await runtime.reconcile(identity, context=context)`; if still uncertain,
retain the obligation for later recovery. Do not resend under a new identity.
Repeating the same committed identity and payload returns the old result;
a different payload under that identity refuses.

Automatic transaction retry is off by default (one attempt). Future explicitly
retry-safe whole-transaction callbacks can request up to three total attempts;
statement/commit retries are never enabled individually. Such callbacks cannot
make an external file write or network call atomic with a database transaction.

## Close and evolve

Always use `await runtime.aclose()`, including after failures. CLOSED means
quiescent and no unresolved work; UNRESOLVED names uncertain transactions;
NONQUIESCENT retains owned work still running. The host must keep recovery and
containment ownership for nonclosed outcomes. A second close is safe, not proof
that the first close finished. No implicit finalizer replaces this obligation.

For schema evolution, compile a next-generation artifact, obtain an explicit
migration request against the expected previous generation, open the privileged
Provisioner and call `await provisioner.migrate(request, context=context)`.
Migration serializes and drains the whole deployment; it is not an ordinary
runtime close. Unsupported or destructive transformations refuse before effect.
If a metadata-only change is supported, it publishes the next generation without
pretending data effects occurred. Accounted data changes need their classified
transaction path. There is no automatic reverse migration or data-loss undo:
request rollback before commit; after commit, an explicit compensating governed
transaction is a new recorded operation. Uninstall/drop is an administrator
operation, not an accidental mirror of `ship`.

## Availability

These names are proposals until Surface and architecture review accept them.
Live subscriptions, Rust surfaces, arbitrary SQL, external writes/capture,
automatic deployment activation and nested transactions are not in this slice.
Unsupported capabilities refuse explicitly; they do not fall back silently.
