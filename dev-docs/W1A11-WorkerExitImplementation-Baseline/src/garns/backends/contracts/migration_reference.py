"""Sealed identities for deterministic migration-attempt contract evidence.

These empty values and private records do not implement durable or cross-process
coordination.  They make attempt, participant, acknowledgement, and no-effect
proof identity explicit in the single-process reference model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .semantic import BindingIdentity
from .values import QualifiedDeployment


_ATTEMPT_SEAL = object()
_PARTICIPANT_SEAL = object()
_ACK_SEAL = object()
_NO_EFFECT_SEAL = object()


class _EmptyIdentity:
    __slots__ = ("__weakref__",)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __copy__(self):
        raise TypeError(f"{type(self).__name__} cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError(f"{type(self).__name__} cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError(f"{type(self).__name__} cannot be serialized")


class MigrationAttempt(_EmptyIdentity):
    __slots__ = ()

    def __new__(cls, seal: object = None):
        if cls is not MigrationAttempt or seal is not _ATTEMPT_SEAL:
            raise TypeError("migration attempts are coordinator-issued")
        return super().__new__(cls)


class MigrationParticipant(_EmptyIdentity):
    __slots__ = ()

    def __new__(cls, seal: object = None):
        if cls is not MigrationParticipant or seal is not _PARTICIPANT_SEAL:
            raise TypeError("migration participants are coordinator-issued")
        return super().__new__(cls)


class MigrationBarrierAcknowledgement(_EmptyIdentity):
    __slots__ = ()

    def __new__(cls, seal: object = None):
        if cls is not MigrationBarrierAcknowledgement or seal is not _ACK_SEAL:
            raise TypeError("migration acknowledgements are coordinator-issued")
        return super().__new__(cls)


class MigrationNoEffectProof(_EmptyIdentity):
    __slots__ = ()

    def __new__(cls, seal: object = None):
        if cls is not MigrationNoEffectProof or seal is not _NO_EFFECT_SEAL:
            raise TypeError("migration no-effect proofs are coordinator-issued")
        return super().__new__(cls)


@dataclass(slots=True)
class MigrationAttemptRecord:
    deployment: QualifiedDeployment
    old_binding: BindingIdentity
    protocol_epoch: int
    admission_epoch: int
    required: frozenset[MigrationParticipant]
    acknowledged: dict[MigrationParticipant, MigrationBarrierAcknowledgement] = field(default_factory=dict)
    requested_binding: BindingIdentity | None = None
    effect_begun: bool = False
    closed: bool = False


@dataclass(frozen=True, slots=True)
class MigrationNoEffectRecord:
    attempt: MigrationAttempt
    deployment: QualifiedDeployment
    old_binding: BindingIdentity
    protocol_epoch: int
    admission_epoch: int
    exclusive_request_released_digest: str
    no_effect_outcome_digest: str


def issue_attempt() -> MigrationAttempt:
    return MigrationAttempt(_ATTEMPT_SEAL)


def issue_participant() -> MigrationParticipant:
    return MigrationParticipant(_PARTICIPANT_SEAL)


def issue_acknowledgement() -> MigrationBarrierAcknowledgement:
    return MigrationBarrierAcknowledgement(_ACK_SEAL)


def issue_no_effect_proof() -> MigrationNoEffectProof:
    return MigrationNoEffectProof(_NO_EFFECT_SEAL)
