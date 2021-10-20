import datetime
from typing import Any
import excel_dates
import pandas as pd
from excel_text.errors import *

"""
https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/text.py#L39
"""
placeholders = set("#0?")
NUMBER_TOKEN_MATCH = {"#": None, "0": "0", "?": "0"}
# DIGITS = set("0123456789")

"""
https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/text.py#L44
"""


class Types:
    STRING = 1
    DATETIME = 2
    AM_PM = 3
    NUMBER = 4


"""
https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/date_time.py#L209
"""
df_datetime_formats = pd.DataFrame(
    [
        ["yyyy", lambda d: d.strftime("%Y")],
        ["yy", lambda d: d.strftime("%y")],
        ["mmmmm", lambda d: d.strftime("%b")[0]],
        ["mmmm", lambda d: d.strftime("%B")],
        ["mmm", lambda d: d.strftime("%b")],
        ["mm", lambda d: "{:02d}".format(d.month)],
        ["m", lambda d: str(d.month)],
        ["dddd", lambda d: d.strftime("%A")],
        ["ddd", lambda d: d.strftime("%a")],
        ["dd", lambda d: "{:02d}".format(d.day)],
        ["d", lambda d: str(d.day)],
        ["hh", lambda d: "{:02d}".format(d.hour)],
        ["h", lambda d: str(d.hour)],
        ["HH", lambda d: d.strftime("%I")],  # 12 Hour (AM/PM)
        ["H", lambda d: str(int(d.strftime("%I")))],  # 12 Hour (AM/PM)
        ["MM", lambda d: "{:02d}".format(d.minute)],
        ["M", lambda d: str(d.minute)],
        ["ss", lambda d: "{:02d}".format(d.second)],
        ["s", lambda d: str(d.second)],
        [".", lambda d: "."],
        [".0", lambda d: ".{:01d}".format(round(d.microsecond / 100000))],
        [".00", lambda d: ".{:02d}".format(round(d.microsecond / 10000))],
        [".000", lambda d: ".{:03d}".format(round(d.microsecond / 1000))],
        ["[h]", lambda d: str(elapsed(d, "h"))],
        ["[m]", lambda d: str(elapsed(d, "m"))],
        ["[s]", lambda d: str(elapsed(d, "s"))],
        ["am/pm", lambda d: d.strftime("%p")],
        ["a/p", lambda d: d.strftime("%p")[0].lower()],
        ["A/P", lambda d: d.strftime("%p")[0].upper()],
        ["A/p", lambda d: "A" if d.strftime("%p").lower() == "am" else "p"],
        ["a/P", lambda d: "a" if d.strftime("%p").lower() == "am" else "P"],
    ],
    columns=["format", "conversion"],
)

df_datetime_formats["char"] = list(
    fmt[0] for fmt in df_datetime_formats["format"].values.tolist()
)


def elapsed(d, units):
    """
    solution is unique enough.
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/date_time.py#L176

    converts time to time-elapsed.
    :param d: Value as DateTime
    :param units: h|m|s = hours|minutes|seconds
    :return: Returns the total hours|minutes|seconds

    >>> elapsed(datetime.datetime(1903,5,18,0,0,0), "h")
    29616
    """
    date_zero = datetime.datetime(1899, 12, 30, 0, 0, 0)
    delta_time = (d - date_zero).total_seconds()
    if units not in "hms":
        raise ValueExcelError("invalid time duration option")

    if units == "h":
        delta_time /= 60 ** 2
    if units == "m":
        delta_time /= 60

    return int(delta_time)


def check_duplicates(element, characters):
    """
    solution is unique enough.
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/text.py#L77

    Select all consecutive chars matching element from the characters dataframe and returns as string.
    :param element: 1 entry from the characters dataframe.
    :param characters: The dataframe containing the: code, next_code, char
    :return: Returns a string of characters that matches element.code

    element:
    Pandas(Index=0, code='y', next_code='y', character='y')

    characters:
    Pandas(Index=1, code='y', next_code='y', character='y')
    Pandas(Index=2, code='y', next_code='y', character='y')
    Pandas(Index=3, code='y', next_code=None, character='y')

    output:
    "yyyy"
    """
    elements = pd.DataFrame(columns=["position", "code", "next_code", "char"])
    elements.loc[0] = list(element)

    while elements.iloc[-1].next_code == elements.iloc[-1].code:
        elements.loc[len(elements)] = next(characters)

    return "".join(elements.code.values)


def check_am_pm(element, characters, fmt):
    """
    solution was copied
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/text.py#L63

    Check if the fmt input contains the am/pm option. i.e 'am/pm', 'a/p', 'A/P', 'A/p', 'a/P'
    :param element: 1 entry from the characters dataframe.
    :param characters: The dataframe containing the: code, next_code, char
    :param fmt: a string of the fmt input to the text function
    :return: returns 'am/pm', 'a/p', 'A/P', 'A/p', 'a/P' if there is a match, else None
    """
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


def format_value(format_str, fmt_value):
    """
    solution is unique enough.
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/date_time.py#L282

    Formats the excel token to its required value by using the fmt_value and the df_datetime_formats dataframe
    :param format_str: format token that must match df_datetime_formats["format"]
    :param fmt_value: The datetime value that will be converted to its required format.
    :return: Returns the formatted datetime

    >>> format_value("yyyy", datetime.datetime(1903, 5, 18))
    '1903'
    """
    try:
        return df_datetime_formats[
            df_datetime_formats.format == format_str
        ].conversion.values[0](fmt_value)
    except Exception:
        raise ValueExcelError("incorrect DateTime format")


def convert_format(fmt, decimal_char, thousands_char):
    """
    solution was copied
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/text.py#L87

    Convert the input to tokens.
    :param thousands_char: thousands seperator
    :param decimal_char: decimal seperator
    :param fmt: the format input to the text function
    :return: a tokens dataframe cotaining the token string and token type.

    >>> convert_format("yyyy", ".", ",")
    (  token token_type
    0  yyyy          2, False, False, 0)
    """

    numbers = "0#?%" + decimal_char + thousands_char
    number_options = set(numbers)

    last_date_token = None
    have_decimal = False
    have_thousands = False
    percents = 0
    characters = pd.DataFrame(columns=["code", "next_code", "character"])
    tokens = pd.DataFrame(columns=["token", "token_type"])

    # insert fmt into the characters DataFrame
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
                if char.next_code is None:
                    raise NaExcelError("missing following quotation marks")
                char = next(characters)
                word += char.code
            word = word.strip('"')
            tokens.loc[len(tokens)] = [word, Types.STRING]
            next(characters)

        elif char.code in number_options and not (
            last_date_token
            and (
                (last_date_token[0] == "s" or last_date_token == "[s]")
                and char.code == decimal_char
                or char.code == thousands_char
            )
        ):
            need_emit = True
            if char.code == thousands_char:
                need_emit = False
                if (
                    have_decimal
                    or have_thousands
                    or char.Index == 0
                    or char.next_code is None
                    or fmt[char.Index - 1] not in placeholders
                    or fmt[char.Index + 1] not in placeholders
                ):
                    # just a regular thousands char, not 1000's indicator
                    if char.Index == 0 or (fmt[char.Index - 1] not in placeholders):
                        tokens.loc[len(tokens)] = [char.code, Types.STRING]

                else:
                    have_thousands = True

            elif char.code == decimal_char:
                if have_decimal:
                    need_emit = False
                    tokens.loc[len(tokens)] = [char.code, Types.STRING]

                else:
                    have_decimal = True

            elif char.code == "%":
                percents += 1
                need_emit = False
                tokens.loc[len(tokens)] = [char.code, Types.STRING]

            if need_emit:
                code = check_duplicates(char, characters)

                tokens.loc[len(tokens)] = [code, Types.NUMBER]

        elif char.code == "[" and char.next_code in set("hms"):
            if char.next_code is None:
                raise ValueExcelError("missing arguments")
            char = next(characters)
            code = check_duplicates(char, characters)
            tokens.loc[len(tokens)] = [f"[{code[0]}]", Types.DATETIME]

            if next(characters).code != "]":
                raise ValueExcelError("missing ']'")
            last_date_token = tokens.iloc[-1].token

        elif char.code in df_datetime_formats.char.values:
            am_pm = check_am_pm(char, characters, fmt)
            if am_pm:
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

                    tokens.loc[len(tokens) - 1] = [
                        tokens.loc[len(tokens) - 1].token.str.upper(),
                        Types.DATETIME,
                    ]

                elif code == decimal_char and char.next_code == "0":
                    # if we are here with '.', then this is subseconds: ss.000
                    code_next = next(characters)
                    code += check_duplicates(code_next, characters)

                tokens.loc[len(tokens)] = [code, Types.DATETIME]

                last_date_token = tokens.iloc[-1].token
        else:
            tokens.loc[len(tokens)] = [char.character, Types.STRING]
            pass

    return tokens, have_decimal, have_thousands, percents


def date_time(Value, tokens):
    """
    solution is unique enough.
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/date_time.py#L282

    Loop through all tokens at convert the tokens with a datetime type to usble datetime values.
    :param Value: The value input of the text function.
    :param tokens: A dataframe with tokens.
    :return: a string with the final converted result.

    Value:
    1234
    tokens:
      token token_type
    0  yyyy          2

    output:
    1903
    """

    value_datetime = excel_dates.ensure_python_datetime(Value)

    # check is seconds are present, but milliseconds not. Round of to seconds if so.
    if not tokens[
        (tokens.token.str.contains("s"))
        & (tokens.token_type == Types.DATETIME)
        & (~tokens.token.str.contains(".0").any())
    ].empty:

        if value_datetime.microsecond > 500000:
            value_datetime = value_datetime + datetime.timedelta(seconds=1)

    for index, row in tokens.iterrows():
        if row.token_type != Types.STRING:
            tokens.loc[index] = format_value(row.token, value_datetime)
    return "".join(tokens.token.values)


def number_function(
    Value, tokens, have_decimal, have_thousands, percents, decimal_char, thousands_char
):
    """
    solution was copied
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/text.py#L300

    Sllit Value and token instructions to integers and decimals
    :param thousands_char: thousands seperator character
    :param decimal_char: decimal seperator character.
    :param Value: int/datetime value that must be converted
    :param tokens: Dataframe of tokens that is used to format the Value input
    :param have_decimal: boolean value indicating if the result must have decimal value
    :param have_thousands: boolean value indicating if the result must have a thousands seperator
    :param percents: converts value to % if percents > 0
    :return: a string with the formatted value

    Value:
    1234.1239
    tokens:
      token token_type
    0     $          1
    1     #          4
    2                1
    3    ##          4
    4     0          4
    5     .          4
    6   000          4
    have_decimal:
    True
    have_thousands:
    False
    percents:
    0
    decimal_char:
    .
    thousands_char:
    ,

    output:
    $1,234.124
    """
    Value *= 100 ** percents
    number_format = "".join(tokens[tokens.token_type == Types.NUMBER].token.values)
    thousands = thousands_char if have_thousands else ""

    if have_decimal:
        left_num_format, right_num_format = number_format.split(decimal_char, 1)
        decimals = len(right_num_format)
        Value_left_side, Value_right_side = f"{Value:#{thousands}.{decimals}f}".split(
            decimal_char
        )
        Value_right_side = Value_right_side.rstrip("0")
    else:
        Value_left_side = f"{int(round(Value, 0)):{thousands}}"
        Value_right_side = None
    Value_left_side = Value_left_side.lstrip("0")

    if have_decimal:
        decimal_loc = tokens[tokens.token == decimal_char].index.values[0]
        left_side_tokens = tokens[tokens.index < decimal_loc]
        left_side_results = token_to_number_converter(
            left_side_tokens, Value_left_side, left_side=True
        )
        right_side_tokens = tokens[tokens.index > decimal_loc]
        right_side_results = token_to_number_converter(
            right_side_tokens, Value_right_side, left_side=False
        )
        right_side_results = "".join(right_side_results)
        return f'{"".join(left_side_results[::-1])}.{right_side_results}'

    else:
        left_side_results = token_to_number_converter(
            tokens, Value_left_side, left_side=True
        )
        return "".join(left_side_results[::-1])


def token_to_number_converter(tokens, number, left_side=False):
    """
    solution was copied
    https://github.com/dgorissen/pycel/blob/165b9548a500d25e6ee200e06a3648e7a5937ee3/src/pycel/lib/text.py#L327

    Loop through all tokens and convert the tokens to usable numerical values.
    :param tokens: dataframe of formats that's used to convert the number input.
    :param number: value that gets converted to the format input
    :param left_side: boolean. if True, "tokens" and "number" are for whole numbers.
    :return: a list with the formatted values.

    tokens:
      token token_type
    0     $          1
    1     #          4
    2    ##          4
    3     0          4

    number:
    1,234

    left_side:
    True

    output:
    ['4', '3', '2', ',', '1', '$']
    """

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
                    if not c.isdigit():
                        c = next(digits_iter, NUMBER_TOKEN_MATCH[token.token[0]])
                        if c is not None:  # pragma: no cover
                            result.append(c)
    result.extend(digits_iter)
    result += filler
    return result


def get_text_function(config=None):
    """
    >>> text = get_text_function({"decimal": ".", "thousands": ",", "raise":False})

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
    >>> text(1234.5432, "[hh]:mm:ss")
    '29629:02:12'
    >>> text(1234.5432, "[mm]:ss")
    '1777742:12'
    >>> text(1234.5432, "[ss]")
    '106664532'

    >>> text(1234.1239, "$# ##0.000")
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

    if config is None:
        config = {"decimal": ".", "thousands": ",", "raise": True}

    def text(Value: Any, fmt: str) -> str:
        """
        The same functions as the =TEXT(...) function in excel. Converts the input value to the desired format.
        :param Value: int/float/datetime value that will be formatted.
        :param fmt: The format that is used to format the value input.
        :return: formatted string.
        """
        if config["raise"]:
            raise_input = config["raise"]
        else:
            raise_input = True

        if config["decimal"]:
            decimal_char = config["decimal"]
        else:
            decimal_char = True

        if config["thousands"]:
            thousands_char = config["thousands"]
        else:
            thousands_char = True

        try:
            # decimal_char = config["decimal"]
            # thousands_char = config["thousands"]

            tokens, has_decimals, has_thousands, percents = convert_format(
                fmt, decimal_char, thousands_char
            )

            if (
                Types.AM_PM in tokens.token_type.values
            ):  # convert to 12 hour time if AM/PM included
                if not tokens[tokens.token.isin(["h", "hh"])].empty:
                    tokens.at[tokens.token.isin(["h", "hh"]), "token"] = (
                        tokens[tokens.token.isin(["h", "hh"])].token.values[0].upper()
                    )
                    tokens.at[
                        tokens.token_type == Types.AM_PM, "token_type"
                    ] = Types.DATETIME

            if Types.DATETIME in tokens.token_type.values:
                return date_time(Value, tokens)
            elif Types.NUMBER in tokens.token_type.values:
                return number_function(
                    Value,
                    tokens,
                    has_decimals,
                    has_thousands,
                    percents,
                    decimal_char,
                    thousands_char,
                )
        except ExcelError as e:
            if raise_input:
                raise e
            else:
                return str(e)

    return text


text = get_text_function({"decimal": ".", "thousands": ",", "raise": False})
