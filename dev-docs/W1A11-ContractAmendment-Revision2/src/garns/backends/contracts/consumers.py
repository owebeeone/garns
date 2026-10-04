"""Sealed exact plan consumers and closed reference step products."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import weakref

from .admission import OperationIdentity, PlanStep
from .semantic import Plan
from .values import ContractRefusal, FrozenMap, ParameterValues, RefusalCode


_CONSUMER_SEAL = object()


class ClosedPlanConsumer:
    """Empty identity for an issuer-owned consumer that never exposes a Plan."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not ClosedPlanConsumer or seal is not _CONSUMER_SEAL:
            raise TypeError("closed plan consumers are issuer-created")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _CONSUMER_SEAL:
            raise TypeError("closed plan consumers are issuer-created")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("ClosedPlanConsumer is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("ClosedPlanConsumer is immutable")

    def __repr__(self) -> str:
        return "ClosedPlanConsumer(<opaque identity>)"

    def __copy__(self):
        raise TypeError("ClosedPlanConsumer cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("ClosedPlanConsumer cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("ClosedPlanConsumer cannot be serialized")


@dataclass(frozen=True, slots=True)
class ClosedStepProduct:
    """Only closed data crosses the lexical private-plan boundary."""

    operation: OperationIdentity
    step: PlanStep
    label: str
    read_qid: str
    plan_digest: str
    parameters: FrozenMap

    def __post_init__(self) -> None:
        if type(self.operation) is not OperationIdentity or type(self.step) is not PlanStep:
            raise TypeError("step products require exact operation and step values")
        for name in ("label", "read_qid", "plan_digest"):
            if type(getattr(self, name)) is not str or not getattr(self, name):
                raise ValueError(f"{name} is required")
        if type(self.parameters) is not FrozenMap:
            raise TypeError("step products require detached frozen parameters")


@dataclass(frozen=True, slots=True)
class _ConsumerRecord:
    label: str
    effect: Callable[[ClosedStepProduct], None] | None


class ReferenceConsumerIssuer:
    """Issuer-private consumer registry used by the deterministic verifier."""

    __slots__ = ("_records",)

    def __init__(self) -> None:
        self._records: weakref.WeakKeyDictionary[ClosedPlanConsumer, _ConsumerRecord]
        self._records = weakref.WeakKeyDictionary()

    def issue(
        self,
        label: str,
        effect: Callable[[ClosedStepProduct], None] | None = None,
    ) -> ClosedPlanConsumer:
        if type(label) is not str or not label:
            raise ValueError("consumer label is required")
        if effect is not None and not callable(effect):
            raise TypeError("consumer effect must be callable")
        consumer = ClosedPlanConsumer(_CONSUMER_SEAL)
        self._records[consumer] = _ConsumerRecord(label, effect)
        return consumer

    def owns(self, consumer: object) -> bool:
        """Check exact issuer ownership without touching a private plan or effect."""

        return type(consumer) is ClosedPlanConsumer and consumer in self._records

    def consume(
        self,
        consumer: ClosedPlanConsumer,
        plan: Plan,
        parameters: ParameterValues,
        operation: OperationIdentity,
        step: PlanStep,
    ) -> ClosedStepProduct:
        if type(consumer) is not ClosedPlanConsumer:
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "exact closed consumer is required")
        record = self._records.get(consumer)
        if record is None:
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "consumer belongs to another issuer")
        if type(plan) is not Plan or type(parameters) is not ParameterValues:
            raise TypeError("issuer consumption requires private plan and pinned parameters")
        product = ClosedStepProduct(
            operation,
            step,
            record.label,
            plan.read_qid,
            plan.root.canonical_digest,
            parameters.values,
        )
        if record.effect is not None:
            record.effect(product)
        return product
