from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from .models import Mentor, Student


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
        self.mentor_ids = get_mentor_ids()
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
        self.valid_mentor_data = {
            "email": "mentor@example.com",
            "first_name": "Mentor",
            "last_name": "Example",
            "birth_date": "1990-01-01",
            "phone": "0987654321",
            "gender": "Female",
            "passport_id": self.mentor_ids[0],
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
        self.assertEqual(response.status_code, 200)

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
