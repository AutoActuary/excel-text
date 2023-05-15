"""
Python Exceptions that represent Excel errors.

@see https://support.microsoft.com/en-us/office/Formulas-and-functions-294d9486-b332-48ed-b489-abe7d0f9eda9#ID0EAABAAA=Errors&ID0EBBD=Errors
"""


class ExcelError(ValueError):
    """
    An Excel error.
    """

    pass


class NaExcelError(ExcelError):
    """
    Excel #N/A error.

    https://support.microsoft.com/en-us/office/how-to-correct-a-n-a-error-a9708411-f82e-4e1b-8a7e-28c28311b993
    """

    pass


class NameExcelError(ExcelError):
    """
    Excel #NAME? error.

    https://support.microsoft.com/en-us/office/how-to-correct-a-name-error-b6d54e31-a743-4d7d-9b61-40002a7b4286
    """

    pass


class DivExcelError(ExcelError):
    """
    Excel #DIV/0! error.

    https://support.microsoft.com/en-us/office/how-to-correct-a-div-0-error-3a5a18a9-8d80-4ebb-a908-39e759a009a5
    """

    pass


class ValueExcelError(ExcelError):
    """
    Excel #VALUE! error.

    https://support.microsoft.com/en-us/office/how-to-correct-a-value-error-15e1b616-fbf2-4147-9c0b-0a11a20e409e
    """

    pass


class RefExcelError(ExcelError):
    """
    Excel #REF! error.

    https://support.microsoft.com/en-us/office/how-to-correct-a-ref-error-822c8e46-e610-4d02-bf29-ec4b8c5ff4be
    """

    pass


class NumExcelError(ExcelError):
    """
    Excel #NUM! error.

    https://support.microsoft.com/en-us/office/how-to-correct-a-num-error-f5193bfc-4400-43f4-88c4-8e1dcca0428b
    """

    pass
