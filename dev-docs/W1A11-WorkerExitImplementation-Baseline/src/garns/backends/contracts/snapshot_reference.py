"""Sealed deterministic snapshot candidates; no database provenance is claimed."""

from __future__ import annotations

from dataclasses import dataclass

from .admission import AdmittedReadHandle, OperationIdentity, ReadOperationLease
from .buffer_reference import SubscriptionRegistration
from .lifetime import ResourceIdentity
from .semantic import BindingIdentity
from .values import FrozenMap, ParameterValues, RevisionCursor


_INITIAL_SEAL = object()
_REFRESH_SEAL = object()


class _EmptyCandidate:
    __slots__ = ("__weakref__",)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError(f"{type(self).__name__} is immutable")

    def __copy__(self):
        raise TypeError(f"{type(self).__name__} cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError(f"{type(self).__name__} cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError(f"{type(self).__name__} cannot be serialized")


class InitialSnapshotCandidate(_EmptyCandidate):
    __slots__ = ()

    def __new__(cls, seal: object = None):
        if cls is not InitialSnapshotCandidate or seal is not _INITIAL_SEAL:
            raise TypeError("initial snapshot candidates are issuer-created")
        return super().__new__(cls)


class RefreshSnapshotCandidate(_EmptyCandidate):
    __slots__ = ()

    def __new__(cls, seal: object = None):
        if cls is not RefreshSnapshotCandidate or seal is not _REFRESH_SEAL:
            raise TypeError("refresh snapshot candidates are issuer-created")
        return super().__new__(cls)


@dataclass(frozen=True, slots=True)
class InitialSnapshotPublication:
    rows: tuple[FrozenMap, ...]
    watermark: RevisionCursor
    registration: SubscriptionRegistration


@dataclass(slots=True)
class _InitialRecord:
    lease: ReadOperationLease
    operation: OperationIdentity
    admission: AdmittedReadHandle
    parameters: FrozenMap
    binding: BindingIdentity
    plan_digest: str
    subscription: ResourceIdentity
    queue: ResourceIdentity
    rows: tuple[FrozenMap, ...]
    watermark: RevisionCursor
    consumed: bool = False


@dataclass(slots=True)
class _RefreshRecord:
    lease: ReadOperationLease
    operation: OperationIdentity
    admission: AdmittedReadHandle
    parameters: FrozenMap
    binding: BindingIdentity
    plan_digest: str
    registration: SubscriptionRegistration
    subscription: ResourceIdentity
    queue: ResourceIdentity
    previous: RevisionCursor
    triggered_by: RevisionCursor
    observed_through: RevisionCursor
    rows: tuple[FrozenMap, ...]
    durable_advancement: str
    consumed: bool = False


class ReferenceSnapshotRegistry:
    """Issuer-private candidate records produced by explicitly named fixtures."""

    def __init__(self) -> None:
        self._initial: dict[InitialSnapshotCandidate, _InitialRecord] = {}
        self._refresh: dict[RefreshSnapshotCandidate, _RefreshRecord] = {}

    def setup_initial(
        self, lease: ReadOperationLease, operation: OperationIdentity,
        admission: AdmittedReadHandle, parameters: ParameterValues,
        binding: BindingIdentity, plan_digest: str, subscription: ResourceIdentity,
        queue: ResourceIdentity, rows: tuple[FrozenMap, ...], watermark: RevisionCursor,
    ) -> InitialSnapshotCandidate:
        if type(rows) is not tuple or any(type(row) is not FrozenMap for row in rows):
            raise TypeError("initial snapshot rows must already be frozen")
        candidate = InitialSnapshotCandidate(_INITIAL_SEAL)
        self._initial[candidate] = _InitialRecord(
            lease, operation, admission, parameters.values, binding, plan_digest,
            subscription, queue, rows, watermark,
        )
        return candidate

    def initial_record(self, candidate: InitialSnapshotCandidate) -> _InitialRecord:
        if type(candidate) is not InitialSnapshotCandidate:
            raise TypeError("exact initial snapshot candidate is required")
        record = self._initial.get(candidate)
        if record is None or record.consumed:
            raise ValueError("initial snapshot candidate is unavailable")
        return record

    def consume_initial(self, record: _InitialRecord) -> None:
        if record.consumed:
            raise ValueError("initial snapshot candidate was already consumed")
        record.consumed = True

    def setup_refresh(
        self, lease: ReadOperationLease, operation: OperationIdentity,
        admission: AdmittedReadHandle, parameters: ParameterValues,
        binding: BindingIdentity, plan_digest: str,
        registration: SubscriptionRegistration, subscription: ResourceIdentity,
        queue: ResourceIdentity, previous: RevisionCursor,
        triggered_by: RevisionCursor, observed_through: RevisionCursor,
        rows: tuple[FrozenMap, ...], durable_advancement: str,
    ) -> RefreshSnapshotCandidate:
        if type(rows) is not tuple or any(type(row) is not FrozenMap for row in rows):
            raise TypeError("refresh snapshot rows must already be frozen")
        if type(durable_advancement) is not str or not durable_advancement:
            raise ValueError("refresh advancement digest is required")
        candidate = RefreshSnapshotCandidate(_REFRESH_SEAL)
        self._refresh[candidate] = _RefreshRecord(
            lease, operation, admission, parameters.values, binding, plan_digest,
            registration, subscription, queue, previous, triggered_by,
            observed_through, rows, durable_advancement,
        )
        return candidate

    def refresh_record(self, candidate: RefreshSnapshotCandidate) -> _RefreshRecord:
        if type(candidate) is not RefreshSnapshotCandidate:
            raise TypeError("exact refresh snapshot candidate is required")
        record = self._refresh.get(candidate)
        if record is None or record.consumed:
            raise ValueError("refresh snapshot candidate is unavailable")
        return record

    def consume_refresh(self, record: _RefreshRecord) -> None:
        if record.consumed:
            raise ValueError("refresh snapshot candidate was already consumed")
        record.consumed = True
