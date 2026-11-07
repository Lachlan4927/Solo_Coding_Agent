import sys
import unittest
sys.path.insert(0, "/workspace")

from multiplication import multiply

class TestMultiplication(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(multiply(2, 3), 6)

    def test_negative(self):
        self.assertEqual(multiply(-2, 3), -6)
        self.assertEqual(multiply(2, -3), -6)
        self.assertEqual(multiply(-2, -3), 6)

    def test_zero(self):
        self.assertEqual(multiply(0, 5), 0)
        self.assertEqual(multiply(5, 0), 0)
        self.assertEqual(multiply(0, 0), 0)

if __name__ == "__main__":
    unittest.main()
