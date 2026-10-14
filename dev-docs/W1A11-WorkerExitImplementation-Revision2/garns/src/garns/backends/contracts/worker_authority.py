"""Sealed worker-exit identities and the lifetime-owner call facade.

This module owns no mutable worker or lease state. The deterministic lifetime
registry is the sole mutation owner; this module supplies exact empty identity
types and a narrow facade used by a bound executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class WorkerCommandState(str, Enum):
    QUEUED = "queued"
    QUEUE_REMOVED = "queue_removed"
    RUNNING_IDLE = "running_idle"
    EFFECT_IN_FLIGHT = "effect_in_flight"
    SUCCESS_PENDING = "success_pending"
    CONTAINED = "contained"
    QUIESCENT_SUCCESS = "quiescent_success"
    QUIESCENT_CONTAINED = "quiescent_contained"
    RESULT_ACCEPTED = "result_accepted"


class EffectKnowledge(str, Enum):
    NOT_BEGUN = "not_begun"
    RETURNED = "returned"
    BEGUN_UNCERTAIN = "begun_uncertain"


class WorkerExitKind(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    CANCEL = "cancel"


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
            raise TypeError(f"{name} is issuer-created")
        return object.__new__(cls)

    return type(name, (_EmptyIdentity,), {
        "__slots__": (),
        "__new__": new,
        "_issuer_seal": seal,
    })


WorkerCommandAuthorization = _identity_type("WorkerCommandAuthorization")
WorkerEffectReservation = _identity_type("WorkerEffectReservation")
WorkerExitReceipt = _identity_type("WorkerExitReceipt")
WorkerStopReceipt = _identity_type("WorkerStopReceipt")
ReceivingTaskLifecycleObservation = _identity_type("ReceivingTaskLifecycleObservation")
RuntimeContinuationOwner = _identity_type("RuntimeContinuationOwner")
WorkerContainmentOwner = _identity_type("WorkerContainmentOwner")
ClosedWorkerCommand = _identity_type("ClosedWorkerCommand")
ClosedWorkerResult = _identity_type("ClosedWorkerResult")
ClosedWorkerFailure = _identity_type("ClosedWorkerFailure")
DeliveryPublicationCandidate = _identity_type("DeliveryPublicationCandidate")
DeliverySettlementReceipt = _identity_type("DeliverySettlementReceipt")
DeliveryRetirementReceipt = _identity_type("DeliveryRetirementReceipt")
DeliveryStopObservation = _identity_type("DeliveryStopObservation")


def _issue(identity_type):
    return identity_type(identity_type._issuer_seal)


@dataclass(frozen=True, slots=True)
class WorkerCommandSpec:
    """Trusted setup description for one closed command slot."""

    label: str
    required_effects: tuple[int, ...]
    optional_effects: tuple[int, ...] = ()
    cleanup_steps: int = 0

    def __post_init__(self) -> None:
        if type(self.label) is not str or not self.label:
            raise ValueError("command label is required")
        required = tuple(self.required_effects)
        optional = tuple(self.optional_effects)
        all_ordinals = required + optional
        if not required or any(type(item) is not int or item < 1 for item in all_ordinals):
            raise ValueError("a command requires finite positive exact effect ordinals")
        if len(set(all_ordinals)) != len(all_ordinals):
            raise ValueError("effect ordinals must be unique across the command")
        if type(self.cleanup_steps) is not int or self.cleanup_steps < 0:
            raise ValueError("cleanup step count must be a nonnegative exact integer")
        object.__setattr__(self, "required_effects", required)
        object.__setattr__(self, "optional_effects", optional)


class WorkerAuthorizationIssuer:
    """Stateless executor facade; every call delegates to the lifetime owner."""

    __slots__ = ("_run_effect", "_context_owner", "_revoke")

    def __init__(
        self,
        run_effect: Callable[[WorkerCommandAuthorization, int], object],
        context_owner: Callable[[WorkerCommandAuthorization], object],
        revoke: Callable[[WorkerCommandAuthorization], None],
    ) -> None:
        self._run_effect = run_effect
        self._context_owner = context_owner
        self._revoke = revoke

    def run_effect(self, authorization: WorkerCommandAuthorization, ordinal: int) -> object:
        return self._run_effect(authorization, ordinal)

    def context_owner(self, authorization: WorkerCommandAuthorization) -> object:
        return self._context_owner(authorization)

    def revoke(self, authorization: WorkerCommandAuthorization) -> None:
        self._revoke(authorization)
