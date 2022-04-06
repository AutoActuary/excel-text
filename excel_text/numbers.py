def insert_thousands_separator(value: str, thousands: str) -> str:
    """
    Insert thousands separator at appropriate locations.

    :param value: String representation of a number, without thousands separators.
    :param thousands: The thousands separator.

    :return: String representation of the number, with thousands separators.

    >>> insert_thousands_separator("7654321", ",")
    '765,432,1'

    >>> insert_thousands_separator("654321", ";")
    '654;321'

    >>> insert_thousands_separator("54321", "_")
    '543_21'

    >>> insert_thousands_separator("0987654321", " ")
    '098 765 432 1'

    >>> insert_thousands_separator("432", ",")
    '432'

    >>> insert_thousands_separator("0", ",")
    '0'
    """
    value_left_side_rev = value
    for counter in range(1, (len(value) - 1) // 3 + 1):
        pos = counter * 3 + counter - 1
        value_left_side_rev = (
            f"{value_left_side_rev[:pos]}{thousands}{value_left_side_rev[pos:]}"
        )
    return value_left_side_rev


def render_left(
    fmt_left: str,
    thousands_char: str,
    values: str,
):
    values = iter(values)
    return_string = ""
    filler = ""

    has_thousands_seperator = thousands_char in fmt_left

    for character in fmt_left:
        if character in "0#?":
            if character == "0":
                value = next(values, "0")
            else:
                value = next(values, None)
            if value is None:
                break
            elif value.isnumeric():
                return_string += value
            else:
                filler += value
                return_string += "0"
        else:
            if character != thousands_char:
                return_string += character

    for character in list(values):
        return_string += character

    if has_thousands_seperator:
        return_string = insert_thousands_separator(return_string, thousands_char)

    return_string += filler
    return return_string[::-1]


def render_right(
    fmt_right: str,
    values: str,
):
    _counter = 0
    n_sig_figs = calculate_num_significant_figures(fmt_right)

    values = iter(values)
    return_string = ""
    sig_figs_counter = 0
    for character in fmt_right:
        _counter += 1
        if character in "0#?":
            sig_figs_counter += 1
            value = next(values, "0")
            if _counter != n_sig_figs:
                return_string += value
            else:
                return_str = str(int(value) + int((int(next(values, "0")) + 5) / 10))
                if len(return_str) == 1:
                    return_string += return_str
                else:
                    return_string = (
                        return_string[:-1] + str(int(return_string[-1]) + 1) + "0"
                    )
        else:
            return_string += character
    return return_string


def calculate_num_significant_figures(fmt_right):
    total = 0
    for character in "0#?":
        total += fmt_right.count(character)
    return total
