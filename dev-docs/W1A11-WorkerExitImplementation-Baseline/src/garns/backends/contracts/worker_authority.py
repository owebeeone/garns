"""Issuer-private exact-command worker authorization reference contract."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar
import weakref

from .admission import OperationIdentity, ReadOperationLease
from .authority import RuntimeAuthority, TrustedContext
from .semantic import BindingIdentity
from .values import Capability, ContractRefusal, RefusalCode


_WORKER_AUTHORIZATION_SEAL = object()


class WorkerCommandAuthorization:
    """Empty issuer-private identity; it never contains a public context."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not WorkerCommandAuthorization or seal is not _WORKER_AUTHORIZATION_SEAL:
            raise TypeError("worker command authorization is issuer-created")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _WORKER_AUTHORIZATION_SEAL:
            raise TypeError("worker command authorization is issuer-created")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("WorkerCommandAuthorization is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("WorkerCommandAuthorization is immutable")

    def __repr__(self) -> str:
        return "WorkerCommandAuthorization(<opaque identity>)"

    def __copy__(self):
        raise TypeError("WorkerCommandAuthorization cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("WorkerCommandAuthorization cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("WorkerCommandAuthorization cannot be serialized")


@dataclass(slots=True)
class _WorkerRecord:
    context: TrustedContext
    context_owner: object
    capability: Capability
    runtime_identity: object
    operation: OperationIdentity
    lease: ReadOperationLease
    command_identity: object
    worker_identity: object
    binding: BindingIdentity
    remaining_ordinals: set[int]
    consumed_ordinals: set[int] = field(default_factory=set)
    revoked: bool = False


EffectResult = TypeVar("EffectResult")


class WorkerAuthorizationIssuer:
    """Pure issuer-owned registry; callers never provide claims or freshness."""

    __slots__ = ("_authority", "_dispatch_owner", "_live_operation", "_records")

    def __init__(
        self,
        authority: RuntimeAuthority,
        dispatch_owner: object,
        live_operation: Callable[[OperationIdentity, ReadOperationLease, object, object, BindingIdentity, WorkerCommandAuthorization], bool],
    ) -> None:
        self._authority = authority
        self._dispatch_owner = dispatch_owner
        self._live_operation = live_operation
        self._records: weakref.WeakKeyDictionary[WorkerCommandAuthorization, _WorkerRecord]
        self._records = weakref.WeakKeyDictionary()

    def _issue_for_dispatch(
        self,
        dispatch_owner: object,
        context: TrustedContext,
        capability: Capability,
        runtime_identity: object,
        operation: OperationIdentity,
        lease: ReadOperationLease,
        command_identity: object,
        worker_identity: object,
        binding: BindingIdentity,
        effect_ordinals: tuple[int, ...],
    ) -> WorkerCommandAuthorization:
        if dispatch_owner is not self._dispatch_owner:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "dispatch issuer is not authoritative")
        if type(operation) is not OperationIdentity or type(lease) is not ReadOperationLease:
            raise TypeError("dispatch requires exact operation and lease identities")
        if type(binding) is not BindingIdentity or binding.scope != operation.deployment:
            raise ValueError("dispatch binding must match the operation deployment")
        if binding.generation != operation.generation:
            raise ValueError("dispatch binding generation must match the operation")
        if runtime_identity is not operation.runtime_identity:
            raise ValueError("dispatch runtime must be the exact operation runtime")
        if command_identity is None or worker_identity is None:
            raise ValueError("dispatch command and worker identities are required")
        ordinals = tuple(effect_ordinals)
        if not ordinals or any(type(item) is not int or item < 1 for item in ordinals):
            raise ValueError("effect ordinals must be finite positive exact integers")
        if len(set(ordinals)) != len(ordinals):
            raise ValueError("effect ordinals must be unique")
        issued = self._authority._worker_dispatch_record(
            context,
            scope=operation.deployment,
            capability=capability,
        )
        authorization = WorkerCommandAuthorization(_WORKER_AUTHORIZATION_SEAL)
        self._records[authorization] = _WorkerRecord(
            context=context,
            context_owner=issued.owner_task,
            capability=capability,
            runtime_identity=runtime_identity,
            operation=operation,
            lease=lease,
            command_identity=command_identity,
            worker_identity=worker_identity,
            binding=binding,
            remaining_ordinals=set(ordinals),
        )
        return authorization

    def run_effect(
        self,
        authorization: WorkerCommandAuthorization,
        runtime_identity: object,
        operation: OperationIdentity,
        lease: ReadOperationLease,
        command_identity: object,
        worker_identity: object,
        binding: BindingIdentity,
        ordinal: int,
        effect: Callable[[], EffectResult],
    ) -> EffectResult:
        record = self._validate_exact_record(
            authorization,
            runtime_identity,
            operation,
            lease,
            command_identity,
            worker_identity,
            binding,
        )
        if type(ordinal) is not int or ordinal not in record.remaining_ordinals:
            code = (
                RefusalCode.EFFECT_ORDINAL_REUSED
                if ordinal in record.consumed_ordinals
                else RefusalCode.WORKER_AUTHORITY_INVALID
            )
            raise ContractRefusal(code, "effect ordinal is unavailable")
        self._authority._validate_worker_source(
            record.context,
            scope=record.operation.deployment,
            capability=record.capability,
            owner_task=record.context_owner,
        )
        if not self._authority.is_current_task(record.worker_identity):
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "assigned worker is not current")
        if not self._live_operation(
            operation, lease, command_identity, worker_identity, binding, authorization,
        ):
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "operation owner or fence is not live")
        record.remaining_ordinals.remove(ordinal)
        record.consumed_ordinals.add(ordinal)
        return effect()

    def context_owner(self, authorization: WorkerCommandAuthorization | None) -> object:
        if type(authorization) is not WorkerCommandAuthorization:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "authorization is not exact")
        record = self._records.get(authorization)
        if record is None or record.revoked:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "worker authorization is not live")
        return record.context_owner

    def revoke(self, authorization: WorkerCommandAuthorization) -> None:
        if type(authorization) is not WorkerCommandAuthorization:
            return
        record = self._records.get(authorization)
        if record is not None:
            record.revoked = True
            record.remaining_ordinals.clear()

    def _validate_exact_record(
        self,
        authorization: WorkerCommandAuthorization,
        runtime_identity: object,
        operation: OperationIdentity,
        lease: ReadOperationLease,
        command_identity: object,
        worker_identity: object,
        binding: BindingIdentity,
    ) -> _WorkerRecord:
        if type(authorization) is not WorkerCommandAuthorization:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "not an issued worker authorization")
        record = self._records.get(authorization)
        if record is None or record.revoked:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "worker authorization is not live")
        exact = (
            runtime_identity is record.runtime_identity
            and operation == record.operation
            and lease is record.lease
            and command_identity is record.command_identity
            and worker_identity is record.worker_identity
            and binding == record.binding
        )
        if not exact:
            raise ContractRefusal(RefusalCode.WORKER_AUTHORITY_INVALID, "worker authorization binding mismatch")
        return record
