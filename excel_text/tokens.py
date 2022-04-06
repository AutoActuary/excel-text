import re
from dataclasses import dataclass, field
from typing import Any, List

from excel_dates import ensure_python_date, ensure_python_time

from excel_text.condition import Condition
from excel_text.elapsed import elapsed_hours, elapsed_minutes, elapsed_seconds
from excel_text.numbers import render_left, render_right


@dataclass
class FormatStringToken:
    text: str

    def render(self, value: Any):
        raise NotImplementedError()


@dataclass
class MonthOrMinuteToken(FormatStringToken):
    """
    A placeholder token to use when we don't know yet whether it's minutes or months.
    """

    def render(self, value: Any):
        raise NotImplementedError(
            f"Failed to determine whether '{self.text}' refers to months or minutes."
        )


@dataclass
class DateToken(FormatStringToken):
    def render(self, value: Any):
        raise NotImplementedError()


@dataclass
class YearToken(DateToken):
    def __post_init__(self):
        if re.fullmatch("e+", self.text):
            self.text = "yyyy"

    def render(self, value: Any):
        n = len(self.text)
        d = ensure_python_date(value)
        if n > 2:
            return d.strftime("%Y")
        if n > 0:
            return d.strftime("%y")

        raise ValueError("TODO proper Excel error")


@dataclass
class MonthToken(DateToken):
    def render(self, value: Any):
        n = len(self.text)
        d = ensure_python_date(value)
        if n >= 6 or n == 4:
            return d.strftime("%B")
        if n == 5:
            return d.strftime("%b")[0]
        if n == 3:
            return d.strftime("%b")
        if n == 2:
            return f"{d.month:02d}"
        if n == 1:
            return str(d.month)


@dataclass
class DayToken(DateToken):
    def render(self, value: Any):
        n = len(self.text)
        d = ensure_python_date(value)
        if n > 3:
            return d.strftime("%A")
        if n > 2:
            return d.strftime("%a")
        if n > 1:
            return f"{d.day:02d}"
        if n > 0:
            return str(d.day)


@dataclass
class HourToken(DateToken):
    twelve: bool = False
    """
    12-hour mode
    """

    def render(self, value: Any):
        n = len(self.text)
        d = ensure_python_time(value)
        if self.twelve:
            if n >= 2:
                return d.strftime("%I")
            if n == 1:
                return d.strftime("%I").lstrip("0")
        else:
            if n >= 2:
                return f"{d.hour:02d}"
            if n == 1:
                return str(d.hour)

        raise ValueError("TODO proper Excel error")


@dataclass
class MinuteToken(DateToken):
    def render(self, value: Any):
        n = len(self.text)
        d = ensure_python_time(value)
        if n == 2:
            return f"{d.minute:02d}"
        if n == 1:
            return str(d.minute)


@dataclass
class SecondToken(FormatStringToken):
    decimal_char: str

    def render(self, value: Any):
        d = ensure_python_time(value)
        val = d.second + d.microsecond / 1000000

        parts = self.text.split(self.decimal_char)
        n_int = len(parts[0])
        if len(parts) > 1:
            # Seconds with decimals.
            n_frac = len(parts[1])
            pad = f"0{1 + n_frac + n_int}"
        else:
            # Seconds as integer.
            n_frac = 0
            pad = f"0{n_int}"

        return f"{val:{pad}.{n_frac}f}"


@dataclass
class AmPmToken(FormatStringToken):
    def render(self, value: Any):
        d = ensure_python_time(value)
        val = d.strftime("%p")

        if self.text == "am/pm":
            return val.lower()
        if self.text == "AM/PM":
            return val.upper()
        if self.text == "a/p":
            return val[0].lower()
        if self.text == "A/P":
            return val[0].upper()
        if self.text == "A/p":
            return "A" if val.lower() == "am" else "p"
        if self.text == "a/P":
            return "a" if val.lower() == "am" else "P"

        raise ValueError(f"Failed to render token '{self.text}'.")


@dataclass
class ElapsedHoursToken(FormatStringToken):
    text: str = field(default="[h]", init=False, repr=False, compare=False)

    def render(self, value: Any):
        return str(int(elapsed_hours(value)))


@dataclass
class ElapsedMinutesToken(FormatStringToken):
    text: str = field(default="[m]", init=False, repr=False, compare=False)

    def render(self, value: Any):
        return str(int(elapsed_minutes(value)))


@dataclass
class ElapsedSecondsToken(FormatStringToken):
    text: str = field(default="[s]", init=False, repr=False, compare=False)

    def render(self, value: Any):
        return str(int(elapsed_seconds(value)))


@dataclass
class VerbatimToken(FormatStringToken):
    """
    Renders a part of the format string into the results. Ignores the value.
    """

    def render(self, value: Any):
        return self.text


@dataclass
class NumberToken(FormatStringToken):
    """
    >>> NumberToken(text="0000", decimal_char=".", thousands_char=",").render(12)
    '0012'

    >>> NumberToken(text="$#,##0.00", decimal_char=".", thousands_char=",").render(1234.5678)
    '$1,234.57'
    """

    decimal_char: str
    thousands_char: str

    def render(self, value: Any):
        if not isinstance(value, (float, int)):
            raise ValueError("Value is not numeric.")

        parts = self.text.split(self.decimal_char)
        if "%" in self.text:
            value *= 100

        if len(parts) == 1:
            return render_left(
                parts[0][::-1],
                self.thousands_char,
                str(int(round(value)))[::-1],
            )
        else:
            left = render_left(
                parts[0][::-1],
                self.thousands_char,
                str(int(value))[::-1],
            )
            right = render_right(
                parts[1],
                str(abs(value) % 1)[2:],
            )
            return f"{left}{self.decimal_char}{right}"


@dataclass
class StringToken(FormatStringToken):
    """
    Represents the "@" formatter, which means "format as a string". Its definition is quite vague.
    """

    text: str = field(default="@", init=False, repr=False, compare=False)

    def render(self, value: Any):
        return str(value)


@dataclass
class BinaryConditionalToken(FormatStringToken):
    """
    Represents an conditional structure like `[condition]true_value;false_value`.
    """

    condition: Condition
    true_tokens: List[FormatStringToken]
    false_tokens: List[FormatStringToken]

    def render(self, value: Any):
        tokens = self.true_tokens if self.condition.eval(value) else self.false_tokens
        return "".join(t.render(value) for t in tokens)


@dataclass
class TernaryConditionalToken(FormatStringToken):
    """
    Represents an conditional structure like `value_if_gt_zero;value_if_zero;value_if_lt_zero`
    """

    gt_tokens: List[FormatStringToken]
    lt_tokens: List[FormatStringToken]
    eq_tokens: List[FormatStringToken]

    def render(self, value: Any):
        if value > 0:
            tokens = self.gt_tokens
        elif value < 0:
            tokens = self.lt_tokens
        else:
            tokens = self.eq_tokens

        return "".join(t.render(value) for t in tokens)
