import unittest

from ChatBot.tests import QuestionModelTests
from django.test import TestCase

# Import the test cases from the users and ChatBot apps
from users.tests import (
    HelpRequestAndViewTest,
    LogoutConfirmationTests,
    LogoutViewTest,
    MentorProfileTests,
    PasswordResetTests,
    QuestionsListViewTests,
    RegisterViewTests,
    StudentDashboardViewTests,
    StudentFeedbackViewTests,
    StudentMentorRequestAndViewTest,
    StudentProfileTests,
    GetHintViewTest,
    AnswerQuestionViewTest,
    GradeQuestionViewTest,
    UserNotificationTest,
    GetHintForGradingViewTest
)


# Create a test suite that includes the user and ChatBot tests
def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(RegisterViewTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(LogoutViewTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(StudentProfileTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(MentorProfileTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(HelpRequestAndViewTest))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(StudentMentorRequestAndViewTest)
    )
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(QuestionsListViewTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(QuestionModelTests))
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(StudentDashboardViewTests)
    )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(StudentFeedbackViewTests)
    )
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(LogoutConfirmationTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(PasswordResetTests))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(GetHintViewTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(AnswerQuestionViewTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(GradeQuestionViewTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(UserNotificationTest))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(GetHintForGradingViewTest))
    return suite


# Create a test case to run the suite
class MainAppTestSuite(TestCase):

    def test_all_apps(self):
        runner = unittest.TextTestRunner()
        result = runner.run(suite())
        self.assertTrue(result.wasSuccessful())
