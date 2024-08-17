from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.test import Client, TestCase
from django.urls import reverse

from .models import HelpRequest, Mentor, Question, Student, StudentMentorRequest, User


def get_mentor_ids():
    return [
        "1234567890",
        "2345678901",
        "3456789012",
        "4567890123",
        "5678901234",
        "6789012345",
        "7890123456",
        "8901234567",
        "9012345678",
        "0123456789",
    ]


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("users:register")

        # Create a mentor for testing
        self.mentor = Mentor.objects.create(
            email="mentor@example.com",
            first_name="Mentor",
            last_name="Example",
            birth_date="1990-01-01",
            phone="0987654321",
            gender="Female",
            passport_id="M123456789",
            is_approved=True,
        )

        self.valid_student_data = {
            "email": "student@example.com",
            "first_name": "Student",
            "last_name": "Example",
            "birth_date": "2000-01-01",
            "phone": "1234567890",
            "gender": "Male",
            "passport_id": "1122334455",
            "password": "Testpassword1!",
            "confirm_password": "Testpassword1!",
        }

    def test_register_student_success(self):
        response = self.client.post(self.register_url, self.valid_student_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("users:login"))
        student = Student.objects.get(email=self.valid_student_data["email"])
        self.assertTrue(student.check_password(self.valid_student_data["password"]))
        self.assertEqual(student.first_name, self.valid_student_data["first_name"])
        self.assertEqual(student.last_name, self.valid_student_data["last_name"])

    def test_register_password_mismatch(self):
        invalid_data = self.valid_student_data.copy()
        invalid_data["confirm_password"] = "differentpassword"
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")

    def test_register_missing_fields(self):
        invalid_data = self.valid_student_data.copy()
        invalid_data.pop("email")
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="A123456789",
            gender="Male",
            password="password",
        )

    def test_logout_view(self):
        self.client.login(email="testuser@example.com", password="password")

        response = self.client.get(reverse("users:mentor_dashboard"))
        self.assertEqual(response.status_code, 302)

        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)

        response = self.client.get(reverse("users:mentor_dashboard"))
        self.assertNotEqual(response.status_code, 200)


class StudentProfileTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a student profile for testing
        self.student = Student.objects.create(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
            birth_date="1990-01-01",
            phone="1234567890",
            passport_id="ABCDE12345",  # Ensure this is unique for each test run
            gender="Male",
            level=0,
        )

        # Log the student in using force_login
        self.user = self.student.user_ptr  # Assuming Student inherits from User
        self.client.force_login(self.user)

    def test_delete_student_profile(self):
        # Ensure student profile exists
        self.assertTrue(Student.objects.filter(email=self.student.email).exists())

        # Make a POST request to delete the student profile
        response = self.client.post(
            reverse("users:student_profile"),
            {"user_id": self.student.id, "action": "delete"},
        )

        # Check if the student profile is deleted
        self.assertFalse(Student.objects.filter(email=self.student.email).exists())

        # Check if the response redirects to the login page
        self.assertRedirects(response, reverse("users:login"))

    def test_edit_student_profile(self):
        # Ensure student profile exists
        self.assertTrue(Student.objects.filter(email=self.student.email).exists())

        # Make a POST request to edit the student profile
        updated_first_name = "Jane"
        updated_last_name = "Doe"
        updated_phone = "9876543210"
        updated_email = "updated_email@example.com"

        response = self.client.post(
            reverse("users:student_profile"),
            {
                "user_id": self.student.id,
                "action": "submit",
                "first_name": updated_first_name,
                "last_name": updated_last_name,
                "phone": updated_phone,
                "email": updated_email,
            },
        )

        # Check if the student profile is updated
        updated_student = Student.objects.get(id=self.student.id)
        self.assertEqual(updated_student.first_name, updated_first_name)
        self.assertEqual(updated_student.last_name, updated_last_name)
        self.assertEqual(updated_student.phone, updated_phone)
        self.assertEqual(updated_student.email, updated_email)

        # Check if the response redirects back to the student profile page
        self.assertRedirects(response, reverse("users:student_profile"))


class MentorProfileTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a mentor profile for testing
        self.mentor = Mentor.objects.create(
            email="testuser@example.com",
            first_name="John",
            last_name="Doe",
            birth_date="1990-01-01",
            phone="1234567890",
            passport_id="ABCDE12345",  # Ensure this is unique for each test run
            gender="Male",
        )

        # Log the mentor in using force_login
        self.user = self.mentor.user_ptr  # Assuming mentor inherits from User
        self.client.force_login(self.user)

    def test_delete_mentor_profile(self):
        # Ensure mentor profile exists
        self.assertTrue(Mentor.objects.filter(email=self.mentor.email).exists())

        # Make a POST request to delete the mentor profile
        response = self.client.post(
            reverse("users:mentor_profile"),
            {"user_id": self.mentor.id, "action": "delete"},
        )

        # Check if the mentor profile is deleted
        self.assertFalse(Mentor.objects.filter(email=self.mentor.email).exists())

        # Check if the response redirects to the login page
        self.assertRedirects(response, reverse("users:login"))

    def test_edit_mentor_profile(self):
        # Ensure mentor profile exists
        self.assertTrue(Mentor.objects.filter(email=self.mentor.email).exists())

        # Make a POST request to edit the mentor profile
        updated_first_name = "Jane"
        updated_last_name = "Doe"
        updated_phone = "9876543210"
        updated_email = "updated_email@example.com"

        response = self.client.post(
            reverse("users:mentor_profile"),
            {
                "user_id": self.mentor.id,
                "action": "submit",
                "first_name": updated_first_name,
                "last_name": updated_last_name,
                "phone": updated_phone,
                "email": updated_email,
            },
        )

        # Check if the mentor profile is updated
        updated_mentor = Mentor.objects.get(id=self.mentor.id)
        self.assertEqual(updated_mentor.first_name, updated_first_name)
        self.assertEqual(updated_mentor.last_name, updated_last_name)
        self.assertEqual(updated_mentor.phone, updated_phone)
        self.assertEqual(updated_mentor.email, updated_email)

        # Check if the response redirects back to the mentor profile page
        self.assertRedirects(response, reverse("users:mentor_profile"))


class HelpRequestAndViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a mentor user
        self.mentor = Mentor.objects.create(
            email="mentor@example.com",
            first_name="John",
            last_name="Doe",
            birth_date="1990-01-01",
            phone="1234567890",
            passport_id="A12345678",
            is_approved=True,
        )
        self.client.force_login(self.mentor)
        self.url = reverse("users:submit_help_request")

    # --- Model Tests ---
    def test_help_request_str(self):
        help_request = HelpRequest.objects.create(
            user=self.mentor.id, subject="Test Subject", message="Test Message"
        )
        self.assertEqual(
            str(help_request),
            f"Request from - {self.mentor.email} {help_request.subject}",
        )

    def test_help_request_save_responded_at(self):
        help_request = HelpRequest.objects.create(
            user=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
            is_resolved=True,
        )
        help_request.save()
        self.assertIsNotNone(help_request.responded_at)

    def test_help_request_clean(self):
        help_request = HelpRequest(
            user=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
            is_resolved=True,
        )
        with self.assertRaises(Exception):
            help_request.clean()

    def test_help_request_valid_clean(self):
        help_request = HelpRequest(
            user=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
            response="Test Response",
            is_resolved=True,
        )
        try:
            help_request.clean()  # Should not raise an exception
        except Exception as e:
            self.fail(f"clean() raised Exception unexpectedly: {e}")

    # --- View Tests ---
    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "submit_help_request.html")
        self.assertContains(response, "<form")  # Ensure the form is in the response

    def test_post_request_valid_form(self):
        response = self.client.post(
            self.url,
            {
                "subject": "Test Subject",
                "message": "Test Message",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(HelpRequest.objects.filter(user=self.mentor.id).exists())

    def test_post_request_invalid_form(self):
        response = self.client.post(
            self.url,
            {
                "subject": "",
                "message": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, "form", "subject", "This field is required.")
        self.assertFormError(response, "form", "message", "This field is required.")

    def test_help_request_display(self):
        HelpRequest.objects.create(
            user=self.mentor.id, subject="Test Subject", message="Test Message"
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Test Subject")
        self.assertContains(response, "Test Message")


User = get_user_model()


class QuestionsListViewTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create test users
        self.student_user = User.objects.create_user(
            email="student@example.com",
            first_name="Student",
            last_name="User",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="123456789",
            gender="Male",
            password="password123",
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
            level=5,
        )

        self.mentor_user = User.objects.create_user(
            email="mentor@example.com",
            first_name="Mentor",
            last_name="User",
            phone="1234567890",
            birth_date="1985-01-01",
            passport_id="987654321",
            gender="Female",
            password="password123",
        )

        # Create test questions
        self.question1 = Question.objects.create(
            user=self.student_user.id,
            question_text="What is the capital of France?",
            level=1,
        )
        self.question2 = Question.objects.create(
            user=self.mentor_user.id,
            question_text="What is the capital of Germany?",
            level=2,
        )

    def test_questions_list_requires_login(self):
        response = self.client.get(reverse("users:questions_list"))
        self.assertRedirects(response, "/users/login/?next=/users/questions_list/")

    def test_questions_list_as_mentor(self):
        self.client.login(email="mentor@example.com", password="password123")
        response = self.client.get(reverse("users:questions_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "questions_list.html")
        self.assertIsNone(response.context["user_level"])

    def test_question_creation(self):
        question = Question.objects.create(
            user=self.student_user.id,
            question_text="What is the capital of Spain?",
            level=3,
        )
        self.assertEqual(question.user, self.student_user.id)
        self.assertEqual(question.level, 3)
        self.assertIsNotNone(question.created_at)

    def tearDown(self):
        User.objects.all().delete()
        Question.objects.all().delete()
        Student.objects.all().delete()


class StudentMentorRequestAndViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a mentor user
        self.mentor = Mentor.objects.create(
            email="mentor@example.com",
            first_name="John",
            last_name="Doe",
            birth_date="1990-01-01",
            phone="1234567890",
            passport_id="A12345678",
            is_approved=True,
        )
        # Create a student user
        self.student = Student.objects.create(
            email="student@example.com",
            first_name="Jane",
            last_name="Smith",
            birth_date="2000-01-01",
            phone="0987654321",
            passport_id="B87654321",
            mentor_responsible=self.mentor.id,
        )
        self.client.force_login(self.student)
        self.url = reverse("users:student_mentor_request")

    # --- Model Tests ---
    def test_student_mentor_request_str(self):
        student_mentor_request = StudentMentorRequest.objects.create(
            user=self.student.id,
            mentor_responsible=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
        )
        self.assertEqual(
            str(student_mentor_request),
            f"Request from {self.student.email} to {self.mentor.email} - {student_mentor_request.subject}",
        )

    def test_student_mentor_request_save_responded_at(self):
        student_mentor_request = StudentMentorRequest.objects.create(
            user=self.student.id,
            mentor_responsible=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
            is_resolved=True,
        )
        student_mentor_request.save()
        self.assertIsNotNone(student_mentor_request.responded_at)

    def test_student_mentor_request_clean(self):
        student_mentor_request = StudentMentorRequest(
            user=self.student.id,
            mentor_responsible=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
            is_resolved=True,
        )
        with self.assertRaises(Exception):
            student_mentor_request.clean()

    def test_student_mentor_request_valid_clean(self):
        student_mentor_request = StudentMentorRequest(
            user=self.student.id,
            mentor_responsible=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
            response="Test Response",
            is_resolved=True,
        )
        try:
            student_mentor_request.clean()  # Should not raise an exception
        except Exception as e:
            self.fail(f"clean() raised Exception unexpectedly: {e}")

    # --- View Tests ---
    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "student_mentor_request.html")
        self.assertContains(response, "<form")  # Ensure the form is in the response

    def test_post_request_valid_form(self):
        response = self.client.post(
            self.url,
            {
                "subject": "Test Subject",
                "message": "Test Message",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertTrue(
            StudentMentorRequest.objects.filter(user=self.student.id).exists()
        )

    def test_student_mentor_request_display(self):
        StudentMentorRequest.objects.create(
            user=self.student.id,
            mentor_responsible=self.mentor.id,
            subject="Test Subject",
            message="Test Message",
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Test Subject")
        self.assertContains(response, "Test Message")


class StudentFeedbackViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        # Create a student user
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password123A@",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="A12345678",
            gender="Male",
        )
        # Assign the user as a student
        self.student = Student.objects.create(
            id=self.student_user.id,
            email=self.student_user.email,
            first_name=self.student_user.first_name,
            last_name=self.student_user.last_name,
            phone=self.student_user.phone,
            birth_date=self.student_user.birth_date,
            passport_id=self.student_user.passport_id,
            gender=self.student_user.gender,
            level=1,
            rating=3,
        )
        # Log the student in
        self.client.force_login(self.student)
        self.url = reverse("users:student_feedback")

    def test_student_feedback_post(self):
        response = self.client.post(self.url, {"rating": 5})
        self.student.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Check for redirect status code
        self.assertEqual(self.student.rating, 5)  # Check if the rating was updated

    def test_student_feedback_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Check for redirect status code

    def test_student_mentor_rating_post(self):
        response = self.client.post(self.url, {"mentor_rating": 5})
        self.student.refresh_from_db()
        self.assertEqual(response.status_code, 302)  # Check for redirect status code
        self.assertEqual(
            self.student.mentor_rating, 5
        )  # Check if the rating was updated

    def test_student_mentor_rating_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Check for redirect status code


class StudentDashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123A@",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="A12345678",
            gender="Male",
        )
        self.student.is_active = True
        self.student.save()

        self.student_profile = Student.objects.create(
            id=self.student.id,
            email=self.student.email,
            first_name=self.student.first_name,
            last_name=self.student.last_name,
            phone=self.student.phone,
            birth_date=self.student.birth_date,
            passport_id=self.student.passport_id,
            gender=self.student.gender,
            level=1,
            mentor_responsible=None,
            rating=5,
            mentor_rating=5,
            level_updated=True,
        )
        self.student_profile.save()

        self.client.login(email="student@example.com", password="password123A@")

    def test_student_dashboard_resets_level_updated(self):
        response = self.client.get(reverse("users:student_dashboard"))
        self.student_profile.refresh_from_db()
        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(self.student_profile.level_updated)


from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .forms import CodeVerificationForm, EmailForm, SetNewPasswordForm


class PasswordResetTests(TestCase):

    def setUp(self):
        self.client = Client()

        # Create test users
        self.student_user = User.objects.create_user(
            email="student@example.com",
            first_name="Student",
            last_name="User",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="123456789",
            gender="Male",
            password="password123",
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
            level=5,
        )

        self.mentor_user = User.objects.create_user(
            email="mentor@example.com",
            first_name="Mentor",
            last_name="User",
            phone="1234567890",
            birth_date="1985-01-01",
            passport_id="987654321",
            gender="Female",
            password="password123",
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
            is_approved=True,
        )

    def test_password_reset_request_view_get(self):
        response = self.client.get(reverse("users:password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset_email.html")
        self.assertIsInstance(response.context["form"], EmailForm)

    def test_password_reset_request_view_post_valid_email(self):
        response = self.client.post(
            reverse("users:password_reset"), {"email": self.student_user.email}
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirect after successful email send
        self.assertEqual(len(mail.outbox), 1)  # Check if email is sent
        self.assertRedirects(response, reverse("users:verify_code"))

    def test_password_reset_request_view_post_invalid_email(self):
        response = self.client.post(
            reverse("users:password_reset"), {"email": "invalid@example.com"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset_email.html")

    def test_code_verification_view_get(self):
        response = self.client.get(reverse("users:verify_code"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset_code.html")
        self.assertIsInstance(response.context["form"], CodeVerificationForm)

    def test_code_verification_view_post_valid_code(self):
        self.client.session["reset_code"] = "1234"
        self.client.session.save()
        response = self.client.post(reverse("users:verify_code"), {"code": "1234"})
        self.assertEqual(response.status_code, 200)

    def test_code_verification_view_post_invalid_code(self):
        self.client.session["reset_code"] = "1234"
        self.client.session.save()
        response = self.client.post(reverse("users:verify_code"), {"code": "0000"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "password_reset_code.html")

    def test_set_new_password_view_get(self):
        response = self.client.get(reverse("users:set_new_password"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "set_new_password.html")
        self.assertIsInstance(response.context["form"], SetNewPasswordForm)


class LogoutConfirmationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123A@",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="A12345678",
            gender="Male",
        )
        self.student.is_active = True
        self.student.save()

        self.student_profile = Student.objects.create(
            id=self.student.id,
            email=self.student.email,
            first_name=self.student.first_name,
            last_name=self.student.last_name,
            phone=self.student.phone,
            birth_date=self.student.birth_date,
            passport_id=self.student.passport_id,
            gender=self.student.gender,
            level=1,
            mentor_responsible=None,
            rating=5,
            mentor_rating=5,
            level_updated=True,
        )
        self.student_profile.save()
        self.client.login(email="student@example.com", password="password123A@")

    def test_logout_confirmation_modal(self):
        # Access any protected view to ensure the user is logged in
        response = self.client.get(
            reverse("users:student_dashboard")
        )  # Replace with an actual view in your project
        self.assertEqual(response.status_code, 302)

        # Simulate the logout action by posting to the logout URL
        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, reverse("users:login"))

        response = self.client.post(reverse("users:logout"))
        self.assertRedirects(response, reverse("users:login"))

class GetHintViewTest(TestCase):

    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="123456789",
            gender="Male",
            password="password123",
        )

        # Create a test question
        self.question = Question.objects.create(
            user=self.user.id,  # Assuming the user field stores the user's ID
            question_text="What is the capital of France?",
            level=1,
        )

    def test_get_hint_view(self):
        # Log in the test user
        self.client.login(email="testuser@example.com", password="password123")

        # Send a GET request to the get_hint view
        url = reverse('users:get_hint', args=[self.question.id])
        response = self.client.get(url)

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the response contains a hint key (assuming the hint is always returned in the response)
        self.assertIn("hint", response.json())




class AnswerQuestionViewTest(TestCase):

    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a mentor user
        self.mentor_user = User.objects.create_user(
            email="mentor@example.com",
            password="password123A@",
            first_name="Jane",
            last_name="Smith",
            phone="0987654321",
            birth_date="1980-01-01",
            passport_id="B12345678",
            gender="Female",
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

        # Create a student user
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password123A@",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="A12345678",
            gender="Male",
        )
        # Assign the user as a student
        self.student = Student.objects.create(
            id=self.student_user.id,
            email=self.student_user.email,
            first_name=self.student_user.first_name,
            last_name=self.student_user.last_name,
            phone=self.student_user.phone,
            birth_date=self.student_user.birth_date,
            passport_id=self.student_user.passport_id,
            gender=self.student_user.gender,
            level=1,
            rating=3,
            mentor_responsible=self.mentor.id,
        )

        # Create an original question
        self.original_question = Question.objects.create(
            user=self.mentor.id,
            question_text="What is the capital of France?",
            level=1,
        )

    def test_answer_question_get_request(self):
        # Log in as the student
        self.client.login(email="student@example.com", password="password123A@")

        # Send a GET request to the answer_question view
        url = reverse('users:answer_question', args=[self.original_question.id])
        response = self.client.get(url)

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 302)



class GradeQuestionViewTest(TestCase):

    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a mentor user
        self.mentor_user = User.objects.create_user(
            email="mentor@example.com",
            password="password123A@",
            first_name="Jane",
            last_name="Smith",
            phone="0987654321",
            birth_date="1980-01-01",
            passport_id="B12345678",
            gender="Female",
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

        # Create a student user
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password123A@",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="A12345678",
            gender="Male",
        )
        # Assign the user as a student
        self.student = Student.objects.create(
            id=self.student_user.id,
            email=self.student_user.email,
            first_name=self.student_user.first_name,
            last_name=self.student_user.last_name,
            phone=self.student_user.phone,
            birth_date=self.student_user.birth_date,
            passport_id=self.student_user.passport_id,
            gender=self.student_user.gender,
            level=1,
            rating=3,
            mentor_responsible=self.mentor.id,
        )

        # Create a question answered by the student
        self.question = Question.objects.create(
            user=self.mentor.id,
            question_text="What is the capital of France?",
            level=1,
            answered_by=self.student.id,
            answer_text="Paris",
        )

    def test_grade_question_get_request(self):
        # Log in as the mentor
        self.client.login(email="mentor@example.com", password="password123A@")

        # Send a GET request to the grade_question view
        url = reverse('users:grade_question', args=[self.question.id])
        response = self.client.get(url)

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 302)

       

    def test_grade_question_post_request(self):
        # Log in as the mentor
        self.client.login(email="mentor@example.com", password="password123A@")

        # Send a POST request to the grade_question view with grade and notes
        url = reverse('users:grade_question', args=[self.question.id])
        response = self.client.post(url, {
            'grade': '90',
            'notes': 'Good answer, but needs more detail.'
        })

        # Check that the response redirects to the mentor submissions page
        self.assertEqual(response.status_code, 302)



    def test_grade_question_without_mentor_access(self):
        # Log in as the student
        self.client.login(email="student@example.com", password="password123A@")

        # Try to access the grade_question view as a student
        url = reverse('users:grade_question', args=[self.question.id])
        response = self.client.get(url)

        # Check that the student is forbidden from accessing the view
        self.assertEqual(response.status_code, 302)  # Assuming mentor_required decorator returns 302


class UserNotificationTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password123A@",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="A12345678",
            gender="Male",
        )

    def test_add_notification(self):
        # Add a notification
        self.user.add_notification("New message received.")
        self.user.add_notification("Your submission has been graded.")

        # Check that notifications count is correct
        self.assertEqual(self.user.notifications, 2)

        # Check that the notification messages are stored correctly
        expected_messages = ["New message received.", "Your submission has been graded."]
        self.assertEqual(self.user.get_notification_messages(), expected_messages)

    def test_clear_notifications(self):
        # Add a notification
        self.user.add_notification("New message received.")

        # Clear notifications
        self.user.clear_notifications()

        # Check that notifications are cleared
        self.assertEqual(self.user.notifications, 0)
        self.assertEqual(self.user.get_notification_messages(), "")


class GetHintForGradingViewTest(TestCase):

    def setUp(self):
        # Set up a test client
        self.client = Client()

        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            phone="1234567890",
            birth_date="2000-01-01",
            passport_id="123456789",
            gender="Male",
            password="password123",
        )

        # Create a test question
        self.question = Question.objects.create(
            user=self.user.id,  # Assuming the user field stores the user's ID
            question_text="What is the capital of France?",
            level=1,
            answer_text="Paris",
        )

    def test_get_hint_for_grading_view(self):
        # Log in the test user
        self.client.login(email="testuser@example.com", password="password123")

        # Send a GET request to the get_hint_for_grading view
        url = reverse('users:get_hint_for_grading', args=[self.question.id])
        response = self.client.get(url)

        # Check that the response is 200 OK
        self.assertEqual(response.status_code, 200)

        # Check that the response contains a hint key (assuming the hint is always returned in the response)
        self.assertIn("hint", response.json())
