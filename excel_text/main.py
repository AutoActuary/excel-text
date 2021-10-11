import datetime
from typing import Any
import excel_dates
import collections
import itertools as it
import numpy as np

number_options = set("0#?.,%")
placeholders = set("#0?")
NUMBER_TOKEN_MATCH = {"#": None, "0": "0", "?": "0"}
DIGITS = set("0123456789")


def elapsed(d, units):
    date_zero = datetime.datetime(1899, 12, 30, 0, 0, 0)

    if hasattr(d, "hour"):
        delta_time = (d - date_zero).days * 24 + d.hour
        if units == "m":
            delta_time = delta_time * 60 + d.minute
        elif units == "s":
            delta_time = (delta_time * 60 + d.minute) * 60 + d.second
    else:
        delta_time = (d - date_zero).days * 24
        if units == "m":
            delta_time *= 60
        elif units == "s":
            delta_time *= 60 * 60
    return int(delta_time)


FORMAT_DATETIME_CONVERSIONS = {
    "yyyy": lambda d: d.strftime("%Y"),
    "yy": lambda d: d.strftime("%y"),
    "mmmmm": lambda d: d.strftime("%b")[0],
    "mmmm": lambda d: d.strftime("%B"),
    "mmm": lambda d: d.strftime("%b"),
    "mm": lambda d: "{:02d}".format(d.month),
    "m": lambda d: str(d.month),
    "dddd": lambda d: d.strftime("%A"),
    "ddd": lambda d: d.strftime("%a"),
    "dd": lambda d: "{:02d}".format(d.day),
    "d": lambda d: str(d.day),
    "hh": lambda d: "{:02d}".format(d.hour),
    "h": lambda d: str(d.hour),
    "HH": lambda d: d.strftime("%I"),  # 12 Hour (AM/PM)
    "H": lambda d: str(int(d.strftime("%I"))),  # 12 Hour (AM/PM)
    "MM": lambda d: "{:02d}".format(d.minute),
    "M": lambda d: str(d.minute),
    "ss": lambda d: "{:02d}".format(d.second),
    "s": lambda d: str(d.second),
    ".": lambda d: ".",
    ".0": lambda d: ".{:01d}".format(round(d.microsecond / 100000)),
    ".00": lambda d: ".{:02d}".format(round(d.microsecond / 10000)),
    ".000": lambda d: ".{:03d}".format(round(d.microsecond / 1000)),
    "[h]": lambda d: str(elapsed(d, "h")),
    "[m]": lambda d: str(elapsed(d, "m")),
    "[s]": lambda d: str(elapsed(d, "s")),
    "am/pm": lambda d: d.strftime("%p"),
    "a/p": lambda d: d.strftime("%p")[0].lower(),
    "A/P": lambda d: d.strftime("%p")[0].upper(),
    "A/p": lambda d: "A" if d.strftime("%p").lower() == "am" else "p",
    "a/P": lambda d: "a" if d.strftime("%p").lower() == "am" else "P",
}


def FORMAT_DATETIME_CONVERSION_LOOKUP(FORMAT_DATETIME_CONVERSIONS):
    return {
        "e": lambda code: FORMAT_DATETIME_CONVERSIONS["yyyy"],
        "y": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {1: "yy", 2: "yy"}.get(len(code), "yyyy")
        ],
        "m": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {1: "m", 2: "mm", 3: "mmm", 4: "mmmm", 5: "mmmmm",}.get(len(code), "mmmm")
        ],
        "d": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {1: "d", 2: "dd", 3: "ddd",}.get(len(code), "dddd")
        ],
        "h": lambda code: FORMAT_DATETIME_CONVERSIONS[{1: "h",}.get(len(code), "hh")],
        "H": lambda code: FORMAT_DATETIME_CONVERSIONS[{1: "H",}.get(len(code), "HH")],
        "M": lambda code: FORMAT_DATETIME_CONVERSIONS[{1: "M",}.get(len(code), "MM")],
        "s": lambda code: FORMAT_DATETIME_CONVERSIONS[{1: "s",}.get(len(code), "ss")],
        ".": lambda code: FORMAT_DATETIME_CONVERSIONS[code],
        "a": lambda code: FORMAT_DATETIME_CONVERSIONS[code],
        "A": lambda code: FORMAT_DATETIME_CONVERSIONS[code],
        "[": lambda code: FORMAT_DATETIME_CONVERSIONS[code],
    }


FORMAT_DATETIME_CONVERSION_LOOKUP = FORMAT_DATETIME_CONVERSION_LOOKUP(
    FORMAT_DATETIME_CONVERSIONS
)


class Types:
    STRING = 1
    DATETIME = 2
    AM_PM = 3
    NUMBER = 4


Element = collections.namedtuple("Element", "position code next_code char")


def check_duplicates(element, stream):
    elements = [element]
    while elements[-1].next_code == elements[-1].code:
        elements.append(next(stream))
    return "".join(e.code for e in elements)


def check_am_pm(element, stream, fmt):
    if element.code == "a" and element.next_code in "m/":
        if element.next_code == "m":
            to_match = "am/pm"
        else:
            to_match = "a/p"
        matched = fmt[element.position : element.position + len(to_match)]
        if matched.lower() == to_match:
            for i in range(len(to_match) - 1):
                next(stream)
            return matched if to_match == "a/p" else to_match
    return None


def format_value(format_str, fmt_value):
    """Format datetime using a single token from a custom format"""

    return FORMAT_DATETIME_CONVERSION_LOOKUP[format_str[0]](format_str)(fmt_value)


def convert_format(fmt):
    last_date = None
    test_arr = []
    have_decimal = False
    have_thousands = False
    percents = 0

    stream = iter(
        Element(i, *e)
        for i, e in enumerate(zip(fmt.lower(), list(fmt[1:].lower()) + [None], fmt))
    )
    for char in stream:

        if char.code in number_options and not (
            last_date
            and (
                (last_date[0][0][0] == "s" or last_date[0][0] == "[s]")
                and char.code == "."
                or char.code == ","
            )
        ):
            # pass
            need_emit = True
            if char.code == ",":
                need_emit = False
                if (
                    have_decimal
                    or have_thousands
                    or char.position == 0
                    or char.next_code is None
                    or fmt[char.position - 1] not in placeholders
                    or fmt[char.position + 1] not in placeholders
                ):
                    # just a regular comma, not 1000's indicator
                    if char.position == 0 or (
                        fmt[char.position - 1] not in placeholders
                    ):
                        test_arr.append([char.code, Types.STRING])
                else:
                    have_thousands = True

            elif char.code == ".":
                if have_decimal:
                    need_emit = False
                    test_arr.append([char.code, Types.STRING])

                else:
                    have_decimal = True

            elif char.code == "%":
                percents += 1
                need_emit = False
                test_arr.append([char.code, Types.STRING])

            if need_emit:
                code = check_duplicates(char, stream)

                test_arr.append([code, Types.NUMBER])

        elif char.code == "[" and char.next_code in set("hms"):
            char = next(stream)
            code = check_duplicates(char, stream)

            test_arr.append([f"[{code[0]}]", Types.DATETIME])
            next(stream)

            last_date = test_arr[-1], len(test_arr)

        elif char.code in FORMAT_DATETIME_CONVERSION_LOOKUP:
            am_pm = check_am_pm(char, stream, fmt)
            if am_pm:
                test_arr.append([am_pm, Types.AM_PM])
            else:
                code = check_duplicates(char, stream)
                if code in {"m", "mm"} and last_date and last_date[0][0][0] in "hs[":
                    # this is minutes not months
                    code = code.upper()

                elif code[0] == "s" and last_date and last_date[0][0] in {"m", "mm"}:
                    # the previous minutes not months
                    prev = last_date[1] - 1
                    test_arr[prev] = [test_arr[prev][0].upper(), Types.DATETIME]

                elif code == "." and char.next_code == "0":
                    # if we are here with '.', then this is subseconds: ss.000
                    code += check_duplicates(next(stream), stream)
                test_arr.append([code, Types.DATETIME])
                last_date = test_arr[-1], len(test_arr)
        else:
            test_arr.append([char.char, Types.STRING])

    return test_arr, have_decimal, have_thousands, percents


def date_time(Value, tokens):
    value_datetime = excel_dates.ensure_python_datetime(Value)

    chars = np.array(tokens)[:, 0]
    if ("s" in chars or "ss" in chars) and not (
        (".0" in chars or ".00" in chars or ".000" in chars)
    ):
        if value_datetime.microsecond > 500000:
            value_datetime = value_datetime + datetime.timedelta(seconds=1)

    tokens = tuple(
        token[0] if token[1] == Types.STRING else format_value(token[0], value_datetime)
        for token in tokens
    )

    return "".join(tokens)


def number_function(Value, tokens, have_decimal, have_thousands, percents):
    Value *= 100 ** percents
    number_format = "".join(t[0] for t in tokens if t[1] == Types.NUMBER)

    thousands = "," if have_thousands else ""

    if have_decimal:
        left_num_format, right_num_format = number_format.split(".", 1)
        decimals = len(right_num_format)
        left_side, right_side = f"{Value:#{thousands}.{decimals}f}".split(".")
        right_side = right_side.rstrip("0")
    else:
        left_side = f"{int(round(Value, 0)):{thousands}}"
        right_side = None
    left_side = left_side.lstrip("0")

    tokens_iter = iter(t for t in tokens)

    left_side_tokens = []
    right_side_tokens = []
    decimal_check = False
    for x in tokens_iter:
        if x[0] == ".":
            decimal_check = True
        elif decimal_check:
            right_side_tokens.append(x)
        else:
            left_side_tokens.append(x)

    left = tuple(_number_token_converter(left_side_tokens, left_side, left_side=True))

    if have_decimal:
        right_side = "".join(_number_token_converter(right_side_tokens, right_side))
        return f'{"".join(str(v) for v in left[::-1]) }.{right_side}'
    else:
        return "".join(str(v) for v in left[::-1])
    # return "test"


def _number_token_converter(tokens, number, left_side=False):

    digits_iter = iter(number[::-1] if left_side else number)
    result = []
    filler = []
    for token in tokens[::-1] if left_side else tokens:
        if token[1] == Types.STRING:
            filler.extend(iter(token[0]))

        else:
            result.extend(filler)
            filler = []
            for i in range(len(token[0])):
                c = next(digits_iter, NUMBER_TOKEN_MATCH[token[0][0]])
                if c is not None:
                    result.append(c)
                    if c not in DIGITS:
                        c = next(digits_iter, NUMBER_TOKEN_MATCH[token[0][0]])
                        if c is not None:  # pragma: no cover
                            result.append(c)
    result.extend(digits_iter)
    result.extend(filler)
    return result


def text(Value: Any, fmt: str) -> str:
    """
    :param Value:
    :param fmt:
    :return:
    >>> text(1224.1234, "d")
    '8'
    >>> text(1224.1234, "dd")
    '08'
    >>> text(1204.1234, "ddd")
    'Sat'
    >>> text(1233.1234, "dddd")
    'Sunday'
    >>> text(1231.1234, "YYYY")
    '1903'
    >>> text(1234.1234, "yy/m/d")
    '03/5/18'
    >>> text(1234.1234, "yyyy/mmmmm")
    '1903/M'
    >>> text(1294.1234, "yyyy mmmm")
    '1903 July'
    >>> text(1264.1234, "yyyy mmm")  # 3 letters only
    '1903 Jun'
    >>> text(1234.1234, "yyyy/mm")
    '1903/05'
    >>> text(1234.1234, "yyyy/m")
    '1903/5'
    >>> text(1234.1234, "yyyy/mm/dd hh:mm:ss")
    '1903/05/18 02:57:42'
    >>> text(1234.8765, "yyyy/mm/dd hh:mm:ss")  # test rounding
    '1903/05/18 21:02:10'
    >>> text(1234.8765, "yyyy/mm/dd hh:mm:ss AM/PM")  # test rounding
    '1903/05/18 09:02:10 PM'
    >>> text(1234.8765, "yyyy/mm/dd hh:mm:ss.00")
    '1903/05/18 21:02:09.60'
    >>> text(1234.8766998, "yyyy/mm/dd hh:mm:ss.0")  # test rounding
    '1903/05/18 21:02:26.9'
    >>> text(1234.5432, "hh:[mm]:ss")
    '13:1777742:12'

    >>> text(1234.1239, "$#,##0.000")
    '$1,234.124'
    >>> text(1234, "R#,##0.0")
    'R1,234.0'
    >>> text(1234, "r#,##0.0000")
    'r1,234.0000'
    >>> text(234.1239, "$#,##0.000")
    '$234.124'
    >>> text(0.1239, "$#,##0.0")
    '$0.1'

    >>> text(0.2859, "0.0%")
    '28.6%'
    >>> text(0.2859, "00.00%")
    '28.59%'
    >>> text(0.2859, "000.000%")
    '028.590%'

    >> text(1234, "0000000")
    '0001234
    """

    test_arr, have_decimal, have_thousands, percents = convert_format(fmt)
    # print(test_arr)
    types = [token[1] for token in test_arr]
    tokens = [t for t in test_arr]
    if Types.AM_PM in types:  # convert to 12 hour time if AM/PM included
        tokens = [
            t if t[0][0] != "h" else [t[0].upper(), Types.DATETIME] for t in test_arr
        ]
        types.remove(Types.AM_PM)
        types.append(Types.DATETIME)

    if Types.DATETIME in types:
        return date_time(Value, tokens)
    elif Types.NUMBER in types:
        return number_function(Value, tokens, have_decimal, have_thousands, percents)
        pass
