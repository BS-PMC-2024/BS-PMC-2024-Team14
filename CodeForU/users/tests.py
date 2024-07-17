from django.test import TestCase

from users.models import Mentor, Student


class UserModelTests(TestCase):

    def test_create_mentor(self):
        mentor = Mentor.objects.create_user(
            email="mentor@example.com",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            birth_date="1980-01-01",
            password="securepassword",
        )
        mentor.additional_field_mentor = "Expert in Python"
        mentor.save()

        self.assertEqual(mentor.email, "mentor@example.com")
        self.assertEqual(mentor.first_name, "John")
        self.assertEqual(mentor.last_name, "Doe")
        self.assertEqual(mentor.phone, "1234567890")
        self.assertEqual(mentor.additional_field_mentor, "Expert in Python")
        self.assertTrue(mentor.check_password("securepassword"))

    def test_create_student(self):
        student = Student.objects.create_user(
            email="student@example.com",
            first_name="Jane",
            last_name="Smith",
            phone="0987654321",
            birth_date="2000-05-15",
            password="securepassword",
        )
        student.additional_field_student = "Learning Django"
        student.save()

        self.assertEqual(student.email, "student@example.com")
        self.assertEqual(student.first_name, "Jane")
        self.assertEqual(student.last_name, "Smith")
        self.assertEqual(student.phone, "0987654321")
        self.assertEqual(student.additional_field_student, "Learning Django")
        self.assertTrue(student.check_password("securepassword"))


# class StudentProfileViewTests(TestCase):

#     def setUp(self):
#         # Create a test user and student object
#         self.user = Student.objects.create_user(
#             email="student@example.com",
#             first_name="Jane",
#             last_name="Smith",
#             phone="0987654321",
#             birth_date="2000-05-15",
#             password="securepassword",
#         )

#     def test_update_student_profile(self):
#         # Simulate a POST request to update the student profile
#         updated_data = {
#             "user_id": self.user.id,
#             "action": "submit",
#             "first_name": "Updated",
#             "last_name": "User",
#             "phone": "987654321",
#             "email": "updated@example.com",
#         }
#         url = reverse("users:student_profile")
#         response = self.client.post(url, updated_data)

#         # Check that the response redirects to the student dashboard upon successful update
#         self.assertRedirects(response, reverse("users:student_dashboard"))

#         # Check that the student object has been updated in the database
#         updated_student = Student.objects.get(id=self.user.id)
#         self.assertEqual(updated_student.first_name, "Updated")
#         self.assertEqual(updated_student.phone, "987654321")
#         self.assertEqual(updated_student.email, "updated@example.com")

#     def tearDown(self):
#         # Clean up by deleting the test user and student objects
#         self.user.delete()
