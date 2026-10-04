"""Sealed exact plan consumers and closed reference step products."""

from __future__ import annotations

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


_COMMAND_SEAL = object()


class ClosedDerivedCommand:
    """Empty identity for one parent-owned child or total-fetch command."""

    __slots__ = ("__weakref__",)

    def __new__(cls, seal: object = None):
        if cls is not ClosedDerivedCommand or seal is not _COMMAND_SEAL:
            raise TypeError("derived commands are issuer-created")
        return super().__new__(cls)

    def __init__(self, seal: object = None) -> None:
        if seal is not _COMMAND_SEAL:
            raise TypeError("derived commands are issuer-created")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("ClosedDerivedCommand is immutable")

    def __copy__(self):
        raise TypeError("ClosedDerivedCommand cannot be copied")

    def __deepcopy__(self, memo: object):
        raise TypeError("ClosedDerivedCommand cannot be deep-copied")

    def __reduce_ex__(self, protocol: int):
        raise TypeError("ClosedDerivedCommand cannot be serialized")


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


@dataclass(slots=True)
class _CommandRecord:
    operation: OperationIdentity
    step: PlanStep
    ordinal: int
    label: str
    consumed: bool = False


class ReferenceConsumerIssuer:
    """Issuer-private consumer registry used by the deterministic verifier."""

    __slots__ = ("_records", "_commands")

    def __init__(self) -> None:
        self._records: weakref.WeakKeyDictionary[ClosedPlanConsumer, _ConsumerRecord]
        self._records = weakref.WeakKeyDictionary()
        self._commands: weakref.WeakKeyDictionary[ClosedDerivedCommand, _CommandRecord]
        self._commands = weakref.WeakKeyDictionary()

    def issue(
        self,
        label: str,
    ) -> ClosedPlanConsumer:
        if type(label) is not str or not label:
            raise ValueError("consumer label is required")
        consumer = ClosedPlanConsumer(_CONSUMER_SEAL)
        self._records[consumer] = _ConsumerRecord(label)
        return consumer

    def issue_command(
        self,
        operation: OperationIdentity,
        step: PlanStep,
        ordinal: int,
        label: str,
    ) -> ClosedDerivedCommand:
        if type(operation) is not OperationIdentity:
            raise TypeError("derived command operation must be exact")
        if type(step) is not PlanStep or step not in {PlanStep.CHILD_FETCH, PlanStep.TOTAL_FETCH}:
            raise ValueError("derived command must be a child or total fetch")
        if type(ordinal) is not int or ordinal < 1:
            raise ValueError("derived command ordinal must be positive")
        if type(label) is not str or not label:
            raise ValueError("derived command label is required")
        command = ClosedDerivedCommand(_COMMAND_SEAL)
        self._commands[command] = _CommandRecord(operation, step, ordinal, label)
        return command

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
        return ClosedStepProduct(
            operation,
            step,
            record.label,
            plan.read_qid,
            plan.root.canonical_digest,
            parameters.values,
        )

    def consume_command(
        self,
        command: ClosedDerivedCommand,
        plan: Plan,
        parameters: ParameterValues,
        operation: OperationIdentity,
        ordinal: int,
    ) -> ClosedStepProduct:
        if type(command) is not ClosedDerivedCommand:
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "exact derived command is required")
        record = self._commands.get(command)
        if (
            record is None or record.consumed or record.operation != operation
            or record.ordinal != ordinal
        ):
            raise ContractRefusal(RefusalCode.PLAN_ADMISSION_REQUIRED, "derived command is unavailable")
        if type(plan) is not Plan or type(parameters) is not ParameterValues:
            raise TypeError("derived command requires private plan and pinned parameters")
        product = ClosedStepProduct(
            operation, record.step, record.label, plan.read_qid,
            plan.root.canonical_digest, parameters.values,
        )
        record.consumed = True
        return product
