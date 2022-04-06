import datetime
import unittest
from excel_text import text, get_text_function
from excel_text.errors import ValueExcelError


class TestText(unittest.TestCase):
    def test_1(self):
        self.assertEqual(
            "8",
            text(1224.1234, "d"),
        )

    def test_2(self):
        self.assertEqual(
            "08",
            text(1224.1234, "dd"),
        )

    def test_3(self):
        self.assertEqual(
            "Sat",
            text(1204.1234, "ddd"),
        )

    def test_4(self):
        self.assertEqual(
            "Sunday",
            text(1233.1234, "dddd"),
        )

    def test_5(self):
        self.assertEqual(
            "1903",
            text(1231.1234, "YYYY"),
        )

    def test_6(self):
        self.assertEqual(
            "03/5/18",
            text(1234.1234, "yy/m/d"),
        )

    def test_7(self):
        self.assertEqual(
            "1903/M",
            text(1234.1234, "yyyy/mmmmm"),
        )

    def test_8(self):
        self.assertEqual(
            "1903 July",
            text(1294.1234, "yyyy mmmm"),
        )

    def test_9(self):
        self.assertEqual(
            "1903 Jun",
            text(1264.1234, "yyyy mmm"),
        )

    def test_10(self):
        self.assertEqual(
            "1903/05",
            text(1234.1234, "yyyy/mm"),
        )

    def test_11(self):
        self.assertEqual(
            "1903/5",
            text(1234.1234, "yyyy/m"),
        )

    def test_12(self):
        self.assertEqual(
            "1903/05/18 02:57:42",
            text(1234.1234, "yyyy/mm/dd hh:mm:ss"),
        )

    def test_13(self):
        self.assertEqual(
            "1903/05/18 21:02:10",
            text(1234.8765, "yyyy/mm/dd hh:mm:ss"),
        )

    def test_14(self):
        self.assertEqual(
            "1903/05/18 09:02:10 PM",
            text(1234.8765, "yyyy/mm/dd hh:mm:ss AM/PM"),
        )

    def test_15(self):
        self.assertEqual(
            "1903/05/18 21:02:09.60",
            text(1234.8765, "yyyy/mm/dd hh:mm:ss.00"),
        )

    def test_16(self):
        self.assertEqual(
            "1903/05/18 21:02:26.9",
            text(1234.8766998, "yyyy/mm/dd hh:mm:ss.0"),
        )

    def test_17(self):
        self.assertEqual(
            "10:57:55",
            text(123.45689, "hh:mm:ss"),
        )

    def test_18(self):
        self.assertEqual(
            "10:55",
            text(123.45689, "hh:ss"),
        )

    def test_19(self):
        self.assertEqual(
            "57:55",
            text(123.45689, "mm:ss"),
        )

    def test_20(self):
        self.assertEqual(
            "55.30",
            text(123.45689, "ss.00"),
        )

    def test_21(self):
        self.assertEqual(
            "06:51:42",
            text(653.2859, "hh:::mm:ss"),
        )

    def test_22(self):
        self.assertEqual(
            "29629:02:12",
            text(1234.5432, "[hh]:mm:ss"),
        )

    def test_23(self):
        self.assertEqual(
            "1777742:12",
            text(1234.5432, "[mm]:ss"),
        )

    def test_24(self):
        self.assertEqual(
            "106664532",
            text(1234.5432, "[ss]"),
        )

    def test_25(self):
        self.assertEqual(
            "46932",
            text(0.5432, "[ss]"),
        )

    def test_26(self):
        self.assertEqual(
            "4",
            text(datetime.datetime(2024, 10, 4, 5, 3, 4), "d"),
        )

    def test_27(self):
        self.assertEqual(
            "5",
            text(datetime.time(5, 3, 4), "h"),
        )

    def test_28(self):
        self.assertEqual(
            "24",
            text(datetime.date(2024, 10, 4), "y"),
        )

    def test_29(self):
        self.assertEqual(
            "303",
            text(datetime.time(5, 3, 4), "[m]"),
        )

    def test_30(self):
        self.assertEqual(
            "1093656",
            text(datetime.date(2024, 10, 4), "[h]"),
        )

    def test_31(self):
        self.assertEqual(
            "$1,234.124",
            text(1234.1239, "$#,##0.000"),
        )

    def test_32(self):
        self.assertEqual(
            "R1,234.0",
            text(1234, "R#,##0.0"),
        )

    def test_33(self):
        self.assertEqual(
            "r1,234.0000",
            text(1234, "r#,##0.0000"),
        )

    def test_34(self):
        self.assertEqual(
            "$234.124",
            text(234.1239, "$#,##0.000"),
        )

    def test_35(self):
        self.assertEqual(
            "$0.1",
            text(0.1239, "$#,##0.0"),
        )

    def test_36(self):
        self.assertEqual(
            "m1,234.1",
            text(1234.1239, '"m"#,##0.0'),
        )

    def test_37(self):
        self.assertEqual(
            "m1,234.0",
            text(1234, '"m"#,##0.0'),
        )

    def test_38(self):
        self.assertEqual(
            "R1,234.0",
            text(1234, "R#,##0.0"),
        )

    def test_38_b(self):
        self.assertEqual(
            "R1,234,567.0",
            text(1234567, "R#,##0.0"),
        )

    def test_39(self):
        self.assertEqual(
            "678.",
            text(678.123, "."),
        )

    def test_40(self):
        self.assertEqual(
            "28.6%",
            text(0.2859, "0.0%"),
        )

    def test_41(self):
        self.assertEqual(
            "28.59%",
            text(0.2859, "00.00%"),
        )

    def test_42(self):
        self.assertEqual(
            "028.590%",
            text(0.2859, "000.000%"),
        )

    def test_43(self):
        self.assertEqual(
            "0001234",
            text(1234, "0000000"),
        )

    def test_44(self):
        self.assertEqual(
            "1234",
            text(1234, "0000"),
        )

    def test_45(self):
        self.assertEqual(
            "1234",
            text(1234, "000"),
        )

    def test_46(self):
        self.assertEqual(
            "12° 34' 56''",
            text(123456, "##0° 00' 00''"),
        )

    def test_47(self):
        self.assertEqual(
            "912° 34' 56''",
            text(9123456, "##0° 00' 00''"),
        )

    def test_48(self):
        self.assertEqual(
            "-R 3,463.46",
            text(-3463.456, "R #,##0.00"),
        )

    def test_49(self):
        self.assertEqual(
            "-0034",
            text(-34.456, "R #,##0.00;0000"),
        )

    def test_50(self):
        self.assertEqual(
            "0543",
            text(543.234, "[>543]0000;#0.0"),
        )

    def test_51(self):
        self.assertEqual(
            "543.2",
            text(543.234, "[<543]0000;#0.0"),
        )

    def test_52(self):
        self.assertEqual(
            "13032",
            text(543, "[=543][h];yyyymm"),
        )

    def test_error(self):
        with self.assertRaises(ValueExcelError):
            text(123.123, "[>1000$# ##0.0"),

        text1 = get_text_function({"raise": False})
        self.assertEqual(
            str(
                ValueExcelError(
                    "A value used in the formula is of the wrong data type."
                )
            ),
            str(text1(123.123, "[>1000$# ##0.0")),
        )

    def test_decimal_and_thousands(self):
        text_with_underscores = get_text_function({"thousands": "_"})
        self.assertEqual(
            "123_123_123_123_123.00",
            text_with_underscores(123123123123123, "#_##0.00"),
        )

        text_with_spaces = get_text_function({"thousands": " "})
        self.assertEqual(
            "123 123 123 123 123.00",
            text_with_spaces(123123123123123, "# ##0.00"),
        )

        text_point_comma = get_text_function({"thousands": ".", "decimal": ","})
        self.assertEqual(
            "123.123.123.123.123,00",
            text_point_comma(123123123123123, "#.##0,00"),
        )

        text_space_comma = get_text_function({"thousands": " ", "decimal": ","})
        self.assertEqual(
            "23 123 123 123 123,12",
            text_space_comma(23123123123123.123, "# ##0,00"),
        )


if __name__ == "__main__":
    unittest.main(
        failfast=True,
    )
