import re
from dataclasses import dataclass
from functools import cached_property
from textwrap import dedent

from parsimonious.grammar import Grammar


@dataclass
class FormatStringParser:
    decimal_char: str
    thousands_char: str

    @cached_property
    def grammar(self):
        re_decimal_char = re.escape(self.decimal_char)
        re_thousands_char = re.escape(self.thousands_char)

        rules = dedent(
            rf"""
            format_string = if_binary / if_ternary / expressions
            
            expression = double_quoted / single_quoted / ampm / elapsed / datetime / colon / at / number / other
            expressions = expression+
            
            double_quoted = ~r'"[^\"]+"'
            single_quoted = ~r"'[^\']+'"
            
            ampm = ~r"am?/pm?"i
            
            elapsed = h_elapsed / m_elapsed / s_elapsed
            h_elapsed = ~r"\[h+]"i
            m_elapsed = ~r"\[m+]"i
            s_elapsed = ~r"\[s+]"i
            
            if_binary = if_condition? expressions if_separator expressions
            if_ternary = expressions if_separator expressions if_separator expressions
            if_separator = ";"
            if_condition = ~r"\[(<=|>=|=|>|<)([\d{re_decimal_char}]+)]"
            
            datetime = y / m / d / h / s
            y = ~r"y+|e+"i
            m = ~r"m+"i
            d = ~r"d+"i
            h = ~r"h+"i
            s = ~r"s+(\.0+)?"i
            
            colon = ~r":+"
            at = ~r"@+"
            
            number = ~r"[#0?%{re_decimal_char}{re_thousands_char}][^bdeghmnsy;@\[\]]*"
            other = ~r"[^;]+?"
            """
        )

        return Grammar(rules=rules)

    def parse(self, fmt: str):
        return self.grammar.parse(fmt)
