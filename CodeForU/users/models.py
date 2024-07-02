from django.db import models
from django.contrib.auth.models import AbstractUser ,BaseUserManager

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self,email,first_name,last_name,phone,birth_date,password = None):
        if not email:
            raise ValueError("Email is Required")
        if not phone:
            raise ValueError("Please provide a valid phone number")
        user=self.model(
            email = self.normalize_email(email),
            first_name =first_name,
            last_name = last_name,
            phone = phone,
            birth_date = birth_date
        )
        user.set_password(password)
        user.save(using = self._db)
        return user
    
    def create_superuser(self,email,first_name,last_name,phone,birth_date,password = None):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name =last_name,
            phone=phone,
            birth_date=birth_date,
            password = password
        )
        user.is_admin = True
        user.is_superuser = True
        user.is_staff = True
        user.save(using = self._db)
        return user

class User(AbstractUser):
    first_name = models.CharField(max_length=30 ,verbose_name="First Name")
    last_name = models.CharField(max_length=30 ,verbose_name="Last Name")
    birth_date = models.DateField(auto_now=True , verbose_name="Birth Date")
    email = models.EmailField(unique=True , verbose_name="Email Address")
    phone = models.CharField(verbose_name="Phone",max_length=10)
    app_rating = models.IntegerField(blank=True, null=True, default=0,verbose_name="App Rating")
    level = models.IntegerField(verbose_name="Student Level", blank=True, null=True, default=0)
    is_mentor = models.BooleanField(default=False,verbose_name= "Is Mentor")
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name','last_name','birth_date','phone']

    objects = UserManager()

    def __str__(self):
        return self.first_name + " " + self.last_name
    
    def has_perm(self,perm,obj=None):
        return True