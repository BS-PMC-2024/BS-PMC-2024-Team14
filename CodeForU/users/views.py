from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import CustomAuthenticationForm
from .models import Mentor, Student


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                print(f"User {user.email} authenticated successfully")
                if user.is_superuser:
                    return redirect("admin:index")  # Ensure the admin URL is correct

                # Check if the user is a mentor
                try:
                    Mentor.objects.get(user_ptr_id=user.id)
                    return redirect("users:mentor_dashboard")
                except Mentor.DoesNotExist:
                    pass

                # Check if the user is a student
                try:
                    Student.objects.get(user_ptr_id=user.id)
                    return redirect("users:student_dashboard")
                except Student.DoesNotExist:
                    pass

                # If user is neither a mentor nor a student
                messages.error(request, "Invalid role")
            else:
                messages.error(request, "Invalid email or password")
        else:
            print("Form is not valid:", form.errors)
    else:
        form = CustomAuthenticationForm()

    return render(request, "login.html", {"form": form})


def register_view(request):
    return render(request, "register.html")


@login_required(login_url="/users/login/")
def mentor_dashboard(request):
    return render(request, "mentor_dashboard.html")


@login_required(login_url="/users/login/")
def student_dashboard(request):
    return render(request, "student_dashboard.html")


@login_required(login_url="/users/login/")
def student_profile(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")

        if action == "submit":
            # Handle the update action
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            phone = request.POST.get("phone")
            email = request.POST.get("email")

            try:
                student = Student.objects.get(id=user_id)
                student.first_name = first_name
                student.last_name = last_name
                student.phone = phone
                student.email = email
                student.save()
                print("Updated successfully")
                return redirect(
                    reverse("users:student_profile")
                )  # Redirect to a success page or render a success message
            except Student.DoesNotExist:
                return HttpResponse("User not found", status=404)

        else:
            # Handle the delete action
            try:
                student = Student.objects.get(id=user_id)
                student.delete()
                print(f"{student.email} got Deleted successfully")
                return redirect(
                    reverse("users:login")
                )  # Redirect to a success page or render a success message
            except Student.DoesNotExist:
                return HttpResponse("User not found", status=404)
    else:
        if not request.user.is_authenticated:
            print("User is not authenticated, redirecting to login")
        else:
            try:
                st = Student.objects.get(email=request.user.email)
                print(
                    f"User {request.user.email} is authenticated, accessing mentor_dashboard"
                )
                return render(request, "student_profile.html", {"student": st})
            except Student.DoesNotExist:
                print("Something went wrong with getting data from mongo")

    return redirect(reverse("users:student_dashboard"))
