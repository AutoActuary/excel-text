from dataclasses import dataclass
from typing import Any, List, Generator

from parsimonious import NodeVisitor
from parsimonious.nodes import Node

from excel_text.condition import Condition
from excel_text.tokens import (
    YearToken,
    MonthOrMinuteToken,
    FormatStringToken,
    DayToken,
    HourToken,
    SecondToken,
    VerbatimToken,
    AmPmToken,
    ElapsedHoursToken,
    ElapsedMinutesToken,
    ElapsedSecondsToken,
    NumberToken,
    StringToken,
    BinaryConditionalToken,
    TernaryConditionalToken,
)


def flatten(values: List) -> Generator:
    for v in values:
        if isinstance(v, List):
            yield from flatten(v)
        else:
            yield v


# noinspection PyMethodMayBeStatic
@dataclass
class FormatStringVisitor(NodeVisitor):
    decimal_char: str
    thousands_char: str

    def visit_format_string(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> List[FormatStringToken]:
        return list(flatten(visited_children))

    def visit_y(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> YearToken:
        return YearToken(node.text)

    def visit_m(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> MonthOrMinuteToken:
        return MonthOrMinuteToken(node.text)

    def visit_d(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> DayToken:
        return DayToken(node.text)

    def visit_h(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> HourToken:
        return HourToken(node.text)

    def visit_s(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> SecondToken:
        return SecondToken(node.text, self.decimal_char)

    def visit_ampm(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> AmPmToken:
        return AmPmToken(node.text)

    def visit_datetime(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> Any:
        return visited_children[0]

    def visit_expression(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> Any:
        return visited_children[0]

    def visit_expressions(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> List[Any]:
        return list(flatten(visited_children))

    def visit_other(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> VerbatimToken:
        return VerbatimToken(node.text)

    def visit_double_quoted(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> VerbatimToken:
        return VerbatimToken(node.text[1:-1].replace(r"\"", '"'))

    def visit_single_quoted(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> VerbatimToken:
        return VerbatimToken(node.text[1:-1].replace(r"\'", "'"))

    def visit_colon(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> VerbatimToken:
        return VerbatimToken(":")

    def visit_h_elapsed(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> ElapsedHoursToken:
        return ElapsedHoursToken()

    def visit_m_elapsed(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> ElapsedMinutesToken:
        return ElapsedMinutesToken()

    def visit_s_elapsed(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> ElapsedSecondsToken:
        return ElapsedSecondsToken()

    def visit_number(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> NumberToken:
        return NumberToken(
            text=node.text,
            decimal_char=self.decimal_char,
            thousands_char=self.thousands_char,
        )

    def visit_if_condition(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> Condition:
        return Condition(
            operator=node.match[1],
            rhs=node.match[2],
        )

    def visit_if_separator(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> Node:
        return node

    def visit_if_binary(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> BinaryConditionalToken:
        if len(node.children) == 4:
            condition = visited_children[0]
            if isinstance(condition, Node) and condition.text == "":
                # The default condition is to check if the value is greater than zero (i.e. "truthy").
                condition = Condition(
                    operator=">",
                    rhs="0",
                )
            else:
                condition = condition[0]

            return BinaryConditionalToken(
                text=node.text,
                condition=condition,
                true_tokens=visited_children[1],
                false_tokens=visited_children[3],
            )
        else:
            raise ValueError(
                f"Don't know how to handle 'if' statement in the form of '{node.text}'."
            )

    def visit_if_ternary(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> TernaryConditionalToken:
        if len(node.children) == 5:
            return TernaryConditionalToken(
                text=node.text,
                gt_tokens=visited_children[0],
                eq_tokens=visited_children[2],
                lt_tokens=visited_children[4],
            )
        else:
            raise ValueError(
                f"Don't know how to handle 'if' statement in the form of '{node.text}'."
            )

    def visit_at(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> StringToken:
        return StringToken()

    def generic_visit(
        self,
        node: Node,
        visited_children: List[Any],
    ) -> Any:
        return visited_children or node
