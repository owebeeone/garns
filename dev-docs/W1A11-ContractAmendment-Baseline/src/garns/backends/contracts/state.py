"""Pure lifecycle, cancellation, publication, and worker-fence models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .values import ContractRefusal, QualifiedDeployment, RefusalCode, RevisionCursor, TransactionIdentity
from .authority import RuntimeAuthority


class CommitKnowledge(str, Enum):
    KNOWN_ABORTED = "known_aborted"
    KNOWN_COMMITTED = "known_committed"
    INDETERMINATE = "indeterminate"


class ReconcileFinding(str, Enum):
    COMMITTED = "committed"
    ABORTED = "aborted"
    STILL_IN_FLIGHT = "still_in_flight"
    NOT_FOUND_NOT_FINAL = "not_found_not_final"


class OperationPhase(str, Enum):
    QUEUED = "queued"
    STATEMENT = "statement"
    WRITES_APPLIED = "writes_applied"
    ROLLBACK_REQUESTED = "rollback_requested"
    COMMIT_REQUESTED = "commit_requested"


class AbortEvidence(str, Enum):
    NOT_STARTED = "not_started"
    ROLLBACK_CONFIRMED = "rollback_confirmed"
    AUTHORITATIVE_ABORT_RECORD = "authoritative_abort_record"
    NONE = "none"
    ROLLBACK_ACK_LOST = "rollback_ack_lost"
    CONNECTION_LOST = "connection_lost"
    CLEANUP_TIMEOUT = "cleanup_timeout"


class ConnectionDisposition(str, Enum):
    RETURN_SANITIZED = "return_sanitized"
    DISCARD = "discard"


class Lifecycle(str, Enum):
    NEW = "new"
    OPEN = "open"
    DRAINING = "draining"
    CLOSED = "closed"
    FAILED = "failed"


class TransactionPhase(str, Enum):
    OWNED = "owned"
    ACTIVE = "active"
    COMMIT_REQUESTED = "commit_requested"
    TERMINAL = "terminal"


class CloseKnowledge(str, Enum):
    CLOSED = "closed"
    UNRESOLVED = "unresolved"
    NONQUIESCENT = "nonquiescent"


@dataclass(frozen=True, slots=True)
class CommitOutcome:
    knowledge: CommitKnowledge
    transaction: TransactionIdentity
    revision: RevisionCursor | None = None

    def __post_init__(self) -> None:
        _validate_commit_outcome(self)


def _validate_commit_outcome(outcome: CommitOutcome) -> None:
    if type(outcome.knowledge) is not CommitKnowledge:
        raise ValueError("commit knowledge must be a declared CommitKnowledge member")
    if type(outcome.transaction) is not TransactionIdentity:
        raise ValueError("commit outcome requires a transaction identity")
    if outcome.revision is not None and type(outcome.revision) is not RevisionCursor:
        raise ValueError("commit revision must be a revision cursor")
    if outcome.knowledge is CommitKnowledge.KNOWN_COMMITTED:
        if outcome.revision is None:
            raise ValueError("known commit requires its durable revision")
        if outcome.revision.scope != outcome.transaction.scope:
            raise ValueError("commit revision must be in transaction scope")
    elif outcome.revision is not None:
        raise ValueError("only a known commit carries its durable revision")


@dataclass(frozen=True, slots=True)
class CloseOutcome:
    knowledge: CloseKnowledge
    unresolved: tuple[TransactionIdentity, ...] = ()

    def __post_init__(self) -> None:
        if type(self.knowledge) is not CloseKnowledge:
            raise ValueError("close knowledge must be a declared CloseKnowledge member")
        unresolved = tuple(self.unresolved)
        if any(type(transaction) is not TransactionIdentity for transaction in unresolved):
            raise ValueError("unresolved work must contain transaction identities")
        object.__setattr__(self, "unresolved", unresolved)
        if self.knowledge is CloseKnowledge.CLOSED and self.unresolved:
            raise ValueError("closed outcome cannot retain unresolved work")
        if self.knowledge is CloseKnowledge.UNRESOLVED and not self.unresolved:
            raise ValueError("unresolved close must name transactions")


_LIFECYCLE_EDGES = {
    Lifecycle.NEW: frozenset({Lifecycle.OPEN, Lifecycle.FAILED, Lifecycle.CLOSED}),
    Lifecycle.OPEN: frozenset({Lifecycle.DRAINING, Lifecycle.FAILED}),
    Lifecycle.DRAINING: frozenset({Lifecycle.CLOSED, Lifecycle.FAILED}),
    Lifecycle.CLOSED: frozenset(), Lifecycle.FAILED: frozenset({Lifecycle.CLOSED}),
}


def transition(current: Lifecycle, target: Lifecycle) -> Lifecycle:
    if target not in _LIFECYCLE_EDGES[current]:
        raise ValueError(f"illegal lifecycle transition: {current.value} -> {target.value}")
    return target


def cancellation_outcome(transaction: TransactionIdentity, phase: OperationPhase,
                         evidence: AbortEvidence) -> CommitOutcome:
    if type(phase) is not OperationPhase or type(evidence) is not AbortEvidence:
        raise ValueError("cancellation requires declared phase and evidence members")
    aborted = {
        (OperationPhase.QUEUED, AbortEvidence.NOT_STARTED),
        (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.ROLLBACK_CONFIRMED),
    }
    indeterminate = {
        (OperationPhase.STATEMENT, AbortEvidence.NONE),
        (OperationPhase.STATEMENT, AbortEvidence.CONNECTION_LOST),
        (OperationPhase.STATEMENT, AbortEvidence.CLEANUP_TIMEOUT),
        (OperationPhase.WRITES_APPLIED, AbortEvidence.NONE),
        (OperationPhase.WRITES_APPLIED, AbortEvidence.CONNECTION_LOST),
        (OperationPhase.WRITES_APPLIED, AbortEvidence.CLEANUP_TIMEOUT),
        (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.NONE),
        (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.ROLLBACK_ACK_LOST),
        (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.CONNECTION_LOST),
        (OperationPhase.ROLLBACK_REQUESTED, AbortEvidence.CLEANUP_TIMEOUT),
        (OperationPhase.COMMIT_REQUESTED, AbortEvidence.NONE),
        (OperationPhase.COMMIT_REQUESTED, AbortEvidence.CONNECTION_LOST),
        (OperationPhase.COMMIT_REQUESTED, AbortEvidence.CLEANUP_TIMEOUT),
    }
    pair = (phase, evidence)
    if pair in aborted:
        return CommitOutcome(CommitKnowledge.KNOWN_ABORTED, transaction)
    if pair in indeterminate:
        return CommitOutcome(CommitKnowledge.INDETERMINATE, transaction)
    raise ValueError(f"invalid cancellation phase/evidence: {phase.value}/{evidence.value}")


def reconcile(transaction: TransactionIdentity, finding: ReconcileFinding,
              revision: RevisionCursor | None = None) -> CommitOutcome:
    if type(finding) is not ReconcileFinding:
        raise ValueError("reconciliation requires a declared finding member")
    if finding is ReconcileFinding.COMMITTED:
        if revision is None or revision.scope != transaction.scope:
            raise ValueError("committed reconciliation requires a revision in transaction scope")
        return CommitOutcome(CommitKnowledge.KNOWN_COMMITTED, transaction, revision)
    if finding is ReconcileFinding.ABORTED:
        if revision is not None:
            raise ValueError("aborted reconciliation cannot carry a revision")
        return CommitOutcome(CommitKnowledge.KNOWN_ABORTED, transaction)
    if revision is not None:
        raise ValueError("unresolved reconciliation cannot carry a revision")
    return CommitOutcome(CommitKnowledge.INDETERMINATE, transaction)


def connection_disposition(*, protocol_idle: bool, transaction_idle: bool,
                           session_sanitized: bool) -> ConnectionDisposition:
    if protocol_idle and transaction_idle and session_sanitized:
        return ConnectionDisposition.RETURN_SANITIZED
    return ConnectionDisposition.DISCARD


class TransactionUseGuard:
    __slots__ = ("_authority", "_owner", "phase", "_in_call")
    def __init__(self, authority: RuntimeAuthority) -> None:
        self._authority = authority
        self._owner = authority.capture_task_owner()
        self.phase = TransactionPhase.OWNED
        self._in_call = False

    def enter(self, *, nested: bool = False) -> None:
        if not self._authority.is_current_task(self._owner) or self._in_call:
            raise ContractRefusal(RefusalCode.CONCURRENT_TRANSACTION_USE, "transaction has one active owner")
        if nested:
            raise ContractRefusal(RefusalCode.NESTED_TRANSACTION_UNSUPPORTED, "nested transactions are unsupported")
        if self.phase is TransactionPhase.TERMINAL:
            raise ValueError("terminal transaction cannot be used")
        self._in_call = True
        self.phase = TransactionPhase.ACTIVE

    def leave(self) -> None:
        if not self._in_call:
            raise ValueError("transaction call is not active")
        self._in_call = False


@dataclass
class CommitOrderedPublication:
    scope: QualifiedDeployment
    generation: int = 1
    _revision: int = 0
    _published: dict[TransactionIdentity, tuple[str, RevisionCursor]] = field(default_factory=dict)

    @property
    def cursor(self) -> RevisionCursor:
        return RevisionCursor(self.scope, self.generation, self._revision)

    def publish_committed(self, transaction: TransactionIdentity, payload_digest: str) -> RevisionCursor:
        if transaction.scope != self.scope or not payload_digest:
            raise ValueError("qualified scope and payload digest are required")
        prior = self._published.get(transaction)
        if prior is not None:
            if prior[0] != payload_digest:
                raise ContractRefusal(RefusalCode.TRANSACTION_IDENTITY_CONFLICT, "identity already used for another payload")
            return prior[1]
        self._revision += 1
        cursor = self.cursor
        self._published[transaction] = (payload_digest, cursor)
        return cursor

    def change_generation(self) -> RevisionCursor:
        self.generation += 1
        self._revision = 0
        return self.cursor

    def compact_to(self, floor: RevisionCursor) -> None:
        if floor.scope != self.scope:
            raise ValueError("retention floor belongs to another scope")
        # Durable identity outcomes intentionally survive generation/retention.


@dataclass
class WorkerCommitFence:
    """A non-killable worker may finish work, but cannot cross a late commit fence."""

    _shutdown_fenced: bool = False
    _begun: set[TransactionIdentity] = field(default_factory=set)
    _commit_requested: set[TransactionIdentity] = field(default_factory=set)
    _resolved: dict[TransactionIdentity, CommitOutcome] = field(default_factory=dict)

    def begin(self, transaction: TransactionIdentity) -> None:
        if self._shutdown_fenced:
            raise ContractRefusal(RefusalCode.DEADLINE_EXCEEDED, "worker is fenced")
        if transaction in self._begun or transaction in self._resolved:
            raise ContractRefusal(RefusalCode.TRANSACTION_IDENTITY_CONFLICT,
                                  "transaction identity is active or terminal")
        self._begun.add(transaction)

    def request_commit(self, transaction: TransactionIdentity) -> None:
        if transaction not in self._begun:
            raise ValueError("transaction was not begun")
        if self._shutdown_fenced:
            raise ContractRefusal(RefusalCode.DEADLINE_EXCEEDED, "shutdown forbids late commit")
        self._commit_requested.add(transaction)

    def start_shutdown(self) -> None:
        self._shutdown_fenced = True

    def close_outcome(self, quiescent: bool) -> CloseOutcome:
        if type(quiescent) is not bool:
            raise ValueError("quiescence must be an exact boolean")
        ordered = tuple(sorted(self._begun, key=lambda tx: (tx.scope.world, tx.scope.deployment, tx.client_id)))
        if not quiescent:
            return CloseOutcome(CloseKnowledge.NONQUIESCENT, ordered)
        if not ordered:
            return CloseOutcome(CloseKnowledge.CLOSED)
        return CloseOutcome(CloseKnowledge.UNRESOLVED, ordered)

    def finish_without_commit(self, transaction: TransactionIdentity,
                              outcome: CommitOutcome) -> None:
        """Finish only pre-commit work with matching authoritative abort evidence."""
        if transaction in self._commit_requested:
            raise ValueError("commit-requested work requires terminal resolution")
        self._resolve_terminal(transaction, outcome, require_commit_request=False)

    def resolve(self, transaction: TransactionIdentity, outcome: CommitOutcome) -> None:
        """Consume a matching terminal outcome; retain indeterminate work."""
        if transaction not in self._commit_requested and transaction not in self._resolved:
            raise ValueError("transaction has no commit request to resolve")
        self._resolve_terminal(transaction, outcome, require_commit_request=True)

    def _resolve_terminal(self, transaction: TransactionIdentity, outcome: CommitOutcome,
                          *, require_commit_request: bool) -> None:
        _validate_commit_outcome(outcome)
        if outcome.transaction != transaction:
            raise ValueError("outcome belongs to another transaction")
        prior = self._resolved.get(transaction)
        if prior is not None:
            if prior != outcome:
                raise ValueError("transaction already has a different terminal outcome")
            return
        if transaction not in self._begun:
            raise ValueError("transaction was not begun")
        if outcome.knowledge is CommitKnowledge.INDETERMINATE:
            return
        if not require_commit_request and outcome.knowledge is not CommitKnowledge.KNOWN_ABORTED:
            raise ValueError("pre-commit completion requires a known abort")
        self._resolved[transaction] = outcome
        self._begun.remove(transaction)
        self._commit_requested.discard(transaction)
