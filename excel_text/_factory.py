from typing import Union, Any, Optional, Dict, Callable

from excel_text._errors import ExcelError
from excel_text._preprocess import preprocess
from excel_text._grammar import FormatStringParser
from excel_text._visitor import FormatStringVisitor


def get_text_function(
    config: Optional[Dict[str, Any]] = None
) -> Callable[[Any, str], Union[str, ExcelError]]:
    """
    Create a text function.

    The text function can be configured to return errors rather than raise them, just like in Excel.
    The error classes are all subclasses of :class:`ExcelError`.

    TODO: Use a TypedDict for the `config` param.

    :param config: Dictionary with config options.
    :return: TEXT function.
    """

    # Provide config defaults.
    if config is None:
        config = {}

    full_config: Dict[str, Any] = {
        "decimal": ".",
        "thousands": ",",
        "raise": True,
        **config,
    }

    parser = FormatStringParser(
        decimal_char=full_config["decimal"],
        thousands_char=full_config["thousands"],
    )
    visitor = FormatStringVisitor(
        decimal_char=full_config["decimal"],
        thousands_char=full_config["thousands"],
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
            # TODO: Try not to do stuff in-place, because it prevents proper type checking.
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
            if full_config["raise"]:
                raise e
            else:
                return e

    return t


if __name__ == "__main__":
    text = get_text_function({"decimal": ".", "thousands": ",", "raise": False})
