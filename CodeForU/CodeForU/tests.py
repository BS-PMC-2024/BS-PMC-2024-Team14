from django.test import TestCase

class BasicMathTestCase(TestCase):
    def test_addition(self):
        """Test addition of two numbers"""
        self.assertEqual(2 + 2, 4)

class BasicMathTestCase2(TestCase):
    def test_addition(self):
        """Test addition of two numbers"""
        self.assertEqual(3 + 2, 5)
