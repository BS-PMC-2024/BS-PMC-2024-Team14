import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CodeForU.settings')
django.setup()

# Import the necessary models
from users.models import Mentor, Student

# Creating a Mentor
mentor = Mentor.objects.create_user(
    email="mentor@example.com",
    first_name="John",
    last_name="Doe",
    phone="1234567890",
    birth_date="1980-01-01",
    password="securepassword"
)

# Adding the additional fields for Mentor
mentor.additional_field_mentor = "Expert in Python"
mentor.save()

print(f"Mentor created: {mentor}")

# Creating a Student
student = Student.objects.create_user(
    email="student@example.com",
    first_name="Jane",
    last_name="Smith",
    phone="0987654321",
    birth_date="2000-05-15",
    password="securepassword"
)

# Adding the additional fields for Student
student.additional_field_student = "Learning Django"
student.save()

print(f"Student created: {student}")
