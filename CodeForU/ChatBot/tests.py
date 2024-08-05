# ChatBot/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from ChatBot.models import Question

User = get_user_model()

class QuestionModelTests(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            birth_date='1990-01-01',
            passport_id='123456789',
            gender='Male',
            password='testpassword123'
        )
        self.question = Question.objects.create(
            user=self.user.id,
            question_text='This is a test question'
        )

    def test_question_creation(self):
        # Create a question
        question = Question.objects.create(
            user=self.user.id,
            question_text='What is the capital of France?'
        )

        # Check if the question is created successfully
        self.assertEqual(question.user, self.user.id)
        self.assertEqual(question.question_text, 'What is the capital of France?')
        self.assertIsNotNone(question.created_at)

    def test_question_str_method(self):
        # Check the __str__ method
        self.assertEqual(str(self.question), f"Question by user ID {self.user.id} at {self.question.created_at}")

    def test_question_creation_with_null_user(self):
        # Create a question with null user
        question = Question.objects.create(
            user=None,
            question_text='What is the capital of France?'
        )

        # Check if the question is created successfully
        self.assertIsNone(question.user)
        self.assertEqual(question.question_text, 'What is the capital of France?')
        self.assertIsNotNone(question.created_at)

    def test_question_deletion(self):
        # Ensure the question is created
        self.assertEqual(Question.objects.count(), 1)

        # Delete the question directly
        self.question.delete()
        self.assertEqual(Question.objects.count(), 0)

    def test_user_deletion_does_not_delete_questions(self):
        # Ensure the question is created
        self.assertEqual(Question.objects.count(), 1)

        # Delete the user
        self.user.delete()
        self.assertEqual(Question.objects.count(), 1)  # The question remains because we use IntegerField for user

    def tearDown(self):
        if self.user.id:
            self.user.delete()
        Question.objects.all().delete()
