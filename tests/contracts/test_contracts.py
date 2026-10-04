from __future__ import annotations

import asyncio
import copy
from dataclasses import FrozenInstanceError, asdict, replace
from enum import Enum
import inspect
import pickle
import unittest

from garns.types import TypeRef
from garns.backends.contracts.authority import AuthorityBoundIterator, RuntimeAuthority, TrustedClaims, TrustedContext
from garns.backends.contracts.admission import LeaseState, OperationKind, PlanStep, ReadOperationLease
from garns.backends.contracts.generation_reference import ReferenceGenerationCoordinator
from garns.backends.contracts.lifetime import ActivationEvidence, ResourceIdentity, ResourceKind
from garns.backends.contracts.lifetime_reference import ReferenceLifetimeRegistry
from garns.backends.contracts.operations import (
    GovernedMutation, LedgerEffect, LedgerPublication, MigrationDecision, MigrationEffect,
    MigrationLock, MigrationOutcome, MigrationRequest, MutationKind, QualifiedName,
    SchemaSnapshot,
)
from garns.backends.contracts.protocols import AsyncBackend, AsyncConnection, AsyncPool, AsyncSubscription, AsyncTransaction
from garns.backends.contracts.semantic import (
    BindingIdentity, FrozenPlanRoot, NestedResult, Parameter, Plan, PlanOrigin,
    NESTED_RESULT_TYPE, ResultField, ResultFieldRole, ResultShape, SemanticType,
)
from garns.backends.contracts.state import (
    AbortEvidence, CloseKnowledge, CloseOutcome, CommitKnowledge, CommitOutcome,
    CommitOrderedPublication, Lifecycle, OperationPhase, ReconcileFinding,
    TransactionUseGuard, WorkerCommitFence, cancellation_outcome,
    connection_disposition, reconcile, transition,
)
from garns.backends.contracts.values import (
    BackendCapabilities, Capability, ContractRefusal, DeadlinePolicy, Delivery,
    FrozenMap, ParameterValues, QualifiedDeployment, RefusalCode, RevisionCursor,
    Snapshot, TransactionIdentity,
)


class AuthorizingFakeTransaction:
    def __init__(self, connection, identity): self.connection, self.identity = connection, identity
    async def mutate(self, mutation, context):
        self.connection.authorize(Capability.GOVERNED_WRITE, context)
        self.connection.invocations += 1
    async def commit(self, context):
        self.connection.authorize(Capability.GOVERNED_WRITE, context)
        return cancellation_outcome(self.identity, OperationPhase.COMMIT_REQUESTED, AbortEvidence.NONE)
    async def rollback(self):
        return cancellation_outcome(self.identity, OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.ROLLBACK_CONFIRMED)
    async def reconcile(self, context):
        self.connection.authorize(Capability.GOVERNED_WRITE, context)
        return reconcile(self.identity, ReconcileFinding.NOT_FOUND_NOT_FINAL)


class AuthorizingFakeConnection:
    def __init__(self, issuer, binding, capabilities, verifier):
        self.issuer, self.binding, self.capabilities, self.verifier = issuer, binding, capabilities, verifier
        self.invocations = 0

    def authorize(self, capability, context):
        self.capabilities.require(capability)
        self.issuer.validate(context, scope=self.binding.scope, capability=capability)

    async def execute(self, lease, context):
        self.authorize(Capability.QUERY, context)
        owner = self.issuer.capture_task_owner()
        self.verifier.run_plan_step(
            lease, PlanStep.LOWER, owner, self.verifier.issue_consumer("fake-lower"),
        )
        self.verifier.run_plan_step(
            lease, PlanStep.PUBLICATION, owner, self.verifier.issue_consumer("fake-publish"),
        )
        self.invocations += 1
        self.verifier.complete(lease, owner, LeaseState.SUCCEEDED)
        return ()

    async def begin(self, identity, context):
        self.authorize(Capability.GOVERNED_WRITE, context)
        self.invocations += 1
        return AuthorizingFakeTransaction(self, identity)

    async def consistent_snapshot(self, lease, context):
        self.authorize(Capability.QUERY, context)
        owner = self.issuer.capture_task_owner()
        self.verifier.run_plan_step(
            lease, PlanStep.SNAPSHOT_WATERMARK, owner,
            self.verifier.issue_consumer("fake-snapshot"),
        )
        self.verifier.run_plan_step(
            lease, PlanStep.PUBLICATION, owner,
            self.verifier.issue_consumer("fake-snapshot-publish"),
        )
        self.invocations += 1
        self.verifier.complete(lease, owner, LeaseState.SUCCEEDED)
        return Snapshot(RevisionCursor(self.binding.scope, self.binding.generation, 0), ())

    async def inspect_schema(self, context):
        self.authorize(Capability.SCHEMA_INSPECT, context)
        self.invocations += 1
        return SchemaSnapshot(self.binding, "schema", ())

    async def acquire_migration_lock(self, request, context, deadline):
        self.authorize(Capability.MIGRATE_DATA, context)
        self.invocations += 1
        return MigrationLock("scope", "owner")

    async def apply_migration(self, lock, request, context):
        self.authorize(Capability.MIGRATE_DATA, context); self.invocations += 1
        return MigrationOutcome.success(request, request.after, metadata_proof_digest="proof")

    async def read_ledger(self, after, context):
        self.authorize(Capability.REPLAY, context)
        self.invocations += 1
        return ()

    async def sanitize(self, deadline): return True
    async def close(self, deadline): return CloseOutcome(CloseKnowledge.CLOSED)


class AuthorizingFakePool:
    def __init__(self, issuer, connection): self.issuer, self.connection = issuer, connection
    async def acquire(self, context, deadline):
        self.issuer.validate(context, scope=self.connection.binding.scope, capability=Capability.QUERY)
        return self.connection
    async def release(self, connection, context, deadline):
        self.issuer.validate(context, scope=self.connection.binding.scope, capability=Capability.QUERY)
    async def close(self, deadline, force=False): return CloseOutcome(CloseKnowledge.CLOSED)


class AuthorizingFakeBackend:
    def __init__(self, issuer, binding, capabilities, verifier):
        self.issuer, self.capabilities = issuer, capabilities
        self.connection = AuthorizingFakeConnection(issuer, binding, capabilities, verifier)
    async def open(self, context, deadlines):
        self.issuer.validate(context, scope=self.connection.binding.scope, capability=Capability.QUERY)
        return AuthorizingFakePool(self.issuer, self.connection)
    async def open_privileged(self, binding, deadlines):
        if binding != self.connection.binding: raise ContractRefusal(RefusalCode.BINDING_MISMATCH, "binding")
        return AuthorizingFakePool(self.issuer, self.connection)
    async def subscribe(self, handle, lease, context, after):
        raise NotImplementedError


def make_plan(scope: QualifiedDeployment, *, storage: str = "storage", generation: int = 1) -> Plan:
    text = SemanticType("Text", "text")
    origin = PlanOrigin(scope.world, "ir", storage, generation)
    return Plan("sales.open", "query", (Parameter("floor", text),),
                ResultShape((ResultField("sales.Order.status", text),)),
                FrozenPlanRoot("w2/1", "root-digest", b"opaque"), origin)


class AuthorityState:
    def __init__(self): self.now, self.epoch, self.task = 1.0, 3, object()

def make_context(scope: QualifiedDeployment, capabilities: object = None):
    state = AuthorityState()
    issuer = RuntimeAuthority(lambda: state.now, lambda: state.epoch, lambda: state.task)
    claims = TrustedClaims("SECRET_PRINCIPAL", "SECRET_WRITER", scope,
                           {Capability.QUERY} if capabilities is None else capabilities,
                           "SECRET_CONTEXT", 10.0, 3)
    return issuer, issuer.issue(claims), state


def make_reference_registry(issuer, scope, plan):
    binding = BindingIdentity(scope, "ir", "storage", 1)
    coordinator = ReferenceGenerationCoordinator(scope, binding)
    coordinator.begin_activation(1)
    coordinator.finish_activation(ActivationEvidence(
        scope, binding, 1, "inventory", "physical-fence", "record",
        "plan_admission_lifetime_v1",
    ))
    coordinator.first_lifetime_open("plan_admission_lifetime_v1", 1)
    registry = ReferenceLifetimeRegistry(issuer, object(), coordinator)
    registry.open_lifetime()
    runtime = ResourceIdentity("runtime", ResourceKind.RUNTIME)
    pool = ResourceIdentity("pool", ResourceKind.POOL, ("runtime",))
    connection = ResourceIdentity("connection", ResourceKind.CONNECTION, ("runtime", "pool"))
    for resource in (runtime, pool, connection):
        registry.add_resource(resource)
    handle = registry.setup_reference_admission(plan, binding)
    return registry, handle, connection


class ImmutableSemanticTests(unittest.TestCase):
    def test_type_ref_dimensions_are_lossless(self) -> None:
        samples = (
            TypeRef("Text", "text"),
            TypeRef("Text", "text", optional=True),
            TypeRef("Integer", "integer", list_of=True),
            TypeRef("Text", "text", nominal="m.Code"),
            TypeRef("Text", "text", nominal="m.State", closed=("open", "closed")),
            TypeRef("Id", "text", carrier="m.Order"),
        )
        descriptors = tuple(SemanticType.from_type_ref(sample) for sample in samples)
        self.assertEqual(len(samples), len(set(descriptors)))
        for source, target in zip(samples, descriptors):
            self.assertEqual(source.canonical(), {
                "base": target.base, "class": target.storage_class,
                "optional": target.optional, "list_of": target.list_of,
                "nominal": target.nominal, "closed": list(target.closed),
                "carrier": target.carrier,
            })

    def test_each_type_dimension_affects_identity(self) -> None:
        base = SemanticType("Text", "text")
        mutants = (
            SemanticType("Id", "text"), SemanticType("Text", "opaque"),
            SemanticType("Text", "text", optional=True), SemanticType("Text", "text", list_of=True),
            SemanticType("Text", "text", nominal="m.N"),
            SemanticType("Text", "text", nominal="m.C", closed=("x",)),
            SemanticType("Text", "text", carrier="m.Carrier"),
        )
        self.assertTrue(all(mutant != base for mutant in mutants))

    def test_nested_results_have_stable_named_owner(self) -> None:
        text = SemanticType("Text", "text")
        child = ResultShape((ResultField("sales.Line.value", text),))
        parent = ResultShape((ResultField("sales.Order.lines", NESTED_RESULT_TYPE,
                                          role=ResultFieldRole.NESTED_OWNER),),
                             (NestedResult("sales.Order.lines", child),))
        self.assertEqual("sales.Order.lines", parent.nested[0].owner_qualified_name)
        with self.assertRaises(ValueError):
            ResultShape(parent.fields, (NestedResult("wrong", child),))

    def test_caller_lists_are_detached_from_shapes_and_plan(self) -> None:
        text = SemanticType("Text", "text")
        fields = [ResultField("m.x", text)]
        parameters = [Parameter("p", text)]
        shape = ResultShape(fields)  # type: ignore[arg-type]
        plan = Plan("m.q", "query", parameters, shape, FrozenPlanRoot("w2", "d", b"x"),  # type: ignore[arg-type]
                    PlanOrigin("W", "i", "s", 1))
        fields.clear(); parameters.clear()
        self.assertEqual(1, len(plan.result.fields))
        self.assertEqual(1, len(plan.parameters))

    def test_plan_root_is_owned_bytes_and_binding_aware(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        payload = bytearray(b"opaque")
        with self.assertRaises(TypeError):
            FrozenPlanRoot("w2", "d", payload)  # type: ignore[arg-type]
        a = make_plan(scope, storage="a")
        b = make_plan(scope, storage="b")
        self.assertNotEqual(a, b)
        with self.assertRaises(ContractRefusal) as caught:
            BindingIdentity(scope, "ir", "b", 1).validate_plan(a)
        self.assertEqual(RefusalCode.BINDING_MISMATCH, caught.exception.code)
        with self.assertRaises(ContractRefusal) as caught:
            BindingIdentity(scope, "ir", "a", 2).validate_plan(a)
        self.assertEqual(RefusalCode.GENERATION_MISMATCH, caught.exception.code)

    def test_parameters_snapshots_and_deliveries_recursively_detach(self) -> None:
        source = {"nested": [{"x": [1, 2]}, {"tags": {"a", "b"}}]}
        values = ParameterValues(source)
        scope = QualifiedDeployment("SALES", "PROD")
        row = {"value": source["nested"]}
        snap = Snapshot(RevisionCursor(scope, 1, 4), (row,))
        delivery = Delivery(RevisionCursor(scope, 1, 3), RevisionCursor(scope, 1, 4),
                            RevisionCursor(scope, 1, 4), (row,))
        source["nested"][0]["x"].append(99)  # type: ignore[index,union-attr]
        self.assertNotIn("99", repr(values.values))
        self.assertNotIn("99", repr(snap.rows))
        self.assertEqual(snap.rows, delivery.rows)
        with self.assertRaises(TypeError):
            Snapshot(RevisionCursor(scope, 1, 4), ({"bad": object()},))


class TrustedContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = QualifiedDeployment("SALES", "PROD")
        self.issuer, self.context, self.state = make_context(self.scope)

    def validate(self, context: TrustedContext | object = None) -> None:
        self.issuer.validate(self.context if context is None else context, scope=self.scope,
                             capability=Capability.QUERY)  # type: ignore[arg-type]

    def test_only_exact_issued_instance_validates(self) -> None:
        self.validate()
        counterfeit = object.__new__(TrustedContext)
        with self.assertRaises(ContractRefusal):
            self.validate(counterfeit)

    def test_copy_deepcopy_replace_pickle_and_dataclass_conversion_refuse(self) -> None:
        for operation in (
            lambda: copy.copy(self.context), lambda: copy.deepcopy(self.context),
            lambda: replace(self.context), lambda: pickle.dumps(self.context),
            lambda: asdict(self.context),
        ):
            with self.assertRaises(TypeError):
                operation()

    def test_handle_has_no_authority_bearing_fields_or_reinitialization(self) -> None:
        self.assertEqual(("__weakref__",), TrustedContext.__slots__)
        for name in ("_claims", "claims", "_issuer", "issuer", "_registry", "registry",
                     "_capability_id", "context_id", "principal", "writer", "scope"):
            self.assertFalse(hasattr(self.context, name), name)
            with self.assertRaises(AttributeError):
                setattr(self.context, name, object())
        with self.assertRaises(TypeError):
            self.context.__init__()
        self.validate()

    def test_direct_claim_substitution_refuses(self) -> None:
        with self.assertRaises(AttributeError):
            self.context._claims = TrustedClaims("attacker", "attacker", self.scope,
                                                 {Capability.GOVERNED_WRITE}, "x", 10, 3)
        self.validate()
        with self.assertRaises(AttributeError):
            del self.context._claims

    def test_repr_and_serialization_do_not_disclose_canaries(self) -> None:
        canaries = ("SECRET_PRINCIPAL", "SECRET_WRITER", "SECRET_WORLD",
                    "SECRET_DEPLOYMENT", "SECRET_CONTEXT", "query",
                    "987654.125", "7654321")
        state = AuthorityState()
        issuer = RuntimeAuthority(lambda: state.now, lambda: state.epoch, lambda: state.task)
        context = issuer.issue(TrustedClaims(canaries[0], canaries[1],
            QualifiedDeployment(canaries[2], canaries[3]), {Capability.QUERY},
            canaries[4], 987654.125, 7654321))
        surfaces = (repr(context), str(context), repr(dir(context)),
                    repr(inspect.getmembers(context)))
        for rendered in surfaces:
            for canary in canaries:
                self.assertNotIn(canary, rendered)
        for operation in (lambda: pickle.dumps(context), lambda: context.__reduce_ex__(5),
                          lambda: copy.copy(context), lambda: copy.deepcopy(context),
                          lambda: vars(context), lambda: asdict(context)):
            with self.assertRaises((TypeError, AttributeError)):
                operation()

    def test_cross_issuer_and_reconstructed_handles_refuse(self) -> None:
        other = RuntimeAuthority(lambda: self.state.now, lambda: self.state.epoch,
                                 lambda: self.state.task)
        with self.assertRaises(ContractRefusal):
            other.validate(self.context, scope=self.scope, capability=Capability.QUERY)
        for counterfeit in (object.__new__(TrustedContext),):
            with self.assertRaises(ContractRefusal):
                self.validate(counterfeit)

    def test_claims_defensively_normalize_mutable_inputs_and_hostile_strings(self) -> None:
        class HostileStr(str):
            pass
        caps = {Capability.QUERY}
        claims = TrustedClaims(HostileStr("p"), HostileStr("w"), self.scope, caps,
                               HostileStr("c"), 10.0, 0)
        caps.add(Capability.GOVERNED_WRITE)
        self.assertEqual(frozenset({Capability.QUERY}), claims.capabilities)
        self.assertIs(str, type(claims.principal))
        with self.assertRaises(ValueError):
            TrustedClaims("p", "w", self.scope, set(), "c", float("inf"), 0)

    def test_runtime_owned_task_clock_epoch_scope_and_capability_refuse(self) -> None:
        for mutate in (
            lambda: setattr(self.state, "task", object()),
            lambda: setattr(self.state, "now", 10.0),
            lambda: setattr(self.state, "epoch", 4),
        ):
            original = (self.state.task, self.state.now, self.state.epoch)
            mutate()
            with self.assertRaises(ContractRefusal): self.validate()
            self.state.task, self.state.now, self.state.epoch = original
        with self.assertRaises(ContractRefusal):
            self.issuer.validate(self.context, scope=QualifiedDeployment("SALES", "TEST"), capability=Capability.QUERY)
        with self.assertRaises(ContractRefusal):
            self.issuer.validate(self.context, scope=self.scope, capability=Capability.GOVERNED_WRITE)


class StateModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = QualifiedDeployment("SALES", "PROD")
        self.tx = TransactionIdentity(self.scope, "tx")

    def test_cancellation_requires_authoritative_abort_evidence(self) -> None:
        unresolved = (
            (OperationPhase.STATEMENT, AbortEvidence.NONE),
            (OperationPhase.WRITES_APPLIED, AbortEvidence.CONNECTION_LOST),
            (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.ROLLBACK_ACK_LOST),
            (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.CLEANUP_TIMEOUT),
            (OperationPhase.COMMIT_REQUESTED, AbortEvidence.NONE),
        )
        for phase, evidence in unresolved:
            self.assertIs(CommitKnowledge.INDETERMINATE,
                          cancellation_outcome(self.tx, phase, evidence).knowledge)
        self.assertIs(CommitKnowledge.KNOWN_ABORTED,
                      cancellation_outcome(self.tx, OperationPhase.QUEUED, AbortEvidence.NOT_STARTED).knowledge)
        self.assertIs(CommitKnowledge.KNOWN_ABORTED,
                      cancellation_outcome(self.tx, OperationPhase.ROLLBACK_REQUESTED,
                                           AbortEvidence.ROLLBACK_CONFIRMED).knowledge)

    def test_phase_evidence_cartesian_product_is_exhaustive(self) -> None:
        aborted = {(OperationPhase.QUEUED, AbortEvidence.NOT_STARTED),
                   (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.ROLLBACK_CONFIRMED)}
        indeterminate = {
            (OperationPhase.STATEMENT, AbortEvidence.NONE), (OperationPhase.STATEMENT, AbortEvidence.CONNECTION_LOST),
            (OperationPhase.STATEMENT, AbortEvidence.CLEANUP_TIMEOUT), (OperationPhase.WRITES_APPLIED, AbortEvidence.NONE),
            (OperationPhase.WRITES_APPLIED, AbortEvidence.CONNECTION_LOST), (OperationPhase.WRITES_APPLIED, AbortEvidence.CLEANUP_TIMEOUT),
            (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.NONE), (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.ROLLBACK_ACK_LOST),
            (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.CONNECTION_LOST), (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.CLEANUP_TIMEOUT),
            (OperationPhase.COMMIT_REQUESTED, AbortEvidence.NONE), (OperationPhase.COMMIT_REQUESTED, AbortEvidence.CONNECTION_LOST),
            (OperationPhase.COMMIT_REQUESTED, AbortEvidence.CLEANUP_TIMEOUT),
        }
        for phase in OperationPhase:
            for evidence in AbortEvidence:
                pair = (phase, evidence)
                if pair in aborted:
                    self.assertIs(CommitKnowledge.KNOWN_ABORTED, cancellation_outcome(self.tx, phase, evidence).knowledge)
                elif pair in indeterminate:
                    self.assertIs(CommitKnowledge.INDETERMINATE, cancellation_outcome(self.tx, phase, evidence).knowledge)
                else:
                    with self.assertRaises(ValueError): cancellation_outcome(self.tx, phase, evidence)

    def test_cancellation_rejects_every_nonmember_enum_shape(self) -> None:
        class Foreign(str, Enum):
            QUEUED = "queued"
            NOT_STARTED = "not_started"

        malformed = (0, 1, False, True, object(), Foreign.QUEUED)
        for phase in OperationPhase:
            with self.assertRaises(ValueError):
                cancellation_outcome(self.tx, phase.value, AbortEvidence.NONE)  # type: ignore[arg-type]
        for evidence in AbortEvidence:
            with self.assertRaises(ValueError):
                cancellation_outcome(self.tx, OperationPhase.STATEMENT,
                                     evidence.value)  # type: ignore[arg-type]
        for value in malformed:
            with self.assertRaises(ValueError):
                cancellation_outcome(self.tx, value, AbortEvidence.NOT_STARTED)  # type: ignore[arg-type]
            with self.assertRaises(ValueError):
                cancellation_outcome(self.tx, OperationPhase.QUEUED, value)  # type: ignore[arg-type]

        fence = WorkerCommitFence(); fence.begin(self.tx)
        with self.assertRaises(ValueError):
            cancellation_outcome(self.tx, "queued", "not_started")  # type: ignore[arg-type]
        self.assertEqual((self.tx,), fence.close_outcome(True).unresolved)

    def test_absence_is_not_abort(self) -> None:
        for finding in (ReconcileFinding.STILL_IN_FLIGHT, ReconcileFinding.NOT_FOUND_NOT_FINAL):
            self.assertIs(CommitKnowledge.INDETERMINATE, reconcile(self.tx, finding).knowledge)

    def test_reconciliation_requires_exact_finding_and_preserves_valid_relation(self) -> None:
        class Foreign(str, Enum):
            ABORTED = "aborted"

        committed = reconcile(self.tx, ReconcileFinding.COMMITTED,
                              RevisionCursor(self.scope, 1, 8))
        self.assertIs(CommitKnowledge.KNOWN_COMMITTED, committed.knowledge)
        self.assertIs(CommitKnowledge.KNOWN_ABORTED,
                      reconcile(self.tx, ReconcileFinding.ABORTED).knowledge)
        for finding in ReconcileFinding:
            with self.assertRaises(ValueError):
                reconcile(self.tx, finding.value)  # type: ignore[arg-type]
        for malformed in (0, 1, False, True, object(), Foreign.ABORTED):
            with self.assertRaises(ValueError):
                reconcile(self.tx, malformed)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            reconcile(self.tx, ReconcileFinding.COMMITTED)
        with self.assertRaises(ValueError):
            reconcile(self.tx, ReconcileFinding.COMMITTED,
                      RevisionCursor(QualifiedDeployment("OTHER", "PROD"), 1, 8))
        for finding in (ReconcileFinding.ABORTED, ReconcileFinding.STILL_IN_FLIGHT,
                        ReconcileFinding.NOT_FOUND_NOT_FINAL):
            with self.assertRaises(ValueError):
                reconcile(self.tx, finding, RevisionCursor(self.scope, 1, 8))

    def test_publication_is_idempotent_and_conflict_detecting_across_generation(self) -> None:
        model = CommitOrderedPublication(self.scope)
        first = model.publish_committed(self.tx, "payload-a")
        self.assertEqual(first, model.publish_committed(self.tx, "payload-a"))
        self.assertEqual(1, model.cursor.revision)
        model.change_generation()
        model.compact_to(RevisionCursor(self.scope, 2, 0))
        self.assertEqual(first, model.publish_committed(self.tx, "payload-a"))
        with self.assertRaises(ContractRefusal) as caught:
            model.publish_committed(self.tx, "payload-b")
        self.assertEqual(RefusalCode.TRANSACTION_IDENTITY_CONFLICT, caught.exception.code)

    def test_revision_follows_publication_not_request_order(self) -> None:
        model = CommitOrderedPublication(self.scope)
        second = model.publish_committed(TransactionIdentity(self.scope, "second"), "b")
        first = model.publish_committed(TransactionIdentity(self.scope, "first"), "a")
        self.assertEqual((1, 2), (second.revision, first.revision))

    def test_worker_fence_blocks_late_commit_and_reports_unresolved(self) -> None:
        fence = WorkerCommitFence()
        fence.begin(self.tx)
        fence.start_shutdown()
        outcome = fence.close_outcome(quiescent=False)
        self.assertIs(CloseKnowledge.NONQUIESCENT, outcome.knowledge)
        self.assertEqual((self.tx,), outcome.unresolved)
        with self.assertRaises(ContractRefusal):
            fence.request_commit(self.tx)
        fence.finish_without_commit(self.tx, CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx))
        self.assertIs(CloseKnowledge.CLOSED, fence.close_outcome(quiescent=True).knowledge)

    def test_commit_already_requested_remains_unresolved_not_aborted(self) -> None:
        fence = WorkerCommitFence(); fence.begin(self.tx); fence.request_commit(self.tx); fence.start_shutdown()
        self.assertIs(CloseKnowledge.NONQUIESCENT, fence.close_outcome(False).knowledge)
        self.assertIs(CommitKnowledge.INDETERMINATE,
                      cancellation_outcome(self.tx, OperationPhase.COMMIT_REQUESTED, AbortEvidence.CLEANUP_TIMEOUT).knowledge)

    def test_commit_requested_requires_matching_terminal_resolution(self) -> None:
        fence = WorkerCommitFence(); fence.begin(self.tx); fence.request_commit(self.tx); fence.start_shutdown()
        indeterminate = CommitOutcome(CommitKnowledge.INDETERMINATE, self.tx)
        fence.resolve(self.tx, indeterminate)
        self.assertEqual((self.tx,), fence.close_outcome(False).unresolved)
        with self.assertRaises(ValueError):
            fence.finish_without_commit(self.tx, CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx))
        other = TransactionIdentity(self.scope, "other")
        with self.assertRaises(ValueError):
            fence.resolve(self.tx, CommitOutcome(CommitKnowledge.KNOWN_ABORTED, other))
        self.assertEqual((self.tx,), fence.close_outcome(False).unresolved)
        committed = CommitOutcome(CommitKnowledge.KNOWN_COMMITTED, self.tx,
                                  RevisionCursor(self.scope, 1, 9))
        fence.resolve(self.tx, committed)
        fence.resolve(self.tx, committed)
        self.assertIs(CloseKnowledge.CLOSED, fence.close_outcome(True).knowledge)
        with self.assertRaises(ValueError):
            fence.resolve(self.tx, CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx))

    def test_wrong_scope_commit_resolution_refuses_without_state_change(self) -> None:
        fence = WorkerCommitFence(); fence.begin(self.tx); fence.request_commit(self.tx)
        with self.assertRaises(ValueError):
            CommitOutcome(CommitKnowledge.KNOWN_COMMITTED, self.tx,
                          RevisionCursor(QualifiedDeployment("OTHER", "PROD"), 1, 1))
        self.assertEqual((self.tx,), fence.close_outcome(False).unresolved)

    def test_abort_resolution_acknowledgement_loss_and_repeated_shutdown(self) -> None:
        fence = WorkerCommitFence(); fence.begin(self.tx); fence.request_commit(self.tx)
        fence.start_shutdown(); fence.start_shutdown()
        lost = cancellation_outcome(self.tx, OperationPhase.COMMIT_REQUESTED,
                                    AbortEvidence.CONNECTION_LOST)
        fence.resolve(self.tx, lost)
        self.assertEqual((self.tx,), fence.close_outcome(False).unresolved)
        aborted = CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx)
        fence.resolve(self.tx, aborted); fence.resolve(self.tx, aborted)
        self.assertIs(CloseKnowledge.CLOSED, fence.close_outcome(True).knowledge)

    def test_worker_admission_refuses_active_and_terminal_identity_reuse(self) -> None:
        fence = WorkerCommitFence(); fence.begin(self.tx)
        with self.assertRaises(ContractRefusal) as active:
            fence.begin(self.tx)
        self.assertEqual(RefusalCode.TRANSACTION_IDENTITY_CONFLICT, active.exception.code)
        self.assertEqual((self.tx,), fence.close_outcome(True).unresolved)
        fence.request_commit(self.tx)
        terminal = CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx)
        fence.resolve(self.tx, terminal); fence.resolve(self.tx, terminal)
        with self.assertRaises(ContractRefusal) as reused:
            fence.begin(self.tx)
        self.assertEqual(RefusalCode.TRANSACTION_IDENTITY_CONFLICT, reused.exception.code)
        self.assertIs(CloseKnowledge.CLOSED, fence.close_outcome(True).knowledge)
        with self.assertRaises(ValueError):
            fence.resolve(self.tx, CommitOutcome(CommitKnowledge.KNOWN_COMMITTED, self.tx,
                                                  RevisionCursor(self.scope, 1, 4)))

    def test_equal_client_ids_in_distinct_qualified_scopes_remain_distinct(self) -> None:
        other = TransactionIdentity(QualifiedDeployment("OTHER", "PROD"), self.tx.client_id)
        fence = WorkerCommitFence(); fence.begin(self.tx); fence.begin(other)
        self.assertEqual({self.tx, other}, set(fence.close_outcome(True).unresolved))
        fence.finish_without_commit(self.tx, CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx))
        self.assertEqual((other,), fence.close_outcome(True).unresolved)

    def test_commit_outcome_closed_grammar_and_resolution_revalidation(self) -> None:
        self.assertIs(CommitKnowledge.KNOWN_ABORTED,
                      CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx).knowledge)
        self.assertIs(CommitKnowledge.INDETERMINATE,
                      CommitOutcome(CommitKnowledge.INDETERMINATE, self.tx).knowledge)
        self.assertIs(CommitKnowledge.KNOWN_COMMITTED,
                      CommitOutcome(CommitKnowledge.KNOWN_COMMITTED, self.tx,
                                    RevisionCursor(self.scope, 1, 1)).knowledge)
        for malformed in ("indeterminate", "fabricated", 0, 1, False, True, object()):
            with self.assertRaises(ValueError):
                CommitOutcome(malformed, self.tx)  # type: ignore[arg-type]
        for knowledge, revision in (
            (CommitKnowledge.KNOWN_COMMITTED, None),
            (CommitKnowledge.KNOWN_ABORTED, RevisionCursor(self.scope, 1, 1)),
            (CommitKnowledge.INDETERMINATE, RevisionCursor(self.scope, 1, 1)),
        ):
            with self.assertRaises(ValueError):
                CommitOutcome(knowledge, self.tx, revision)

        fence = WorkerCommitFence(); fence.begin(self.tx); fence.request_commit(self.tx)
        fabricated = object.__new__(CommitOutcome)
        object.__setattr__(fabricated, "knowledge", "fabricated")
        object.__setattr__(fabricated, "transaction", self.tx)
        object.__setattr__(fabricated, "revision", None)
        with self.assertRaises(ValueError):
            fence.resolve(self.tx, fabricated)
        self.assertEqual((self.tx,), fence.close_outcome(True).unresolved)
        self.assertEqual({}, fence._resolved)

    def test_close_outcome_quiescence_and_transaction_knowledge_are_independent(self) -> None:
        empty = WorkerCommitFence()
        self.assertEqual(CloseOutcome(CloseKnowledge.CLOSED), empty.close_outcome(True))
        self.assertEqual(CloseOutcome(CloseKnowledge.NONQUIESCENT), empty.close_outcome(False))

        precommit = WorkerCommitFence(); precommit.begin(self.tx)
        self.assertEqual(CloseKnowledge.UNRESOLVED, precommit.close_outcome(True).knowledge)
        self.assertEqual(CloseKnowledge.NONQUIESCENT, precommit.close_outcome(False).knowledge)

        indeterminate = WorkerCommitFence(); indeterminate.begin(self.tx); indeterminate.request_commit(self.tx)
        indeterminate.resolve(self.tx, CommitOutcome(CommitKnowledge.INDETERMINATE, self.tx))
        for quiescent, expected in ((True, CloseKnowledge.UNRESOLVED),
                                    (False, CloseKnowledge.NONQUIESCENT)):
            outcome = indeterminate.close_outcome(quiescent)
            self.assertIs(expected, outcome.knowledge)
            self.assertEqual((self.tx,), outcome.unresolved)

        terminal = WorkerCommitFence(); terminal.begin(self.tx); terminal.request_commit(self.tx)
        terminal.resolve(self.tx, CommitOutcome(CommitKnowledge.KNOWN_ABORTED, self.tx))
        self.assertEqual(CloseOutcome(CloseKnowledge.CLOSED), terminal.close_outcome(True))
        self.assertEqual(CloseOutcome(CloseKnowledge.NONQUIESCENT), terminal.close_outcome(False))

        other = TransactionIdentity(QualifiedDeployment("OTHER", "PROD"), "other")
        multiple_precommit = WorkerCommitFence()
        multiple_precommit.begin(self.tx); multiple_precommit.begin(other)
        multiple_indeterminate = WorkerCommitFence()
        for transaction in (self.tx, other):
            multiple_indeterminate.begin(transaction); multiple_indeterminate.request_commit(transaction)
            multiple_indeterminate.resolve(
                transaction, CommitOutcome(CommitKnowledge.INDETERMINATE, transaction))
        for fence in (multiple_precommit, multiple_indeterminate):
            expected = {self.tx, other}
            quiescent = fence.close_outcome(True)
            running = fence.close_outcome(False)
            self.assertIs(CloseKnowledge.UNRESOLVED, quiescent.knowledge)
            self.assertIs(CloseKnowledge.NONQUIESCENT, running.knowledge)
            self.assertEqual(expected, set(quiescent.unresolved))
            self.assertEqual(expected, set(running.unresolved))

        with self.assertRaises(ValueError):
            CloseOutcome(CloseKnowledge.UNRESOLVED)
        with self.assertRaises(ValueError):
            CloseOutcome(CloseKnowledge.CLOSED, (self.tx,))
        with self.assertRaises(ValueError):
            empty.close_outcome(1)  # type: ignore[arg-type]
        with self.assertRaises(ValueError):
            CloseOutcome("closed")  # type: ignore[arg-type]

    def test_lifecycle_ownership_and_sanitation(self) -> None:
        self.assertIs(Lifecycle.OPEN, transition(Lifecycle.NEW, Lifecycle.OPEN))
        with self.assertRaises(ValueError):
            transition(Lifecycle.OPEN, Lifecycle.CLOSED)
        state = AuthorityState(); authority = RuntimeAuthority(lambda: 1.0, lambda: 0, lambda: state.task)
        guard = TransactionUseGuard(authority); guard.enter()
        with self.assertRaises(ContractRefusal):
            guard.enter()
        guard.leave()
        self.assertEqual("discard", connection_disposition(protocol_idle=False, transaction_idle=True,
                                                            session_sanitized=True).value)

    def test_equal_but_distinct_owner_cannot_enter(self) -> None:
        class Equal:
            def __eq__(self, other): return True
        owner, counterfeit = Equal(), Equal()
        current = [owner]
        authority = RuntimeAuthority(lambda: 1.0, lambda: 0, lambda: current[0])
        guard = TransactionUseGuard(authority); current[0] = counterfeit
        with self.assertRaises(ContractRefusal): guard.enter()

    def test_child_task_cannot_use_parent_owned_transaction(self) -> None:
        async def scenario():
            owner = asyncio.current_task(); self.assertIsNotNone(owner)
            authority = RuntimeAuthority(lambda: 1.0, lambda: 0, lambda: asyncio.current_task())
            guard = TransactionUseGuard(authority)
            async def child():
                with self.assertRaises(ContractRefusal): guard.enter()
            await asyncio.create_task(child())
            guard.enter(); guard.leave()
        asyncio.run(scenario())


class ProtocolAndOperationTests(unittest.TestCase):
    def test_complete_protocol_operation_inventory_and_async_shape(self) -> None:
        expected = {
            AsyncBackend: {"open", "open_privileged", "subscribe"},
            AsyncPool: {"acquire", "release", "close"},
            AsyncConnection: {"execute", "begin", "consistent_snapshot", "inspect_schema",
                              "acquire_migration_lock", "apply_migration", "read_ledger", "sanitize", "close"},
            AsyncTransaction: {"mutate", "commit", "rollback", "reconcile"},
            AsyncSubscription: {"refresh", "bind_delivery", "aclose"},
        }
        for protocol, names in expected.items():
            self.assertTrue(names <= set(dir(protocol)))
            for name in names:
                if name != "bind_delivery":
                    self.assertTrue(inspect.iscoroutinefunction(getattr(protocol, name)), f"{protocol.__name__}.{name}")
                parameters = inspect.signature(getattr(protocol, name)).parameters
                self.assertFalse({"now", "epoch", "owner_id", "current_epoch"} & set(parameters),
                                 f"{protocol.__name__}.{name} exposes caller freshness/owner")

    def test_both_backend_descriptions_use_same_surface_and_refuse_explicitly(self) -> None:
        for backend in ("sqlite", "postgres"):
            caps = BackendCapabilities(backend, {Capability.QUERY}, {"serializable"}, "target")
            caps.require(Capability.QUERY)
            with self.assertRaises(ContractRefusal):
                caps.require(Capability.MIGRATE_DATA)

    def test_migration_classes_account_or_refuse(self) -> None:
        MigrationDecision(MigrationEffect.METADATA_ONLY, False, False).validate()
        for effect in (MigrationEffect.BACKFILL, MigrationEffect.DDL_DATA_CHANGE):
            with self.assertRaises(ContractRefusal):
                MigrationDecision(effect, False, True).validate()
            MigrationDecision(effect, True, True).validate()

    def test_migration_success_is_coupled_to_request_and_publication(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        before = BindingIdentity(scope, "ir1", "s1", 1)
        after = BindingIdentity(scope, "ir2", "s2", 2)
        metadata = MigrationRequest(before, after, MigrationDecision(MigrationEffect.METADATA_ONLY, False, False), "meta")
        self.assertIsNone(MigrationOutcome.success(metadata, after, metadata_proof_digest="proof").publication)
        with self.assertRaises(ValueError): MigrationOutcome.success(metadata, after)
        for effect in (MigrationEffect.BACKFILL, MigrationEffect.DDL_DATA_CHANGE):
            request = MigrationRequest(before, after, MigrationDecision(effect, True, True), "change")
            mutation = GovernedMutation(MutationKind.UPDATE, "sales.Order", 1, {"status": "closed"})
            ledger_effect = LedgerEffect("sales.Order", 1, MutationKind.UPDATE, mutation.values)
            good = LedgerPublication(TransactionIdentity(scope, "migration:change"),
                                     RevisionCursor(scope, 2, 1), "change", (ledger_effect,))
            self.assertEqual(after, MigrationOutcome.success(request, after, good).binding)
            malformed = (
                None,
                LedgerPublication(TransactionIdentity(scope, "migration:change"), RevisionCursor(scope, 2, 1), "change", ()),
                LedgerPublication(TransactionIdentity(QualifiedDeployment("SALES", "TEST"), "migration:change"), RevisionCursor(QualifiedDeployment("SALES", "TEST"), 2, 1), "change", (ledger_effect,)),
                LedgerPublication(TransactionIdentity(scope, "migration:change"), RevisionCursor(scope, 1, 1), "change", (ledger_effect,)),
                LedgerPublication(TransactionIdentity(scope, "wrong"), RevisionCursor(scope, 2, 1), "change", (ledger_effect,)),
                LedgerPublication(TransactionIdentity(scope, "migration:change"), RevisionCursor(scope, 2, 1), "wrong", (ledger_effect,)),
            )
            for publication in malformed:
                with self.assertRaises(ValueError): MigrationOutcome.success(request, after, publication)

    def test_misc_qualified_and_deadline_values(self) -> None:
        self.assertEqual("bound", QualifiedName("db", "bound", "orders").schema)
        with self.assertRaises(ValueError):
            DeadlinePolicy(1, 1, float("inf"), 1, 1, 1)


class AuthorityFakeTests(unittest.IsolatedAsyncioTestCase):
    async def test_conforming_fake_open_acquire_execute_snapshot_authority(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        issuer, context, state = make_context(scope)
        plan = make_plan(scope)
        caps = BackendCapabilities("sqlite", {Capability.QUERY}, {"serializable"}, "target")
        registry, handle, resource = make_reference_registry(issuer, scope, plan)
        backend = AuthorizingFakeBackend(issuer, BindingIdentity(scope, "ir", "storage", 1), caps, registry)
        self.assertIsInstance(backend, AsyncBackend)
        deadlines = DeadlinePolicy(1, 1, 1, 1, 1, 1)
        bad_contexts = (object(), object.__new__(TrustedContext))
        for bad in bad_contexts:
            with self.assertRaises(ContractRefusal):
                await backend.open(bad, deadlines)
        for field, value in (("task", object()), ("now", 10.0), ("epoch", 4)):
            original = getattr(state, field); setattr(state, field, value)
            with self.assertRaises(ContractRefusal):
                await backend.open(context, deadlines)
            setattr(state, field, original)
        pool = await backend.open(context, deadlines)
        self.assertIsInstance(pool, AsyncPool)
        connection = await pool.acquire(context, 1.0)
        self.assertIsInstance(connection, AsyncConnection)
        execute_lease = registry.acquire(
            handle, OperationKind.EXECUTE, ParameterValues({"floor": "x"}), context,
            resource=resource, owner=state.task,
        )
        await connection.execute(execute_lease, context)
        snapshot_lease = registry.acquire(
            handle, OperationKind.CONSISTENT_SNAPSHOT, ParameterValues({"floor": "x"}), context,
            resource=resource, owner=state.task,
        )
        await connection.consistent_snapshot(snapshot_lease, context)
        self.assertEqual(2, backend.connection.invocations)
        rejected_lease = registry.acquire(
            handle, OperationKind.EXECUTE, ParameterValues({}), context,
            resource=resource, owner=state.task,
        )
        with self.assertRaises(ContractRefusal):
            state.task = object()
            await connection.execute(rejected_lease, context)
        self.assertEqual(2, backend.connection.invocations)

    async def test_unsupported_protected_work_refuses_before_adapter_invocation_on_both_backends(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        for backend_name in ("sqlite", "postgres"):
            issuer, context, state = make_context(scope, {Capability.QUERY, Capability.GOVERNED_WRITE})
            caps = BackendCapabilities(backend_name, {Capability.QUERY}, {"serializable"}, "target")
            registry, handle, resource = make_reference_registry(issuer, scope, make_plan(scope))
            backend = AuthorizingFakeBackend(
                issuer, BindingIdentity(scope, "ir", "storage", 1), caps, registry)
            before = backend.connection.invocations
            with self.assertRaises(ContractRefusal) as caught:
                await backend.connection.begin(TransactionIdentity(scope, "tx"), context)
            self.assertEqual(RefusalCode.CAPABILITY_UNSUPPORTED, caught.exception.code)
            self.assertEqual(before, backend.connection.invocations)

    async def test_replacement_context_cannot_override_lease_bound_authority(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        issuer, original, state = make_context(scope)
        replacement = issuer.issue(TrustedClaims(
            "other", "other", scope, {Capability.QUERY}, "replacement", 10.0, 3,
        ))
        plan = make_plan(scope)
        registry, handle, resource = make_reference_registry(issuer, scope, plan)
        caps = BackendCapabilities("sqlite", {Capability.QUERY}, {"serializable"}, "target")
        connection = AuthorizingFakeConnection(
            issuer, BindingIdentity(scope, "ir", "storage", 1), caps, registry,
        )
        lease = registry.acquire(
            handle, OperationKind.EXECUTE, ParameterValues({"floor": "x"}), original,
            resource=resource, owner=state.task,
        )
        issuer.invalidate(original)
        with self.assertRaises(ContractRefusal):
            await connection.execute(lease, replacement)
        self.assertEqual(0, connection.invocations)
        self.assertEqual(LeaseState.CONTAINED, registry.lease_state(lease))

    async def test_wrong_plan_binding_refuses_before_adapter_invocation(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        issuer, context, state = make_context(scope)
        caps = BackendCapabilities("sqlite", {Capability.QUERY}, {"serializable"}, "target")
        registry, handle, resource = make_reference_registry(issuer, scope, make_plan(scope))
        connection = AuthorizingFakeConnection(
            issuer, BindingIdentity(scope, "ir", "storage", 1), caps, registry)
        with self.assertRaises(ContractRefusal):
            registry.setup_reference_admission(
                make_plan(scope, storage="other"), BindingIdentity(scope, "ir", "storage", 1))
        self.assertEqual(0, connection.invocations)

    async def test_authority_bound_async_for_checks_before_and_after_read(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        state = AuthorityState()
        authority = RuntimeAuthority(lambda: state.now, lambda: state.epoch, lambda: state.task)
        claims = TrustedClaims("p", "w", scope, {Capability.LIVE}, "c", 5.0, 3)
        context = authority.issue(claims)
        reads = 0
        async def immediate():
            nonlocal reads; reads += 1
            return "row"
        iterator = AuthorityBoundIterator(authority, context, scope, Capability.LIVE, immediate)
        self.assertEqual("row", await iterator.__anext__())
        state.now = 6.0
        with self.assertRaises(ContractRefusal): await iterator.__anext__()
        self.assertEqual(1, reads, "expired authority must refuse before reading")

    async def test_paused_read_revalidates_and_renewal_closes_old_iterator(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        state = AuthorityState()
        authority = RuntimeAuthority(lambda: state.now, lambda: state.epoch, lambda: state.task)
        context = authority.issue(TrustedClaims("p", "w", scope, {Capability.LIVE}, "old", 10.0, 3))
        entered, release = asyncio.Event(), asyncio.Event()
        async def paused(): entered.set(); await release.wait(); return "secret"
        old = AuthorityBoundIterator(authority, context, scope, Capability.LIVE, paused)
        pending = asyncio.create_task(old.__anext__()); await entered.wait()
        state.epoch = 4; release.set()
        with self.assertRaises(ContractRefusal): await pending

        state.epoch = 3; entered.clear(); release.clear()
        pending = asyncio.create_task(old.__anext__()); await entered.wait()
        renewed_context = authority.issue(TrustedClaims("p", "w", scope, {Capability.LIVE}, "new", 10.0, 3))
        new = old.renew(renewed_context); release.set()
        with self.assertRaises(StopAsyncIteration): await pending
        async def once(): return "new-row"
        new = AuthorityBoundIterator(authority, renewed_context, scope, Capability.LIVE, once)
        rows = []
        async for row in new:
            rows.append(row); new.close()
        self.assertEqual(["new-row"], rows)

    async def test_retained_child_task_cannot_deliver(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        owner = asyncio.current_task()
        authority = RuntimeAuthority(lambda: 1.0, lambda: 3, lambda: asyncio.current_task())
        context = authority.issue(TrustedClaims("p", "w", scope, {Capability.LIVE}, "c", 10.0, 3))
        reads = 0
        async def reader():
            nonlocal reads; reads += 1; return "secret"
        iterator = AuthorityBoundIterator(authority, context, scope, Capability.LIVE, reader)
        async def child():
            with self.assertRaises(ContractRefusal): await iterator.__anext__()
        await asyncio.create_task(child())
        self.assertEqual(0, reads)

    async def test_subscription_has_one_concrete_bound_iteration_graph(self) -> None:
        scope = QualifiedDeployment("SALES", "PROD")
        state = AuthorityState()
        authority = RuntimeAuthority(lambda: state.now, lambda: state.epoch, lambda: state.task)
        context = authority.issue(TrustedClaims("p", "w", scope, {Capability.LIVE}, "c", 10.0, 3))
        async def reader(): return "row"
        class FakeSubscription:
            cursor = RevisionCursor(scope, 1, 0)
            async def refresh(self, lease, supplied):
                return None
            def bind_delivery(self, lease, supplied):
                return AuthorityBoundIterator(authority, supplied, scope, Capability.LIVE, reader)
            async def aclose(self, deadline): return CloseOutcome(CloseKnowledge.CLOSED)
        subscription = FakeSubscription()
        self.assertIsInstance(subscription, AsyncSubscription)
        self.assertFalse(hasattr(subscription, "__aiter__"))
        iterator = subscription.bind_delivery(object.__new__(ReadOperationLease), context)
        self.assertEqual("row", await iterator.__anext__())
        state.epoch = 4
        with self.assertRaises(ContractRefusal): await iterator.__anext__()


if __name__ == "__main__":
    unittest.main()
