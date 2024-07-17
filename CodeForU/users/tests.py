from django.test import TestCase, Client
from django.urls import reverse
from .models import Mentor, Student

def get_mentor_ids():
    return [
        '1234567890',
        '2345678901',
        '3456789012',
        '4567890123',
        '5678901234',
        '6789012345',
        '7890123456',
        '8901234567',
        '9012345678',
        '0123456789',
    ]


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('users:register')
        self.mentor_ids = get_mentor_ids()
        self.valid_student_data = {
            'email': 'student@example.com',
            'first_name': 'Student',
            'last_name': 'Example',
            'birth_date': '2000-01-01',
            'phone': '1234567890',
            'gender': 'Male',
            'passport_id': '1122334455',
            'password': 'Testpassword1!',
            'confirm_password': 'Testpassword1!',
        }
        self.valid_mentor_data = {
            'email': 'mentor@example.com',
            'first_name': 'Mentor',
            'last_name': 'Example',
            'birth_date': '1990-01-01',
            'phone': '0987654321',
            'gender': 'Female',
            'passport_id': self.mentor_ids[0],
            'password': 'Testpassword1!',
            'confirm_password': 'Testpassword1!',
        }

    def test_register_student_success(self):
        response = self.client.post(self.register_url, self.valid_student_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:login'))
        student = Student.objects.get(email=self.valid_student_data['email'])
        self.assertTrue(student.check_password(self.valid_student_data['password']))
        self.assertEqual(student.first_name, self.valid_student_data['first_name'])
        self.assertEqual(student.last_name, self.valid_student_data['last_name'])

    def test_register_password_mismatch(self):
        invalid_data = self.valid_student_data.copy()
        invalid_data['confirm_password'] = 'differentpassword'
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)

    def test_register_missing_fields(self):
        invalid_data = self.valid_student_data.copy()
        invalid_data.pop('email')
        response = self.client.post(self.register_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")


from django.contrib.auth import get_user_model

class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            phone='1234567890',
            birth_date='2000-01-01',
            passport_id='A123456789',
            gender='Male',
            password='password'
        )

    def test_logout_view(self):
        self.client.login(email='testuser@example.com', password='password')

        response = self.client.get(reverse('users:mentor_dashboard'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('users:logout'))
        self.assertEqual(response.status_code, 302) 

        response = self.client.get(reverse('users:mentor_dashboard'))
        self.assertNotEqual(response.status_code, 200)  
 