import unittest

from excel_text.temp import temp


class TestTemp(unittest.TestCase):
    def test_1(self):
        a = temp()
        self.assertEqual(3, a)


if __name__ == "__main__":
    unittest.main(
        failfast=True,
    )