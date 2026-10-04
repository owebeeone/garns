# Garns external write capture future project

**Status:** deferred project brief, not a launch authorization  
**Date:** 2026-10-03

This future project would let supported applications and tools modify
Garns-bound data outside the Garns runtime while keeping its revision history
and live questions correct. It is explicitly not a dependency of the v9-6
PostgreSQL and async runtime release.

## Purpose and boundary

Examples include another service, an import job or direct SQL changing a
bound table. A static query can read committed data on its next execution;
a live question needs reliable knowledge of what changed. Existing
subscriptions, replay and writer attribution cannot be assumed correct merely
because a later fetch sees the new rows.

The project is change capture and integration, not another authentication
provider or an automatic guarantee that arbitrary SQL obeys Garns intents.
Its supported writers, operations, permissions and validation policy must be
explicit. Database administrators who can disable protections are not
automatically covered by that policy.

## Candidate capture mechanisms

**Trigger-maintained change table:** database triggers record changes durably
in the originating transaction. An async consumer processes committed records.
This needs installation, coverage checks, write-overhead measurement and
cleanup. Notifications may wake the consumer but are not its durable evidence.

**Logical decoding:** consume PostgreSQL changes through its logical
replication machinery. This avoids per-table capture triggers but needs
replication configuration, relation/type mapping, appropriate old-row data,
slot lifecycle and WAL-retention operations. It does not require another
database replica. Repeated delivery must be handled safely.

Neither mechanism is selected. Both still need the integration and recovery
work below; choosing a detector does not solve the entire project.

## Main work packages

1. Declare the supported database versions, writer roles and mutation paths,
   including bulk changes, partitions, cascading effects and TRUNCATE.
2. Select and implement one durable source, with installation, coverage,
   permissions and failure diagnostics.
3. Map physical changes through authored bindings into typed Garns identities,
   old/new scopes, relationships and question footprints. Do not infer names
   or dispatch by example schema.
4. Preserve transaction boundaries and commit-safe ordering. Couple event
   consumption, revision creation and acknowledgement idempotently, including
   crash recovery, duplicate delivery and concurrent consumers.
5. Keep external source-actor provenance separate from capture-processor and
   administrator identities. Define what can be trusted, rejected or reported.
6. Integrate snapshot/replay, retention, migration generations, monitoring and
   cleanup with the governed runtime, without a second incompatible ledger.

## Evidence needed to ship

Tests must show that rollback emits nothing, committed events are not lost
after downtime, repeats do not create duplicate revisions, and transaction
interleavings cannot be skipped by a cursor. Live results must agree with
one-shot recomputation for every supported change shape. Coverage, attribution,
permissions, migration, retention and unsupported-path behavior need real
database evidence, not just a happy-path trigger demonstration.

The original plan's W6/P6 requirements and the provider-neutral amendment's
capture-specific tests are useful future acceptance inputs. They must be
reassessed against the shipped governed runtime rather than assumed accepted
for a new adapter.

## Launch later without blocking Garns

When the core transaction, revision and replay contracts are stable, a
separately authorized effort can compare the two mechanisms, choose one,
write an implementation plan and run independent reviews. Package placement
and ownership are future decisions; this brief creates no repository, launches
no agent and imposes no capture-interface freeze on v9-6.

The governing deferral is recorded in
[the v9-6 governed-write scope amendment](GarnsV9-6-GovernedWritesScopeAmendment.md).
