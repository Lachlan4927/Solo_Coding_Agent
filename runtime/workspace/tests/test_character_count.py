import sys
import unittest
sys.path.insert(0, "/workspace")

from character_count import count_characters

class TestCountCharacters(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(count_characters(""), 0)

    def test_simple(self):
        self.assertEqual(count_characters("abc"), 3)
        self.assertEqual(count_characters("a b c"), 5)

    def test_non_string_input(self):
        self.assertEqual(count_characters(123), 3)  # "123"
        self.assertEqual(count_characters(None), 4)  # "None"

if __name__ == "__main__":
    unittest.main()
