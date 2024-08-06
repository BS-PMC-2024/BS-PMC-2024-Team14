# ChatBot/tests.py


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from ChatBot.models import Question
from users.models import Student, Mentor

User = get_user_model()

class QuestionModelTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create test users
        self.student_user = User.objects.create_user(
            email='student@example.com',
            first_name='Student',
            last_name='User',
            phone='1234567890',
            birth_date='2000-01-01',
            passport_id='123456789',
            gender='Male',
            password='password123'
        )
        self.student = Student.objects.create(
            id=self.student_user.id,
            email=self.student_user.email,
            first_name=self.student_user.first_name,
            last_name=self.student_user.last_name,
            phone=self.student_user.phone,
            birth_date=self.student_user.birth_date,
            passport_id=self.student_user.passport_id,
            gender=self.student_user.gender,
            level=5
        )

        self.mentor_user = User.objects.create_user(
            email='mentor@example.com',
            first_name='Mentor',
            last_name='User',
            phone='1234567890',
            birth_date='1985-01-01',
            passport_id='987654321',
            gender='Female',
            password='password123'
        )

        self.mentor = Mentor.objects.create(
            id=self.mentor_user.id,
            email=self.mentor_user.email,
            first_name=self.mentor_user.first_name,
            last_name=self.mentor_user.last_name,
            phone=self.mentor_user.phone,
            birth_date=self.mentor_user.birth_date,
            passport_id=self.mentor_user.passport_id,
            gender=self.mentor_user.gender,
            is_approved=True
        )

        # Create test questions
        self.question1 = Question.objects.create(
            user=self.student_user.id,
            question_text='What is the capital of France?',
            level=1
        )
        self.question2 = Question.objects.create(
            user=self.mentor_user.id,
            question_text='What is the capital of Germany?',
            level=2
        )

    def test_question_creation(self):
        question = Question.objects.create(
            user=self.student_user.id,
            question_text='What is the capital of Spain?',
            level=3
        )
        self.assertEqual(question.user, self.student_user.id)
        self.assertEqual(question.question_text, 'What is the capital of Spain?')
        self.assertEqual(question.level, 3)
        self.assertIsNotNone(question.created_at)

    def test_question_creation_with_null_user(self):
        question = Question.objects.create(
            user=None,
            question_text='What is the capital of France?'
        )
        self.assertIsNone(question.user)
        self.assertEqual(question.question_text, 'What is the capital of France?')
        self.assertIsNotNone(question.created_at)

    def test_question_deletion(self):
        self.assertEqual(Question.objects.count(), 2)
        self.question1.delete()
        self.assertEqual(Question.objects.count(), 1)

    def test_user_deletion_does_not_delete_questions(self):
        self.assertEqual(Question.objects.count(), 2)
        self.student_user.delete()
        self.assertEqual(Question.objects.count(), 2)  # Questions remain because user is stored as an IntegerField

    def test_question_str_method(self):
        self.assertEqual(str(self.question1), f"Question by user ID {self.student_user.id} at {self.question1.created_at}")

    def test_save_question_view(self):
        self.client.login(email='student@example.com', password='password123')
        response = self.client.post(reverse('save_question'), {
            'question_text': 'What is the capital of Italy?',
            'level': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect after saving
        self.assertTrue(Question.objects.filter(question_text='What is the capital of Italy?').exists())


    def tearDown(self):
        User.objects.all().delete()
        Question.objects.all().delete()
        Student.objects.all().delete()
        Mentor.objects.all().delete()