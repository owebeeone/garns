"""Complete async backend protocols; concrete public names remain provisional."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .authority import AuthorityBoundIterator, TrustedContext
from .operations import (
    GovernedMutation, LedgerPublication, MigrationLock,
    MigrationRequest, MigrationResult, SchemaSnapshot,
)
from .semantic import BindingIdentity, Plan
from .state import CloseOutcome, CommitOutcome
from .values import (
    BackendCapabilities, DeadlinePolicy, Delivery, FrozenMap, ParameterValues, RefetchRequired,
    RevisionCursor, Snapshot, TransactionIdentity,
)


@runtime_checkable
class AsyncTransaction(Protocol):
    identity: TransactionIdentity

    async def mutate(self, mutation: GovernedMutation, context: TrustedContext) -> None: ...
    async def commit(self, context: TrustedContext) -> CommitOutcome | LedgerPublication: ...
    async def rollback(self) -> CommitOutcome: ...
    async def reconcile(self, context: TrustedContext) -> CommitOutcome: ...


@runtime_checkable
class AsyncConnection(Protocol):
    capabilities: BackendCapabilities
    binding: BindingIdentity

    async def execute(self, plan: Plan, parameters: ParameterValues,
                      context: TrustedContext) -> tuple[FrozenMap, ...]: ...
    async def begin(self, identity: TransactionIdentity, context: TrustedContext) -> AsyncTransaction: ...
    async def consistent_snapshot(self, plan: Plan, parameters: ParameterValues,
                                  context: TrustedContext) -> Snapshot | RefetchRequired: ...
    async def inspect_schema(self, context: TrustedContext) -> SchemaSnapshot: ...
    async def acquire_migration_lock(self, request: MigrationRequest,
                                     context: TrustedContext,
                                     deadline: float) -> MigrationLock: ...
    async def apply_migration(self, lock: MigrationLock, request: MigrationRequest,
                              context: TrustedContext) -> MigrationResult: ...
    async def read_ledger(self, after: RevisionCursor, context: TrustedContext) -> tuple[LedgerPublication, ...]: ...
    async def sanitize(self, deadline: float) -> bool: ...
    async def close(self, deadline: float) -> CloseOutcome: ...


@runtime_checkable
class AsyncPool(Protocol):
    async def acquire(self, context: TrustedContext, deadline: float) -> AsyncConnection: ...
    async def release(self, connection: AsyncConnection, context: TrustedContext,
                      deadline: float) -> None: ...
    async def close(self, deadline: float, force: bool = False) -> CloseOutcome: ...


@runtime_checkable
class AsyncSubscription(Protocol):
    cursor: RevisionCursor

    def bind_delivery(self, context: TrustedContext) -> AuthorityBoundIterator[Delivery | RefetchRequired]: ...
    async def aclose(self, deadline: float) -> CloseOutcome: ...


@runtime_checkable
class AsyncBackend(Protocol):
    capabilities: BackendCapabilities

    async def open(self, context: TrustedContext, deadlines: DeadlinePolicy) -> AsyncPool: ...
    async def open_privileged(self, binding: BindingIdentity,
                              deadlines: DeadlinePolicy) -> AsyncPool: ...
    async def subscribe(self, plan: Plan, parameters: ParameterValues,
                        context: TrustedContext, after: RevisionCursor | None) -> AsyncSubscription: ...
