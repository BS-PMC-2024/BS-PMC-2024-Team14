# forms.py
import os
import re

import django
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import HelpRequest, StudentMentorRequest, User


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )

    def confirm_login_allowed(self, user):
        pass  # Add any custom validation here if needed


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm Password"}
        )
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "birth_date",
            "password",
            "confirm_password",
            "gender",
            "passport_id",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "First Name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Last Name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Email"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Phone"}
            ),
            "birth_date": forms.DateInput(
                attrs={"class": "form-control", "placeholder": "Birth Date"}
            ),
            "gender": forms.Select(
                attrs={"class": "form-control"},
                choices=[("Male", "Male"), ("Female", "Female")],
            ),
            "passport_id": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Passport ID"}
            ),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not re.match("^[A-Za-z]*$", first_name):
            raise forms.ValidationError("First name should only contain alphabets.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not re.match("^[A-Za-z]*$", last_name):
            raise forms.ValidationError("Last name should only contain alphabets.")
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            try:
                if User.objects.filter(email=email).exists():
                    raise forms.ValidationError(
                        "A user with this email already exists."
                    )
            except Exception as e:
                print(f"Exception occurred: {e}")  # Add this line for debugging
                raise forms.ValidationError(
                    "A user with this email already exists."
                )  # Handle exception gracefully
        return email

    def clean_passport_id(self):
        passport_id = self.cleaned_data.get("passport_id")
        print(f"Passport ID to validate: {passport_id}")  # Add this line for debugging

        if passport_id:
            try:
                if User.objects.filter(passport_id=passport_id).exists():
                    raise forms.ValidationError(
                        "A user with this passport ID already exists."
                    )
            except Exception as e:
                print(f"Exception occurred: {e}")  # Add this line for debugging
                raise forms.ValidationError(
                    "A user with this passport ID already exists."
                )  # Handle exception gracefully

        return passport_id

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError(
                "Password must contain at least one uppercase letter."
            )
        if not any(char in "!@#$%^&*" for char in password):
            raise forms.ValidationError(
                "Password must contain at least one special character."
            )
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError(
                "Passwords do not match. Please enter the same password again."
            )

        return confirm_password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match. Please enter again.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class HelpRequestForm(forms.ModelForm):
    class Meta:
        model = HelpRequest
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "style": "width: 100%; padding: 10px;border:1px solid #987D9A;border-radius:10px;",
                    "class": "form-control",
                    "placeholder": "Enter the subject of your request",  # Placeholder for subject
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "style": "width: 100%; height: 200px; padding: 10px;border:1px solid #987D9A;border-radius:10px;",
                    "class": "form-control",
                    "placeholder": "Let us know your thoughts!",  # Placeholder for messag
                }
            ),
        }


class StudentMentorRequestForm(forms.ModelForm):
    class Meta:
        model = StudentMentorRequest
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "style": "width: 100%; padding: 10px;border:1px solid #987D9A;border-radius:10px;",
                    "class": "form-control",
                    "placeholder": "Enter the subject of your request",  # Placeholder for subject

                }
            ),
            "message": forms.Textarea(
                attrs={
                    "style": "width: 100%; height: 200px; padding: 10px;border:1px solid #987D9A;border-radius:10px;",
                    "class": "form-control",
                    "placeholder": "Let us know your thoughts!",  # Placeholder for messag
                }
            ),
        }



class EmailForm(forms.Form):
    email = forms.EmailField()

class CodeVerificationForm(forms.Form):
    code = forms.CharField(max_length=4, required=True)


class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_new_password(self):
        password = self.cleaned_data.get("new_password")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char in "!@#$%^&*" for char in password):
            raise forms.ValidationError("Password must contain at least one special character.")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Oops, Passwords do not match. Please try again.")

        return confirm_password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Oops, Passwords do not match. Please try again.")
        return cleaned_data


    