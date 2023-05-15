from dataclasses import dataclass
from typing import Any, Dict, Callable

operations: Dict[str, Callable[[Any, Any], bool]] = {
    ">": lambda lhs, rhs: bool(lhs > rhs),
    "<": lambda lhs, rhs: bool(lhs < rhs),
    ">=": lambda lhs, rhs: bool(lhs >= rhs),
    "<=": lambda lhs, rhs: bool(lhs <= rhs),
    "=": lambda lhs, rhs: bool(lhs == rhs),
}


@dataclass
class Condition:
    """
    An IF condition. This is used by BinaryConditionToken.
    """

    operator: str
    rhs: str

    def eval(self, value: Any) -> bool:
        return operations[self.operator](float(value), float(self.rhs))
