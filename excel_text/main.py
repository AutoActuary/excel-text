import datetime
from typing import Any
import excel_dates
import collections
import itertools as it
import numpy as np
import pandas as pd

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


# Element = collections.namedtuple("Element", "position code next_code char")


def check_duplicates(element, characters):
    elements = pd.DataFrame(columns=["position", "code", "next_code", "char"])
    elements.loc[0] = list(element)

    while elements.iloc[-1].next_code == elements.iloc[-1].code:
        elements.loc[len(elements)] = next(characters)

    return "".join(e for e in elements.code.values)


def check_am_pm(element, characters, fmt):
    if element.code == "a" and element.next_code in "m/":
        if element.next_code == "m":
            to_match = "am/pm"
        else:
            to_match = "a/p"
        matched = fmt[element.Index : element.Index + len(to_match)]
        if matched.lower() == to_match:
            for i in range(len(to_match) - 1):
                next(characters)
            return matched if to_match == "a/p" else to_match
    # return None


def format_value(format_str, fmt_value):
    """Format datetime using a single token from a custom format"""

    return FORMAT_DATETIME_CONVERSION_LOOKUP[format_str[0]](format_str)(fmt_value)


def convert_format(fmt):
    last_date_token = None
    # test_arr = []

    have_decimal = False
    have_thousands = False
    percents = 0
    characters = pd.DataFrame(columns=["code", "next_code", "character"])
    tokens = pd.DataFrame(columns=["token", "token_type"])
    # stream = iter(
    #     Element(i, *e)
    #     for i, e in enumerate(zip(fmt.lower(), list(fmt[1:].lower()) + [None], fmt))
    # )
    fmt_next = list(fmt[1:].lower()) + [None]
    for counter in range(len(fmt)):
        characters.loc[len(characters)] = [
            fmt[counter].lower(),
            fmt_next[counter],
            fmt[counter],
        ]

    characters = characters.itertuples()
    for char in characters:

        if char.code == '"':
            word = char.code

            while char.next_code != '"':
                char = next(characters)

                word += char.code
                # test_arr.append([char.code, Types.STRING])
            word = word.strip('"')
            # test_arr.append([word, Types.STRING])
            tokens.loc[len(tokens)] = [word, Types.STRING]
            next(characters)
            # next(stream)

        elif char.code in number_options and not (
            last_date_token
            # last_date_token = tokens.iloc[-1].token
            and (
                (last_date_token[0] == "s" or last_date_token == "[s]")
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
                    or char.Index == 0
                    or char.next_code is None
                    or fmt[char.Index - 1] not in placeholders
                    or fmt[char.Index + 1] not in placeholders
                ):
                    # just a regular comma, not 1000's indicator
                    if char.Index == 0 or (fmt[char.Index - 1] not in placeholders):
                        # test_arr.append([char.code, Types.STRING])
                        tokens.loc[len(tokens)] = [char.code, Types.STRING]

                else:
                    have_thousands = True

            elif char.code == ".":
                if have_decimal:
                    need_emit = False
                    # test_arr.append([char.code, Types.STRING])
                    tokens.loc[len(tokens)] = [char.code, Types.STRING]

                else:
                    have_decimal = True

            elif char.code == "%":
                percents += 1
                need_emit = False
                # test_arr.append([char.code, Types.STRING])
                tokens.loc[len(tokens)] = [char.code, Types.STRING]

            if need_emit:
                code = check_duplicates(char, characters)

                # test_arr.append([code, Types.NUMBER])
                tokens.loc[len(tokens)] = [code, Types.NUMBER]

                # tokens.loc[len(tokens)] = [code, Types.NUMBER]

        elif char.code == "[" and char.next_code in set("hms"):
            char = next(characters)

            code = check_duplicates(char, characters)

            tokens.loc[len(tokens)] = [f"[{code[0]}]", Types.DATETIME]

            # test_arr.append([f"[{code[0]}]", Types.DATETIME])
            next(characters)

            # last_date = test_arr[-1], len(test_arr)

            last_date_token = tokens.iloc[-1].token

        elif char.code in FORMAT_DATETIME_CONVERSION_LOOKUP:
            am_pm = check_am_pm(char, characters, fmt)
            if am_pm:
                # test_arr.append([am_pm, Types.AM_PM])
                tokens.loc[len(tokens)] = [am_pm, Types.AM_PM]

            else:
                code = check_duplicates(char, characters)
                if (
                    code in {"m", "mm"}
                    and last_date_token
                    and last_date_token[0] in "hs["
                ):
                    # this is minutes not months
                    code = code.upper()

                elif (
                    code[0] == "s"
                    and last_date_token
                    and last_date_token in {"m", "mm"}
                ):
                    # the previous minutes not months
                    # prev = last_date_token[1] - 1
                    # test_arr[prev] = [test_arr[prev][0].upper(), Types.DATETIME]
                    tokens.loc[len(tokens) - 1] = [
                        tokens.loc[len(tokens) - 1].token.str.upper(),
                        Types.DATETIME,
                    ]

                elif code == "." and char.next_code == "0":
                    # if we are here with '.', then this is subseconds: ss.000
                    # code += check_duplicates(next(stream), stream)
                    code_next = next(characters)
                    code += check_duplicates(code_next, characters)

                # test_arr.append([code, Types.DATETIME])
                tokens.loc[len(tokens)] = [code, Types.DATETIME]

                last_date_token = tokens.iloc[-1].token
        else:
            # test_arr.append([char.char, Types.STRING])
            tokens.loc[len(tokens)] = [char.character, Types.STRING]
            pass

    return tokens, have_decimal, have_thousands, percents


def date_time(Value, tokens):
    value_datetime = excel_dates.ensure_python_datetime(Value)

    chars = tokens.token.values
    if ("s" in chars or "ss" in chars) and not (
        (".0" in chars or ".00" in chars or ".000" in chars)
    ):
        if value_datetime.microsecond > 500000:
            value_datetime = value_datetime + datetime.timedelta(seconds=1)

    for index, row in tokens.iterrows():
        if row.token_type != Types.STRING:
            tokens.loc[index] = format_value(row.token, value_datetime)

    # tokens = tuple(
    #     token[0] if token[1] == Types.STRING else format_value(token[0], value_datetime)
    #     for token in tokens
    # )

    return "".join(tokens.token.values)


def number_function(Value, tokens, have_decimal, have_thousands, percents):
    Value *= 100 ** percents
    # number_format = "".join(t[0] for t in tokens if t[1] == Types.NUMBER)
    number_format = "".join(tokens[tokens.token_type == Types.NUMBER].token.values)
    thousands = "," if have_thousands else ""

    if have_decimal:
        left_num_format, right_num_format = number_format.split(".", 1)
        decimals = len(right_num_format)
        Value_left_side, Value_right_side = f"{Value:#{thousands}.{decimals}f}".split(
            "."
        )
        Value_right_side = Value_right_side.rstrip("0")
    else:
        Value_left_side = f"{int(round(Value, 0)):{thousands}}"
        Value_right_side = None
    Value_left_side = Value_left_side.lstrip("0")

    if have_decimal:
        decimal_loc = tokens[tokens.token == "."].index.values[0]
        left_side_tokens = tokens[tokens.index < decimal_loc]
        left_side_results = token_to_number_converter(
            left_side_tokens, Value_left_side, left_side=True
        )
        right_side_tokens = tokens[tokens.index > decimal_loc]
        right_side_results = token_to_number_converter(
            right_side_tokens, Value_right_side, left_side=False
        )
        right_side_results = "".join(str(v) for v in right_side_results)
        return (
            f'{"".join(str(v) for v in left_side_results[::-1])}.{right_side_results}'
        )

    else:
        left_side_results = token_to_number_converter(
            tokens, Value_left_side, left_side=True
        )
        return "".join(str(v) for v in left_side_results[::-1])


def token_to_number_converter(tokens, number, left_side=False):
    digits_iter = iter(
        number[::-1] if left_side else number
    )  # reverse order if left side
    result = []
    filler = []
    for token in (
        tokens.iloc[::-1].itertuples() if left_side else tokens.itertuples()
    ):  # reverse order if left side
        if token.token_type == Types.STRING:
            filler.append(token.token)
        else:
            result += filler
            filler = []
            for i in range(len(token.token)):
                c = next(digits_iter, NUMBER_TOKEN_MATCH[token.token[0]])
                if c is not None:
                    result.append(c)
                    if c not in DIGITS:
                        c = next(digits_iter, NUMBER_TOKEN_MATCH[token.token[0]])
                        if c is not None:  # pragma: no cover
                            result.append(c)
    result.extend(digits_iter)
    result += filler
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

    >>> text(1234.1239, '"m"#,##0.0')
    'm1,234.1'

    >>> text(0.2859, "0.0%")
    '28.6%'
    >>> text(0.2859, "00.00%")
    '28.59%'
    >>> text(0.2859, "000.000%")
    '028.590%'

    >>> text(1234, "0000000")
    '0001234'
    >>> text(1234, "0000")
    '1234'
    >>> text(1234, "000")
    '1234'

    >>> text(123456, "##0° 00' 00''")
    "12° 34' 56''"

    >>> text(9123456, "##0° 00' 00''")
    "912° 34' 56''"
    """

    tokens, have_decimal, have_thousands, percents = convert_format(fmt)

    if (
        Types.AM_PM in tokens.token_type.values
    ):  # convert to 12 hour time if AM/PM included
        if not tokens[tokens.token.isin(["h", "hh"])].empty:
            tokens.at[tokens.token.isin(["h", "hh"]), "token"] = (
                tokens[tokens.token.isin(["h", "hh"])].token.values[0].upper()
            )
            tokens.at[tokens.token_type == Types.AM_PM, "token_type"] = Types.DATETIME

    if Types.DATETIME in tokens.token_type.values:
        return date_time(Value, tokens)
    elif Types.NUMBER in tokens.token_type.values:
        return number_function(Value, tokens, have_decimal, have_thousands, percents)


print(text(1.2859, "$$$ 0.00%"))
