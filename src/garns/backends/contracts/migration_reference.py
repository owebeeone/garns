"""Sealed migration, membership, request and phase-proof identities."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .semantic import BindingIdentity
from .values import QualifiedDeployment


class AttemptPhase(str, Enum):
    DRAINING_OLD = "draining_old"
    MIGRATING_PRE_EFFECT = "migrating_pre_effect"
    EFFECT_BEGUN = "effect_begun"


class ParticipantState(str, Enum):
    UNJOINED = "unjoined"
    JOINED = "joined"
    LEAVE_PENDING = "leave_pending"
    LEFT = "left"


class _EmptyIdentity:
    __slots__ = ("__weakref__",)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __repr__(self) -> str:
        return f"{type(self).__name__}(<opaque identity>)"

    def __copy__(self):
        raise TypeError(f"{type(self).__name__} cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError(f"{type(self).__name__} cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError(f"{type(self).__name__} cannot be serialized")


def _identity_type(name: str):
    seal = object()

    def new(cls, supplied: object = None):
        if supplied is not seal:
            raise TypeError(f"{name} is coordinator-issued")
        return object.__new__(cls)

    return type(name, (_EmptyIdentity,), {
        "__slots__": (),
        "__new__": new,
        "_issuer_seal": seal,
    })


MigrationAttempt = _identity_type("MigrationAttempt")
ParticipantMembership = _identity_type("ParticipantMembership")
MigrationBarrierAcknowledgement = _identity_type("MigrationBarrierAcknowledgement")
MigrationRequestIdentity = _identity_type("MigrationRequestIdentity")
MigrationNoEffectProof = _identity_type("MigrationNoEffectProof")
LifetimeOpenRecord = _identity_type("LifetimeOpenRecord")

# Historical internal spelling retained as a type alias, not a second identity.
MigrationParticipant = ParticipantMembership


def _issue(identity_type):
    return identity_type(identity_type._issuer_seal)


@dataclass(slots=True)
class MigrationAttemptRecord:
    deployment: QualifiedDeployment
    old_binding: BindingIdentity
    protocol_epoch: int
    admission_epoch: int
    required: frozenset[ParticipantMembership]
    phase: AttemptPhase
    phase_serial: int
    phase_request: MigrationRequestIdentity
    acknowledged: dict[ParticipantMembership, MigrationBarrierAcknowledgement] = field(default_factory=dict)
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
    phase: AttemptPhase
    phase_serial: int
    phase_request: MigrationRequestIdentity
    requested_binding: BindingIdentity | None


def issue_attempt() -> MigrationAttempt:
    return _issue(MigrationAttempt)


def issue_participant() -> ParticipantMembership:
    return _issue(ParticipantMembership)


def issue_acknowledgement() -> MigrationBarrierAcknowledgement:
    return _issue(MigrationBarrierAcknowledgement)


def issue_request() -> MigrationRequestIdentity:
    return _issue(MigrationRequestIdentity)


def issue_no_effect_proof() -> MigrationNoEffectProof:
    return _issue(MigrationNoEffectProof)


def issue_lifetime_open() -> LifetimeOpenRecord:
    return _issue(LifetimeOpenRecord)
