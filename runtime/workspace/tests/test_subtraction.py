import sys
import unittest
sys.path.insert(0, "/workspace")
from subtraction import subtract

class TestSubtract(unittest.TestCase):
    def test_positive(self):
        self.assertEqual(subtract(5, 3), 2)
        self.assertEqual(subtract(10, 0), 10)
    def test_negative(self):
        self.assertEqual(subtract(-5, -3), -2)
        self.assertEqual(subtract(-10, 5), -15)
    def test_zero_and_equal(self):
        self.assertEqual(subtract(0, 0), 0)
        self.assertEqual(subtract(7, 7), 0)

if __name__ == "__main__":
    unittest.main()
