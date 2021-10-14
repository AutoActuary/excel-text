import unittest

from excel_text.main import text


class TestMain(unittest.TestCase):
    def test_1(self):
        a = text(1224.1234, "d")
        self.assertEqual("8", a)

    def test_2(self):
        a = text(1224.1234, "dd")
        self.assertEqual("08", a)


if __name__ == "__main__":
    unittest.main(failfast=True,)
