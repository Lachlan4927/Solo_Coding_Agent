import sys
import unittest
sys.path.insert(0, "/workspace")

from even_check import is_even

class TestEvenCheck(unittest.TestCase):
    def test_even_positive(self):
        self.assertTrue(is_even(2))
        self.assertTrue(is_even(4))
        self.assertTrue(is_even(100))

    def test_odd_positive(self):
        self.assertFalse(is_even(1))
        self.assertFalse(is_even(3))
        self.assertFalse(is_even(101))

    def test_zero(self):
        self.assertTrue(is_even(0))

    def test_even_negative(self):
        self.assertTrue(is_even(-2))
        self.assertTrue(is_even(-4))
        self.assertTrue(is_even(-100))

    def test_odd_negative(self):
        self.assertFalse(is_even(-1))
        self.assertFalse(is_even(-3))
        self.assertFalse(is_even(-101))

    def test_type_error(self):
        with self.assertRaises(TypeError):
            is_even(2.0)
        with self.assertRaises(TypeError):
            is_even("2")

if __name__ == "__main__":
    unittest.main()
