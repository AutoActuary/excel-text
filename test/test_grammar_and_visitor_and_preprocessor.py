"""
Test the grammar, node visitor, and token preprocessor all together, because it's too tedious to write separate unit
tests for each one, given the huge number of examples here.
"""

import unittest
from typing import List

# noinspection PyProtectedMember
from excel_text._condition import Condition

# noinspection PyProtectedMember
from excel_text._grammar import FormatStringParser

# noinspection PyProtectedMember
from excel_text._preprocess import preprocess

# noinspection PyProtectedMember
from excel_text._tokens import (
    FormatStringToken,
    NumberToken,
    VerbatimToken,
    StringToken,
    ElapsedHoursToken,
    MinuteToken,
    SecondToken,
    ElapsedMinutesToken,
    ElapsedSecondsToken,
    DayToken,
    HourToken,
    YearToken,
    MonthToken,
    AmPmToken,
    BinaryConditionalToken,
)

# noinspection PyProtectedMember
from excel_text._visitor import FormatStringVisitor


def tokenize(
    fmt: str,
    decimal_char: str,
    thousands_char: str,
) -> List[FormatStringToken]:
    """
    Parse, visit and preprocess.
    """
    parser = FormatStringParser(
        decimal_char=decimal_char,
        thousands_char=thousands_char,
    )
    visitor = FormatStringVisitor(
        decimal_char=decimal_char,
        thousands_char=thousands_char,
    )

    tree = parser.parse(fmt)
    tokens = visitor.visit(tree)

    # TODO: Try not to do stuff in-place, because it prevents proper type checking.
    preprocess(tokens)
    return tokens  # type: ignore


class TestGrammar(unittest.TestCase):
    def test_1(self) -> None:
        self.assertEqual(
            [NumberToken(text="000", decimal_char=".", thousands_char=",")],
            tokenize("000", ".", ","),
        )

    def test_2(self) -> None:
        self.assertEqual(
            [NumberToken(text="0000", decimal_char=".", thousands_char=",")],
            tokenize("0000", ".", ","),
        )

    def test_3(self) -> None:
        self.assertEqual(
            [NumberToken(text="0000000", decimal_char=".", thousands_char=",")],
            tokenize("0000000", ".", ","),
        )

    def test_4(self) -> None:
        self.assertEqual(
            [NumberToken(text="# ##0,00", decimal_char=".", thousands_char=",")],
            tokenize("# ##0,00", ".", ","),
        )

    def test_5(self) -> None:
        self.assertEqual(
            [NumberToken(text="# ##0.00", decimal_char=".", thousands_char=",")],
            tokenize("# ##0.00", ".", ","),
        )

    def test_6(self) -> None:
        self.assertEqual(
            [NumberToken(text="##0° 00' 00''", decimal_char=".", thousands_char=",")],
            tokenize("##0° 00' 00''", ".", ","),
        )

    def test_8(self) -> None:
        self.assertEqual(
            [
                NumberToken(text="#.##0,00", decimal_char=".", thousands_char=","),
            ],
            tokenize("#.##0,00", ".", ","),
        )

    def test_9(self) -> None:
        self.assertEqual(
            [
                NumberToken(text="#_##0.00", decimal_char=".", thousands_char=","),
            ],
            tokenize("#_##0.00", ".", ","),
        )

    def test_10(self) -> None:
        self.assertEqual(
            [
                VerbatimToken(text="$"),
                NumberToken(text="# ##0.000", decimal_char=".", thousands_char=","),
            ],
            tokenize("$# ##0.000", ".", ","),
        )

    def test_11(self) -> None:
        self.assertEqual(
            [
                VerbatimToken(text="$"),
                NumberToken(text="#,##0.0", decimal_char=".", thousands_char=","),
            ],
            tokenize("$#,##0.0", ".", ","),
        )

    def test_12(self) -> None:
        self.assertEqual(
            [
                VerbatimToken(text="$"),
                NumberToken(text="#,##0.000", decimal_char=".", thousands_char=","),
            ],
            tokenize("$#,##0.000", ".", ","),
        )

    def test_13(self) -> None:
        self.assertEqual(
            [NumberToken(text=".", decimal_char=".", thousands_char=",")],
            tokenize(".", ".", ","),
        )

    def test_14(self) -> None:
        self.assertEqual(
            [NumberToken(text="0.0%", decimal_char=".", thousands_char=",")],
            tokenize("0.0%", ".", ","),
        )

    def test_15(self) -> None:
        self.assertEqual(
            [NumberToken(text="00.00%", decimal_char=".", thousands_char=",")],
            tokenize("00.00%", ".", ","),
        )

    def test_16(self) -> None:
        self.assertEqual(
            [NumberToken(text="000.000%", decimal_char=".", thousands_char=",")],
            tokenize("000.000%", ".", ","),
        )

    def test_17(self) -> None:
        self.assertEqual(
            [StringToken()],
            tokenize("@", ".", ","),
        )

    def test_18(self) -> None:
        self.assertEqual(
            [
                BinaryConditionalToken(
                    text="[<543]0000;#0.0",
                    condition=Condition(
                        operator="<",
                        rhs="543",
                    ),
                    true_tokens=[
                        NumberToken(text="0000", decimal_char=".", thousands_char=",")
                    ],
                    false_tokens=[
                        NumberToken(text="#0.0", decimal_char=".", thousands_char=",")
                    ],
                )
            ],
            tokenize("[<543]0000;#0.0", ".", ","),
        )

    def test_19(self) -> None:
        self.assertEqual(
            [
                BinaryConditionalToken(
                    text="[=543][h];yyyymm",
                    condition=Condition(
                        operator="=",
                        rhs="543",
                    ),
                    true_tokens=[ElapsedHoursToken()],
                    false_tokens=[
                        YearToken(text="yyyy"),
                        MonthToken(text="mm"),
                    ],
                )
            ],
            tokenize("[=543][h];yyyymm", ".", ","),
        )

    def test_20(self) -> None:
        self.assertEqual(
            [
                BinaryConditionalToken(
                    text="[>543]0000;#0.0",
                    condition=Condition(
                        operator=">",
                        rhs="543",
                    ),
                    true_tokens=[
                        NumberToken(text="0000", decimal_char=".", thousands_char=",")
                    ],
                    false_tokens=[
                        NumberToken(text="#0.0", decimal_char=".", thousands_char=",")
                    ],
                )
            ],
            tokenize("[>543]0000;#0.0", ".", ","),
        )

    # FIXME
    # def test_error(self) -> None:
    #     self.assertEqual(
    #         [],
    #         tokenize("[>1000$# ##0.0", ".", ","),
    #     )

    def test_22(self) -> None:
        self.assertEqual(
            [ElapsedHoursToken()],
            tokenize("[h]", ".", ","),
        )

    def test_23(self) -> None:
        self.assertEqual(
            [
                ElapsedHoursToken(),
                VerbatimToken(text=":"),
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
            ],
            tokenize("[hh]:mm:ss", ".", ","),
        )

    def test_24(self) -> None:
        self.assertEqual(
            [ElapsedMinutesToken()],
            tokenize("[m]", ".", ","),
        )

    def test_25(self) -> None:
        self.assertEqual(
            [
                ElapsedMinutesToken(),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
            ],
            tokenize("[mm]:ss", ".", ","),
        )

    def test_26(self) -> None:
        self.assertEqual(
            [ElapsedSecondsToken()],
            tokenize("[ss]", ".", ","),
        )

    def test_28(self) -> None:
        self.assertEqual(
            [DayToken(text="d")],
            tokenize("d", ".", ","),
        )

    def test_30(self) -> None:
        self.assertEqual(
            [DayToken(text="dd")],
            tokenize("dd", ".", ","),
        )

    def test_31(self) -> None:
        self.assertEqual(
            [DayToken(text="ddd")],
            tokenize("ddd", ".", ","),
        )

    def test_32(self) -> None:
        self.assertEqual(
            [DayToken(text="dddd")],
            tokenize("dddd", ".", ","),
        )

    def test_33(self) -> None:
        self.assertEqual(
            [HourToken(text="h", twelve=False)],
            tokenize("h", ".", ","),
        )

    def test_34(self) -> None:
        self.assertEqual(
            [
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
            ],
            tokenize("hh:::mm:ss", ".", ","),
        )

    def test_35(self) -> None:
        self.assertEqual(
            [
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
            ],
            tokenize("hh:mm:ss", ".", ","),
        )

    def test_36(self) -> None:
        self.assertEqual(
            [
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
            ],
            tokenize("hh:ss", ".", ","),
        )

    def test_37(self) -> None:
        self.assertEqual(
            [
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
            ],
            tokenize("mm:ss", ".", ","),
        )

    def test_38(self) -> None:
        self.assertEqual(
            [
                VerbatimToken(text="R"),
                VerbatimToken(text=" "),
                NumberToken(text="#,##0.00", decimal_char=".", thousands_char=","),
            ],
            tokenize("R #,##0.00", ".", ","),
        )

    def test_39(self) -> None:
        self.assertEqual(
            [
                BinaryConditionalToken(
                    text="R #,##0.00;0000",
                    condition=Condition(
                        operator=">",
                        rhs="0",
                    ),
                    true_tokens=[
                        VerbatimToken(text="R"),
                        VerbatimToken(text=" "),
                        NumberToken(
                            text="#,##0.00", decimal_char=".", thousands_char=","
                        ),
                    ],
                    false_tokens=[
                        NumberToken(text="0000", decimal_char=".", thousands_char=",")
                    ],
                ),
            ],
            tokenize("R #,##0.00;0000", ".", ","),
        )

    def test_40(self) -> None:
        self.assertEqual(
            [
                VerbatimToken(text="R"),
                NumberToken(text="#,##0.0", decimal_char=".", thousands_char=","),
            ],
            tokenize("R#,##0.0", ".", ","),
        )

    def test_41(self) -> None:
        self.assertEqual(
            [
                VerbatimToken(text="r"),
                NumberToken(text="#,##0.0000", decimal_char=".", thousands_char=","),
            ],
            tokenize("r#,##0.0000", ".", ","),
        )

    def test_42(self) -> None:
        self.assertEqual(
            [SecondToken(text="ss.00", decimal_char=".")],
            tokenize("ss.00", ".", ","),
        )

    def test_43(self) -> None:
        self.assertEqual(
            [YearToken(text="y")],
            tokenize("y", ".", ","),
        )

    def test_44(self) -> None:
        self.assertEqual(
            [
                YearToken(text="yy"),
                VerbatimToken(text="/"),
                MonthToken(text="m"),
                VerbatimToken(text="/"),
                DayToken(text="d"),
            ],
            tokenize("yy/m/d", ".", ","),
        )

    def test_45(self) -> None:
        self.assertEqual(
            [YearToken(text="yyyy"), VerbatimToken(text=" "), MonthToken(text="mmm")],
            tokenize("yyyy mmm", ".", ","),
        )

    def test_46(self) -> None:
        self.assertEqual(
            [YearToken(text="yyyy"), VerbatimToken(text=" "), MonthToken(text="mmmm")],
            tokenize("yyyy mmmm", ".", ","),
        )

    def test_47(self) -> None:
        self.assertEqual(
            [YearToken(text="YYYY")],
            tokenize("YYYY", ".", ","),
        )

    def test_48(self) -> None:
        self.assertEqual(
            [YearToken(text="yyyy")],
            tokenize("yyyy", ".", ","),
        )

    def test_49(self) -> None:
        self.assertEqual(
            [YearToken(text="yyyy"), VerbatimToken(text="/"), MonthToken(text="m")],
            tokenize("yyyy/m", ".", ","),
        )

    def test_50(self) -> None:
        self.assertEqual(
            [YearToken(text="yyyy"), VerbatimToken(text="/"), MonthToken(text="mm")],
            tokenize("yyyy/mm", ".", ","),
        )

    def test_51(self) -> None:
        self.assertEqual(
            [
                YearToken(text="yyyy"),
                VerbatimToken(text="/"),
                MonthToken(text="mm"),
                VerbatimToken(text="/"),
                DayToken(text="dd"),
                VerbatimToken(text=" "),
                HourToken(text="hh", twelve=True),
                VerbatimToken(text=":"),
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
                VerbatimToken(text=" "),
                AmPmToken(text="AM/PM"),
            ],
            tokenize("yyyy/mm/dd hh:mm:ss AM/PM", ".", ","),
        )

    def test_52(self) -> None:
        self.assertEqual(
            [
                YearToken(text="yyyy"),
                VerbatimToken(text="/"),
                MonthToken(text="mm"),
                VerbatimToken(text="/"),
                DayToken(text="dd"),
                VerbatimToken(text=" "),
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss", decimal_char="."),
            ],
            tokenize("yyyy/mm/dd hh:mm:ss", ".", ","),
        )

    def test_54(self) -> None:
        self.assertEqual(
            [
                YearToken(text="yyyy"),
                VerbatimToken(text="/"),
                MonthToken(text="mm"),
                VerbatimToken(text="/"),
                DayToken(text="dd"),
                VerbatimToken(text=" "),
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss.0", decimal_char="."),
            ],
            tokenize("yyyy/mm/dd hh:mm:ss.0", ".", ","),
        )

    def test_55(self) -> None:
        self.assertEqual(
            [
                YearToken(text="yyyy"),
                VerbatimToken(text="/"),
                MonthToken(text="mm"),
                VerbatimToken(text="/"),
                DayToken(text="dd"),
                VerbatimToken(text=" "),
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                MinuteToken(text="mm"),
                VerbatimToken(text=":"),
                SecondToken(text="ss.00", decimal_char="."),
            ],
            tokenize("yyyy/mm/dd hh:mm:ss.00", ".", ","),
        )

    def test_56(self) -> None:
        self.assertEqual(
            [YearToken(text="yyyy"), VerbatimToken(text="/"), MonthToken(text="mmmmm")],
            tokenize("yyyy/mmmmm", ".", ","),
        )

    def test_57(self) -> None:
        self.assertEqual(
            [
                VerbatimToken(text="m"),
                NumberToken(text="#,##0.0", decimal_char=".", thousands_char=","),
            ],
            tokenize('"m"#,##0.0', ".", ","),
        )

    def test_am_pm(self) -> None:
        self.assertEqual(
            [
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                HourToken(text="hh", twelve=False),
                VerbatimToken(text=":"),
                HourToken(text="hh", twelve=True),
                VerbatimToken(text=" "),
                AmPmToken(text="am/pm"),
            ],
            tokenize("hh:hh:hh am/pm", ".", ","),
        )


if __name__ == "__main__":
    unittest.main(
        failfast=True,
    )
