import datetime
from typing import Any
import pandas as pd
import excel_dates

number_options = set("0#?.,%")


def elapsed(d, units):
    date_zero = excel_dates.ensure_python_datetime(0)
    if hasattr(d, "hour"):
        elapsed = (d - date_zero).days * 24 + d.hour
        if units == "m":
            elapsed = elapsed * 60 + d.minute
        elif units == "s":
            elapsed = (elapsed * 60 + d.minute) * 60 + d.second
    else:
        elapsed = (d - date_zero).days * 24
        if units == "m":
            elapsed *= 60
        elif units == "s":
            elapsed *= 60 * 60
    return int(elapsed)


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
            {
                1: "m",
                2: "mm",
                3: "mmm",
                4: "mmmm",
                5: "mmmmm",
            }.get(len(code), "mmmm")
        ],
        "d": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {
                1: "d",
                2: "dd",
                3: "ddd",
            }.get(len(code), "dddd")
        ],
        "h": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {
                1: "h",
            }.get(len(code), "hh")
        ],
        "H": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {
                1: "H",
            }.get(len(code), "HH")
        ],
        "M": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {
                1: "M",
            }.get(len(code), "MM")
        ],
        "s": lambda code: FORMAT_DATETIME_CONVERSIONS[
            {
                1: "s",
            }.get(len(code), "ss")
        ],
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


import collections

Element = collections.namedtuple("Element", "position code next_code char")


def check_duplicates(element, stream):
    elements = [element]
    while elements[-1].next_code == elements[-1].code:
        elements.append(next(stream))
    print(elements)
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


def format_value(format_str, format_value):
    """Format datetime using a single token from a custom format"""
    # try:
    print("format string to lookup", format_str)
    print(FORMAT_DATETIME_CONVERSION_LOOKUP[format_str[0]](format_str)(format_value))
    return FORMAT_DATETIME_CONVERSION_LOOKUP[format_str[0]](format_str)(format_value)
    # except (KeyError, ValueError, AttributeError):
    #     return VALUE_ERROR


def convert_format(fmt):
    print(fmt)
    last_date = None
    test_arr = []
    stream = iter(
        Element(i, *e)
        for i, e in enumerate(zip(fmt.lower(), list(fmt[1:].lower()) + [None], fmt))
    )
    for char in stream:

        print(char.code)
        if char.code in number_options and not (
            last_date
            and (
                (last_date[0][0][0] == "s" or last_date[0][0] == "[s]")
                and char.code == "."
                or char.code == ","
            )
        ):
            pass

        elif char.code == "[" and char.next_code in set("hms"):
            char = next(stream)
            code = check_duplicates(char, stream)

            test_arr.append([f"[{code[0]}]", Types.DATETIME])
            char = next(stream)
            char = next(stream)

            last_date = test_arr[-1], len(test_arr)

        if char.code in FORMAT_DATETIME_CONVERSION_LOOKUP:
            am_pm = check_am_pm(char, stream, fmt)
            if am_pm:
                test_arr.append([am_pm, Types.AM_PM])
            else:
                code = check_duplicates(char, stream)
                print("code", code, last_date)
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
            test_arr.append([char.code, Types.STRING])

    return test_arr


def text(Value: Any, fmt: str) -> str:
    # print(fmt)
    # last_date = None
    # test_arr = []
    # stream = iter(
    #     Element(i, *e)
    #     for i, e in enumerate(zip(fmt.lower(), list(fmt[1:].lower()) + [None], fmt))
    # )
    # for char in stream:
    #
    #     print(char.code)
    #     if char.code in number_options and not (
    #         last_date
    #         and (
    #             (last_date[0][0][0] == "s" or last_date[0][0] == "[s]")
    #             and char.code == "."
    #             or char.code == ","
    #         )
    #     ):
    #         pass
    #
    #     elif char.code == "[" and char.next_code in set("hms"):
    #         char = next(stream)
    #         code = check_duplicates(char, stream)
    #
    #         test_arr.append([f"[{code[0]}]", Types.DATETIME])
    #         char = next(stream)
    #         char = next(stream)
    #
    #         last_date = test_arr[-1], len(test_arr)
    #
    #     if char.code in FORMAT_DATETIME_CONVERSION_LOOKUP:
    #         am_pm = check_am_pm(char, stream, fmt)
    #         if am_pm:
    #             test_arr.append([am_pm, Types.AM_PM])
    #         else:
    #             code = check_duplicates(char, stream)
    #             print("code", code, last_date)
    #             if code in {"m", "mm"} and last_date and last_date[0][0][0] in "hs[":
    #                 # this is minutes not months
    #                 code = code.upper()
    #
    #             elif code[0] == "s" and last_date and last_date[0][0] in {"m", "mm"}:
    #                 # the previous minutes not months
    #                 prev = last_date[1] - 1
    #                 test_arr[prev] = [test_arr[prev][0].upper(), Types.DATETIME]
    #
    #             elif code == "." and char.next_code == "0":
    #                 # if we are here with '.', then this is subseconds: ss.000
    #                 code += check_duplicates(next(stream), stream)
    #             test_arr.append([code, Types.DATETIME])
    #             last_date = test_arr[-1], len(test_arr)
    #     else:
    #         test_arr.append([char.code, Types.STRING])
    test_arr = convert_format(fmt)
    print(test_arr)

    types = [token[1] for token in test_arr]
    print(types)
    tokens = [t for t in test_arr]
    if Types.AM_PM in types:  # convert to 12 hour time if AM/PM included
        tokens = [
            t if t[0][0] != "h" else [t[0].upper(), Types.DATETIME] for t in test_arr
        ]
        types.remove(Types.AM_PM)
        types.append(Types.DATETIME)
        print("toekn", tokens)

    if True:
        value_datetime = excel_dates.ensure_python_datetime(Value)

        tokens = tuple(
            token[0]
            if token[1] == Types.STRING
            else format_value(token[0], value_datetime)
            for token in tokens
        )

        print(tokens)
        return "".join(tokens)


print(text(1234.5432, "[hh]:[mm]:[ss] A/p"))

xyz = excel_dates.ensure_python_datetime(1234.5432)

print(xyz)

x = datetime.datetime.now()
y = datetime.datetime.fromtimestamp(0)
print(xyz)
