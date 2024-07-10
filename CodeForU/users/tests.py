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
            password="securepassword"
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
            password="securepassword"
        )
        student.additional_field_student = "Learning Django"
        student.save()
        
        self.assertEqual(student.email, "student@example.com")
        self.assertEqual(student.first_name, "Jane")
        self.assertEqual(student.last_name, "Smith")
        self.assertEqual(student.phone, "0987654321")
        self.assertEqual(student.additional_field_student, "Learning Django")
        self.assertTrue(student.check_password("securepassword"))
