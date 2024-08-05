from django.test import TestCase
import unittest

# Import the test cases from the users and ChatBot apps
from users.tests import RegisterViewTests, LogoutViewTest, StudentProfileTests, MentorProfileTests
from ChatBot.tests import QuestionModelTests

# Create a test suite that includes the user and ChatBot tests
def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(RegisterViewTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(LogoutViewTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StudentProfileTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MentorProfileTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(QuestionModelTests))
    return suite

# Create a test case to run the suite
class MainAppTestSuite(TestCase):

    def test_all_apps(self):
        runner = unittest.TextTestRunner()
        result = runner.run(suite())
        self.assertTrue(result.wasSuccessful())