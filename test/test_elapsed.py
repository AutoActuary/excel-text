import datetime
import unittest

from excel_text.elapsed import elapsed_hours


class TestElapsedHours(unittest.TestCase):
    def test_time(self):
        self.assertEqual(1, elapsed_hours(datetime.time(1)))
        self.assertEqual(2.5, elapsed_hours(datetime.time(2, 30)))

    def test_1900_leap_year(self):
        # February 10th
        self.assertEqual(984, elapsed_hours(datetime.date(1900, 2, 10)))
        self.assertEqual(984, elapsed_hours(datetime.datetime(1900, 2, 10)))
        self.assertEqual(986, elapsed_hours(datetime.datetime(1900, 2, 10, 2)))

        # February 28th, just before the leap day
        self.assertEqual(1416, elapsed_hours(datetime.date(1900, 2, 28)))
        self.assertEqual(1416, elapsed_hours(datetime.datetime(1900, 2, 28)))
        self.assertEqual(1439, elapsed_hours(datetime.datetime(1900, 2, 28, 23)))

        # February 29th, which did not really exist. We can't test this here, because `datetime.date(1900, 2, 29)` is
        # not valid in Python. But `DATE(1900, 2, 29)` works in Excel.
        # self.assertEqual(1440, elapsed_hours(datetime.date(1900, 2, 29)))
        # self.assertEqual(1440, elapsed_hours(datetime.datetime(1900, 2, 29)))
        # self.assertEqual(1441, elapsed_hours(datetime.datetime(1900, 2, 29, 1)))

        # March 1st, just after the leap day
        self.assertEqual(1464, elapsed_hours(datetime.date(1900, 3, 1)))
        self.assertEqual(1464, elapsed_hours(datetime.datetime(1900, 3, 1)))
        self.assertEqual(1465, elapsed_hours(datetime.datetime(1900, 3, 1, 1)))

        # March 10th
        self.assertEqual(1680, elapsed_hours(datetime.date(1900, 3, 10)))
        self.assertEqual(1680, elapsed_hours(datetime.datetime(1900, 3, 10)))
        self.assertEqual(1682, elapsed_hours(datetime.datetime(1900, 3, 10, 2)))

    def test_1903_not_leap_year(self):
        self.assertEqual(29616, elapsed_hours(datetime.date(1903, 5, 18)))
        self.assertEqual(29616, elapsed_hours(datetime.datetime(1903, 5, 18)))

    def test_1904_leap_year(self):
        # February 28th
        self.assertEqual(36480, elapsed_hours(datetime.date(1904, 2, 28)))
        self.assertEqual(36492, elapsed_hours(datetime.datetime(1904, 2, 28, 12)))

        # February 29th
        self.assertEqual(36504, elapsed_hours(datetime.date(1904, 2, 29)))
        self.assertEqual(36516, elapsed_hours(datetime.datetime(1904, 2, 29, 12)))

        # March 1st
        self.assertEqual(36528, elapsed_hours(datetime.date(1904, 3, 1)))
        self.assertEqual(36540, elapsed_hours(datetime.datetime(1904, 3, 1, 12)))


if __name__ == "__main__":
    unittest.main(
        failfast=True,
    )
