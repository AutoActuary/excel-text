def insert_thousands_separator(value: str, thousands: str) -> str:
    """
    Insert thousands separator at appropriate locations.

    :param value: String representation of a number, without thousands separators.
    :param thousands: The thousands separator.

    :return: String representation of the number, with thousands separators.

    >>> insert_thousands_separator("1234567", ",")
    '1,234,567'

    >>> insert_thousands_separator("123456", ";")
    '123;456'

    >>> insert_thousands_separator("12345", "_")
    '12_345'

    >>> insert_thousands_separator("1234567890", " ")
    '1 234 567 890'

    >>> insert_thousands_separator("234", ",")
    '234'

    >>> insert_thousands_separator("0", ",")
    '0'
    """
    value_left_side_rev = value[::-1]
    for counter in range(1, (len(value) - 1) // 3 + 1):
        pos = counter * 3 + counter - 1
        value_left_side_rev = (
            f"{value_left_side_rev[:pos]}{thousands}{value_left_side_rev[pos:]}"
        )
    return value_left_side_rev[::-1]


def render_left(
    fmt_left: str,
    thousands_char: str,
    value: int,
) -> str:
    raise NotImplementedError("TODO: implement number formatting")


def render_right(
    fmt_right: str,
    value: float,
):
    raise NotImplementedError("TODO: implement number formatting")
