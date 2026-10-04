"""Runtime-owned authority, genuine contexts, and authority-bound delivery."""
from __future__ import annotations
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
import math, weakref
from typing import TypeVar
from .values import Capability, ContractRefusal, QualifiedDeployment, RefusalCode

@dataclass(frozen=True, slots=True)
class TrustedClaims:
    principal: str; writer: str; scope: QualifiedDeployment
    capabilities: frozenset[Capability]; context_id: str
    valid_until: float; invalidation_epoch: int
    def __post_init__(self) -> None:
        for name in ("principal", "writer", "context_id"):
            value = str(getattr(self, name)); object.__setattr__(self, name, value)
            if not value: raise ValueError(f"{name} is required")
        object.__setattr__(self, "scope", QualifiedDeployment(self.scope.world, self.scope.deployment))
        object.__setattr__(self, "capabilities", frozenset(Capability(x) for x in self.capabilities))
        if type(self.valid_until) not in {int, float} or type(self.valid_until) is bool: raise ValueError("validity must be numeric")
        object.__setattr__(self, "valid_until", float(self.valid_until))
        if not math.isfinite(self.valid_until): raise ValueError("validity must be finite")
        if type(self.invalidation_epoch) is not int or self.invalidation_epoch < 0: raise ValueError("epoch must be nonnegative")

_HANDLE_SEAL = object()

class TrustedContext:
    """Empty identity handle; all authority-bearing state lives in its issuer."""
    __slots__ = ("__weakref__",)
    def __new__(cls, seal=None):
        if seal is not _HANDLE_SEAL: raise TypeError("issued only by RuntimeAuthority")
        return super().__new__(cls)
    def __init__(self, seal=None) -> None:
        if seal is not _HANDLE_SEAL: raise TypeError("issued only by RuntimeAuthority")
    def __setattr__(self, name, value): raise AttributeError("TrustedContext is immutable")
    def __delattr__(self, name): raise AttributeError("TrustedContext is immutable")
    def __repr__(self): return "TrustedContext(<opaque identity>)"
    def __copy__(self): raise TypeError("TrustedContext cannot be copied")
    def __deepcopy__(self, memo): raise TypeError("TrustedContext cannot be deep-copied")
    def __reduce_ex__(self, protocol): raise TypeError("TrustedContext cannot be serialized")

@dataclass(frozen=True, slots=True)
class _Issued:
    claims: TrustedClaims; owner_task: object

class RuntimeAuthority:
    """Trusted setup injects providers; ordinary calls cannot override them."""
    __slots__ = ("_clock", "_epoch", "_current_task", "_issued")
    def __init__(self, clock: Callable[[], float], epoch: Callable[[], int], current_task: Callable[[], object]) -> None:
        self._clock, self._epoch, self._current_task = clock, epoch, current_task
        self._issued = weakref.WeakKeyDictionary()
    def issue(self, claims: TrustedClaims) -> TrustedContext:
        owner = self._current_task()
        if owner is None: raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, "issuance requires a live task owner")
        normalized = TrustedClaims(claims.principal, claims.writer, claims.scope, claims.capabilities, claims.context_id, claims.valid_until, claims.invalidation_epoch)
        context = TrustedContext(_HANDLE_SEAL)
        self._issued[context] = _Issued(normalized, owner); return context
    def validate(self, context: TrustedContext, *, scope: QualifiedDeployment, capability: Capability) -> TrustedClaims:
        if type(context) is not TrustedContext: raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, "not issued")
        record = self._issued.get(context)
        if record is None: raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, "not live issued instance")
        if self._current_task() is not record.owner_task: raise ContractRefusal(RefusalCode.CONTEXT_OWNER_MISMATCH, "another task owns context")
        claims = record.claims
        if scope != claims.scope: raise ContractRefusal(RefusalCode.SCOPE_MISMATCH, "scope mismatch")
        if self._clock() >= claims.valid_until or self._epoch() != claims.invalidation_epoch: raise ContractRefusal(RefusalCode.CONTEXT_EXPIRED, "expired or invalidated")
        if capability not in claims.capabilities: raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, f"missing {capability.value}")
        return claims
    def invalidate(self, context: TrustedContext) -> None:
        if type(context) is TrustedContext: self._issued.pop(context, None)
    def capture_task_owner(self) -> object:
        owner = self._current_task()
        if owner is None: raise ContractRefusal(RefusalCode.AUTHORITY_INVALID, "task owner is required")
        return owner
    def is_current_task(self, owner: object) -> bool:
        return owner is not None and self._current_task() is owner

T = TypeVar("T")
class AuthorityBoundIterator(AsyncIterator[T]):
    """The sole delivery graph: every ``__anext__`` validates before reading."""
    __slots__ = ("_authority", "_context", "_scope", "_capability", "_reader", "_closed")
    def __init__(self, authority: RuntimeAuthority, context: TrustedContext, scope: QualifiedDeployment, capability: Capability, reader: Callable[[], Awaitable[T]]) -> None:
        self._authority, self._context, self._scope = authority, context, scope
        self._capability, self._reader, self._closed = capability, reader, False
    def __aiter__(self): return self
    async def __anext__(self) -> T:
        if self._closed: raise StopAsyncIteration
        self._authority.validate(self._context, scope=self._scope, capability=self._capability)
        item = await self._reader()
        if self._closed: raise StopAsyncIteration
        self._authority.validate(self._context, scope=self._scope, capability=self._capability)
        return item
    def close(self) -> None: self._closed = True
    def renew(self, context: TrustedContext) -> "AuthorityBoundIterator[T]":
        self.close(); return AuthorityBoundIterator(self._authority, context, self._scope, self._capability, self._reader)

ContextIssuer = RuntimeAuthority
