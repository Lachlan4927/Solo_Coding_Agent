import sys
import unittest
sys.path.insert(0, "/workspace")

from greeting import greet

class TestGreeting(unittest.TestCase):
    def test_greet(self):
        self.assertEqual(greet("Alice"), "Hello, Alice!")
        self.assertEqual(greet("World"), "Hello, World!")
        self.assertEqual(greet(""), "Hello, !")

if __name__ == "__main__":
    unittest.main()
