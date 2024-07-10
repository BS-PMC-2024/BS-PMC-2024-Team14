from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, birth_date, password=None):
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Please provide a valid phone number")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, phone, birth_date, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            password=password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    first_name = models.CharField(max_length=30, verbose_name="First Name")
    last_name = models.CharField(max_length=30, verbose_name="Last Name")
    birth_date = models.DateField(verbose_name="Birth Date")
    email = models.EmailField(unique=True, verbose_name="Email Address", db_index=True)  # Index added
    phone = models.CharField(verbose_name="Phone", max_length=10)
    app_rating = models.IntegerField(blank=True, null=True, default=0, verbose_name="App Rating")
    level = models.IntegerField(verbose_name="Student Level", blank=True, null=True, default=0)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'phone']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def has_perm(self, perm, obj=None):
        return True

    def is_mentor(self):
        try:
            is_mentor = Mentor.objects.filter(user_ptr_id=self.id).exists()
            print(f"Checking if user {self.email} is a mentor: {is_mentor}")
            return is_mentor
        except Exception as e:
            print(f"Error checking if user {self.email} is a mentor: {e}")
            return False

    def is_student(self):
        try:
            is_student = Student.objects.filter(user_ptr_id=self.id).exists()
            print(f"Checking if user {self.email} is a student: {is_student}")
            return is_student
        except Exception as e:
            print(f"Error checking if user {self.email} is a student: {e}")
            return False

class Student(User):
    additional_field_student = models.CharField(max_length=100, verbose_name="Additional Field for Student")

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

class Mentor(User):
    additional_field_mentor = models.CharField(max_length=100, verbose_name="Additional Field for Mentor")

    class Meta:
        verbose_name = 'Mentor'
        verbose_name_plural = 'Mentors'
