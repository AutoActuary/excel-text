from typing import List

from excel_text.tokens import (
    FormatStringToken,
    MonthOrMinuteToken,
    YearToken,
    MonthToken,
    MinuteToken,
    DateToken,
    AmPmToken,
    HourToken,
    BinaryConditionalToken,
    TernaryConditionalToken,
)


def preprocess(tokens: List[FormatStringToken]) -> None:
    """
    Preparse the token list. The list is modified in place.

    Some tokens are influenced by the presence of other tokens in the list. This is handled here.

    :param tokens: The list of tokens to process.
    """
    preprocess_conditionals(tokens)
    preprocess_month_minute(tokens)
    preprocess_am_pm(tokens)


def preprocess_conditionals(tokens: List[FormatStringToken]) -> None:
    """
    Condition tokens contain their own lists of tokens, which must also be pre-processed.
    """
    for t in tokens:
        if isinstance(t, BinaryConditionalToken):
            preprocess(t.true_tokens)
            preprocess(t.false_tokens)
        if isinstance(t, TernaryConditionalToken):
            preprocess(t.lt_tokens)
            preprocess(t.eq_tokens)
            preprocess(t.gt_tokens)


def preprocess_month_minute(tokens: List[FormatStringToken]) -> None:
    """
    Detect when "m" means "month" and when it means "minute".
    """
    last_date_token = None
    for i, token in enumerate(tokens):
        if isinstance(token, MonthOrMinuteToken):
            if isinstance(last_date_token, YearToken):
                # It follows "year", so it must mean "month".
                tokens[i] = MonthToken(token.text)
            else:
                tokens[i] = MinuteToken(token.text)

        if isinstance(token, DateToken):
            last_date_token = token


def preprocess_am_pm(tokens: List[FormatStringToken]) -> None:
    """
    If AM/PM is present, switch all hour tokens to 12-hour mode.
    """
    if not any(isinstance(t, AmPmToken) for t in tokens):
        # Do nothing. The default is 24-hour mode.
        return

    for t in tokens:
        if isinstance(t, HourToken):
            t.twelve = True
