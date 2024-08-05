from django.test import TestCase
from django.contrib.auth import get_user_model
from ChatBot.models import Question

class QuestionModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            birth_date='2000-01-01',
            passport_id='123456789',
            gender='Male',
            password='password123'
        )
        self.question = Question.objects.create(
            user=self.user,
            question_text='This is a test question'
        )

    def test_question_deletion(self):
        # Ensure the question is created
        self.assertEqual(Question.objects.count(), 1)

        # Delete the question directly
        self.question.delete()
        self.assertEqual(Question.objects.count(), 0)

    def test_user_deletion_deletes_questions(self):
        # Ensure the question is created
        self.assertEqual(Question.objects.count(), 1)

        # Delete the user
        self.user.delete()
        self.assertEqual(Question.objects.count(), 0)

    def tearDown(self):
        if self.user.id:
            self.user.delete()
        Question.objects.all().delete()
