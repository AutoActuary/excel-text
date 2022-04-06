from typing import Union, Any

from excel_text.errors import ExcelError
from excel_text.preprocess import preprocess
from excel_text.grammar import FormatStringParser
from excel_text.visitor import FormatStringVisitor


def get_text_function(config: dict = None):
    """
    Create a text function.

    The text function can be configured to return errors rather than raise them, just like in Excel.
    The error classes are all subclasses of :class:`ExcelError`.

    :param config: Dictionary with config options.
    :return: TEXT function.
    """

    # Provide config defaults.
    if config is None:
        config = {}
    config = {
        "decimal": ".",
        "thousands": ",",
        "raise": True,
        **config,
    }

    parser = FormatStringParser(
        decimal_char=config["decimal"],
        thousands_char=config["thousands"],
    )
    visitor = FormatStringVisitor(
        decimal_char=config["decimal"],
        thousands_char=config["thousands"],
    )

    def t(value: Any, fmt: str) -> Union[str, ExcelError]:
        """
        The same as the =TEXT(...) function in excel. Converts the input value to the desired format.

        :param value: Value that will be formatted.
        :param fmt: The format strung that describes how the output should look.

        :return: The formatted string.
        """
        try:
            tree = parser.parse(fmt)
            tokens = visitor.visit(tree)
            preprocess(tokens)
            return_string = ""
            filler_chars = ""
            for token in tokens:
                entry = token.render(value)
                if hasattr(token, "thousands_char"):
                    if entry[0] == "-":
                        filler_chars += "-"
                        entry = entry[1:]
                return_string += entry
            return filler_chars + return_string

        except ExcelError as e:
            if config["raise"]:
                raise e
            else:
                return e

    return t


if __name__ == "__main__":
    text = get_text_function({"decimal": ".", "thousands": ",", "raise": False})
    # print(text(-3463.456, "R #,##0.00"))
    print(text(123.123, "[>1000$# ##0.0"))
