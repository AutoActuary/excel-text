import re
from dataclasses import dataclass
from functools import cached_property

from parsimonious.grammar import Grammar


@dataclass
class FormatStringParser:
    decimal_char: str
    thousands_char: str

    @cached_property
    def grammar(self):
        re_decimal_char = re.escape(self.decimal_char)
        re_thousands_char = re.escape(self.thousands_char)

        rules = rf"""
format_string = if_binary / if_ternary / expressions

expression = double_quoted / single_quoted / ampm / elapsed / datetime / colon / at / number / other
expressions = expression+

double_quoted = ~'"[^\"]+"'
single_quoted = ~"'[^\']+'"

ampm = ~"am?/pm?"i

elapsed = h_elapsed / m_elapsed / s_elapsed
h_elapsed = ~"\[h+]"i
m_elapsed = ~"\[m+]"i
s_elapsed = ~"\[s+]"i

if_binary = if_condition? expressions if_separator expressions
if_ternary = expressions if_separator expressions if_separator expressions
if_separator = ";"
if_condition = ~"\[(<=|>=|=|>|<)([\d{re_decimal_char}]+)]"

datetime = y / m / d / h / s
y = ~"y+|e+"i
m = ~"m+"i
d = ~"d+"i
h = ~"h+"i
s = ~"s+(\.0+)?"i

colon = ~":+"
at = ~"@+"

# number = ~"[#0?%{re_decimal_char}{re_thousands_char}][#0?%{re_decimal_char}{re_thousands_char}acfijklopqrtuvwxz°'\s_]*"
number = ~"[#0?%{re_decimal_char}{re_thousands_char}][^bdeghmnsy;@\[\]]*"
other = ~"[^;]+?"

"""
        return Grammar(rules=rules)

    def parse(self, fmt: str):
        return self.grammar.parse(fmt)
