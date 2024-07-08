from django.test import TestCase

# Create your tests here.
class BasicMathTestCase(TestCase):
    def test_addition(self):
        """Test addition of two numbers"""
        self.assertEqual(2 + 2, 4)