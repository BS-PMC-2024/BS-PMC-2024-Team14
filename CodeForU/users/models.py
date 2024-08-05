from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from ChatBot.models import Question 

class UserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, phone, birth_date,passport_id,gender, password=None):
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Please provide a valid phone number")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            passport_id = passport_id,
            gender = gender,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, first_name, last_name, phone, birth_date,passport_id,gender, password=None):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            password=password,
            passport_id = passport_id,
            gender = gender,

        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    passport_id = models.CharField(max_length=10,unique=True, blank=False,verbose_name="Passport ID")
    first_name = models.CharField(max_length=30, verbose_name="First Name")
    last_name = models.CharField(max_length=30, verbose_name="Last Name")
    birth_date = models.DateField(verbose_name="Birth Date")
    email = models.EmailField(unique=True, verbose_name="Email Address", db_index=True)  # Index added
    phone = models.CharField(verbose_name="Phone", max_length=10)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    gender = models.CharField(max_length=10, verbose_name="Gender", choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')
    saved_questions = models.ManyToManyField(Question, related_name='saved_by', blank=True)  # Reference the Question model


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'birth_date', 'phone','gender','passport_id']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def has_perm(self, perm, obj=None):
        return True

    # def is_mentor(self):
    #     try:
    #         is_mentor = Mentor.objects.filter(user_ptr_id=self.id).exists()
    #         print(f"Checking if user {self.email} is a mentor: {is_mentor}")
    #         return is_mentor
    #     except Exception as e:
    #         print(f"Error checking if user {self.email} is a mentor: {e}")
    #         return False

    # def is_student(self):
    #     try:
    #         is_student = Student.objects.filter(user_ptr_id=self.id).exists()
    #         print(f"Checking if user {self.email} is a student: {is_student}")
    #         return is_student
    #     except Exception as e:
    #         print(f"Error checking if user {self.email} is a student: {e}")
    #         return False
    def is_mentor(self):
        return Mentor.objects.filter(id=self.id).exists()

    def is_student(self):
        return Student.objects.filter(id=self.id).exists()

class Student(User):
    level = models.IntegerField(verbose_name="Student Level", blank=True, null=True, default=0)
    
    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'

class Mentor(User):
    is_approved = models.BooleanField(default=False)
    class Meta:
        verbose_name = 'Mentor'
        verbose_name_plural = 'Mentors'
