from dataclasses import dataclass
from typing import Any


operations = {
    ">": lambda lhs, rhs: lhs > rhs,
    "<": lambda lhs, rhs: lhs < rhs,
    ">=": lambda lhs, rhs: lhs >= rhs,
    "<=": lambda lhs, rhs: lhs <= rhs,
    "=": lambda lhs, rhs: lhs == rhs,
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
