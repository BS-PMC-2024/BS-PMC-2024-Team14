from ChatBot.models import Question
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        first_name,
        last_name,
        phone,
        birth_date,
        passport_id,
        gender,
        password=None,
    ):
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
            passport_id=passport_id,
            gender=gender,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        first_name,
        last_name,
        phone,
        birth_date,
        passport_id,
        gender,
        password=None,
    ):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            birth_date=birth_date,
            password=password,
            passport_id=passport_id,
            gender=gender,
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    passport_id = models.CharField(
        max_length=10, unique=True, blank=False, verbose_name="Passport ID"
    )
    first_name = models.CharField(max_length=30, verbose_name="First Name")
    last_name = models.CharField(max_length=30, verbose_name="Last Name")
    birth_date = models.DateField(verbose_name="Birth Date")
    email = models.EmailField(
        unique=True, verbose_name="Email Address", db_index=True
    )  # Index added
    phone = models.CharField(verbose_name="Phone", max_length=10)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10,
        verbose_name="Gender",
        choices=[("Male", "Male"), ("Female", "Female")],
        default="Male",
    )
    saved_questions = models.ManyToManyField(
        Question, related_name="saved_by", blank=True
    )  # Reference the Question model

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "birth_date",
        "phone",
        "gender",
        "passport_id",
    ]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name + " " + self.last_name

    def has_perm(self, perm, obj=None):
        return True

    @property
    def is_mentor(self):
        try:
            mentor = Mentor.objects.get(user_ptr_id=self.id)
            print(f"Checking if user {self.email} is a mentor: {mentor}")
            return True if mentor else False
        except Exception as e:
            print(f"Error checking if user {self.email} is a mentor: {e}")
            return False

    @property
    def is_student(self):
        try:
            student = Student.objects.get(user_ptr_id=self.id)
            print(f"Checking if user {self.email} is a student: {student}")
            return True if student else False
        except Exception as e:
            print(f"Error checking if user {self.email} is a student: {e}")
            return False


class Student(User):
    level = models.IntegerField(
        verbose_name="Student Level", blank=True, null=True, default=0
    )
    mentor_responsible = models.IntegerField(blank=True, null=True)
    rating = models.IntegerField(blank=True,null=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Mentor(User):
    is_approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Mentor"
        verbose_name_plural = "Mentors"


from django.utils import timezone


class HelpRequest(models.Model):
    user = models.IntegerField(blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        mentor = Mentor.objects.get(id=self.user)
        return f"Request from - {mentor.email} {self.subject}"

    def save(self, *args, **kwargs):
        # Set responded_at if the request is marked as resolved
        if self.is_resolved and not self.responded_at:
            self.responded_at = timezone.now()
        super().save(*args, **kwargs)

    def clean(self):
        # Ensure a response is provided if the request is marked as resolved
        if self.is_resolved and not self.response:
            raise Exception(
                "A response must be provided if the request is marked as resolved."
            )

    def delete(self, *args, **kwargs):
        # Custom delete logic if needed (currently just calls the superclass)
        super().delete(*args, **kwargs)


class StudentMentorRequest(models.Model):
    user = models.IntegerField(blank=True, null=True)
    mentor_responsible = models.IntegerField(blank=True, null=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    response = models.TextField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        student = Student.objects.get(id=self.user)
        mentor = Mentor.objects.get(id=self.mentor_responsible)
        return f"Request from {student.email} to {mentor.email} - {self.subject}"

    def save(self, *args, **kwargs):
        # Set responded_at if the request is marked as resolved
        if self.is_resolved and not self.responded_at:
            self.responded_at = timezone.now()
        super().save(*args, **kwargs)

    def clean(self):
        # Ensure a response is provided if the request is marked as resolved
        if self.is_resolved and not self.response:
            raise Exception(
                "A response must be provided if the request is marked as resolved."
            )

    def delete(self, *args, **kwargs):
        # Custom delete logic if needed (currently just calls the superclass)
        super().delete(*args, **kwargs)
