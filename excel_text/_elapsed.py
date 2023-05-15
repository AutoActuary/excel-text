import datetime
from typing import Union

from excel_dates import AnyDateType, ensure_excel_datetime


def elapsed_seconds(value: AnyDateType) -> float:
    """
    Convert the given datetime to the number of seconds elapsed since "date zero" for `date` and `datetime` objects,
    or the start of the day for `time` objects.

    The 1900 bug is reproduced. See:

    - https://docs.microsoft.com/en-us/office/troubleshoot/excel/wrongly-assumes-1900-is-leap-year
    - https://www.quora.com/Why-wont-Microsoft-fix-the-1900-leap-year-bug-that-exists-in-Excel

    :param value: The datetime.
    :return: The number of seconds.
    """

    if type(value) == datetime.time:
        # Very simply the time since the start of the day.
        return (
            (value.hour * 3600)
            + (value.minute * 60)
            + value.second
            + (value.microsecond / 1000000.0)
        )

    return ensure_excel_datetime(value) * 86400


def elapsed_minutes(
    value: Union[datetime.datetime, datetime.date, datetime.time]
) -> float:
    """
    Convert the given datetime to the number of minutes elapsed since "date zero".

    The 1900 bug is reproduced. See:

    - https://docs.microsoft.com/en-us/office/troubleshoot/excel/wrongly-assumes-1900-is-leap-year
    - https://www.quora.com/Why-wont-Microsoft-fix-the-1900-leap-year-bug-that-exists-in-Excel

    :param value: The datetime.
    :return: The number of minutes.
    """
    return elapsed_seconds(value) / 60


def elapsed_hours(
    value: Union[datetime.datetime, datetime.date, datetime.time]
) -> float:
    """
    Convert the given datetime to the number of hours elapsed since "date zero".

    The 1900 bug is reproduced. See:

    - https://docs.microsoft.com/en-us/office/troubleshoot/excel/wrongly-assumes-1900-is-leap-year
    - https://www.quora.com/Why-wont-Microsoft-fix-the-1900-leap-year-bug-that-exists-in-Excel

    :param value: The datetime.
    :return: The number of hours.
    """
    return elapsed_seconds(value) / 3600
