import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .decorators import mentor_required, student_required
from .forms import (
    CustomAuthenticationForm,
    HelpRequestForm,
    StudentMentorRequestForm,
    UserRegistrationForm,
)
from .models import HelpRequest, Mentor, Question, Student, StudentMentorRequest


def get_mentor_ids():
    return [
        "1234567890",
        "2345678901",
        "3456789012",
        "4567890123",
        "5678901234",
        "6789012345",
        "7890123456",
        "8901234567",
        "9012345678",
        "0123456789",
        # Add more fake IDs as needed
    ]


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
                    return redirect("users:transition_men")
                except Mentor.DoesNotExist:
                    pass

                # Check if the user is a student
                try:
                    Student.objects.get(user_ptr_id=user.id)
                    return redirect("users:transition_stu")
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
    mentor_ids = get_mentor_ids()  # Assuming you have a function to get mentor IDs

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])

            if (
                user.passport_id in mentor_ids
            ):  # Check if passport ID is in the list of mentor IDs
                mentor = Mentor.objects.create(
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    birth_date=user.birth_date,
                    phone=user.phone,
                    gender=user.gender,
                    passport_id=user.passport_id,
                )
                mentor.set_password(form.cleaned_data["password"])
                mentor.save()
            else:
                all_mentors = Mentor.objects.all()
                random_index = random.randint(0, len(all_mentors) - 1)
                res_mentor = all_mentors[random_index]
                print(f"your responsible mentor is {res_mentor}")
                student = Student.objects.create(
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    birth_date=user.birth_date,
                    phone=user.phone,
                    gender=user.gender,
                    passport_id=user.passport_id,
                    level=0,  # Add additional fields for students here
                    mentor_responsible=res_mentor.id,
                )
                student.set_password(form.cleaned_data["password"])
                student.save()

            messages.success(request, "Registration successful.")
            return redirect("users:login")
        else:
            messages.error(
                request, "Registration failed. Please correct the errors below."
            )
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


@login_required(login_url="/users/login")
def mentor_dashboard(request):
    return render(request, "mentor_dashboard.html")


@login_required(login_url="/users/login")
def student_dashboard(request):
    return render(request, "student_dashboard.html")


def transition_stu(request):
    return render(request, "transition_stu.html")


def transition_men(request):
    return render(request, "transition_men.html")


@login_required(login_url="/users/login")
def mentor_studentlist(request):
    # Query all students from the database
    students = Student.objects.all()

    # Pass the student list to the template context
    context = {"students": students}

    return render(request, "mentor_studentlist.html", context)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("users:login")
    return redirect("homepage")


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


@login_required(login_url="/users/login/")
def mentor_profile(request):
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
                mentor = Mentor.objects.get(id=user_id)
                mentor.first_name = first_name
                mentor.last_name = last_name
                mentor.phone = phone
                mentor.email = email
                mentor.save()
                print("Updated successfully")
                return redirect(
                    reverse("users:mentor_profile")
                )  # Redirect to a success page or render a success message
            except Mentor.DoesNotExist:
                return HttpResponse("User not found", status=404)

        else:
            # Handle the delete action
            try:
                mentor = Mentor.objects.get(id=user_id)
                mentor.delete()
                print(f"{mentor.email} got Deleted successfully")
                return redirect(
                    reverse("users:login")
                )  # Redirect to a success page or render a success message
            except Mentor.DoesNotExist:
                return HttpResponse("User not found", status=404)
    else:
        if not request.user.is_authenticated:
            print("User is not authenticated, redirecting to login")
        else:
            try:
                men = Mentor.objects.get(email=request.user.email)
                print(
                    f"User {request.user.email} is authenticated, accessing mentor_dashboard"
                )
                return render(request, "mentor_profile.html", {"mentor": men})
            except Mentor.DoesNotExist:
                print("Something went wrong with getting data from mongo")

    return redirect(reverse("users:mentor_dashboard"))


@mentor_required
def submit_help_request(request):
    help_requests = None
    if request.method == "POST":
        form = HelpRequestForm(request.POST)
        if form.is_valid():
            mentor_id = request.user.id
            help_request = form.save(commit=False)
            help_request.user = mentor_id
            help_request.save()
            return redirect(reverse("users:submit_help_request"))
    else:
        mentor_id = request.user.id
        help_requests = HelpRequest.objects.filter(user=mentor_id)
        form = HelpRequestForm()
    return render(
        request, "submit_help_request.html", {"form": form, "requests": help_requests}
    )


@mentor_required
def delete_help_request(request, request_id):
    # print("dasdasfasd")
    help_request = HelpRequest.objects.get(id=request_id)
    print(help_request)
    if request.method == "POST":
        help_request.delete()
        return redirect(reverse("users:submit_help_request"))
    return render(request, "submit_help_request.html")


@login_required(login_url="/users/login/")
def questions_list(request):
    questions = Question.objects.all()
    user_level = None
    if request.user.is_student:
        student = Student.objects.get(id=request.user.id)
        user_level = student.level
        print("user level: \n")
        print(user_level)
        print("\n")
        print("user itself: \n")
        print(request.user)

    return render(
        request,
        "questions_list.html",
        {"questions": questions, "user_level": user_level},
    )


from django.shortcuts import get_object_or_404


@login_required(login_url="/users/login/")
def answer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, "answer_question.html", {"question": question})


@student_required
def student_mentor_request(request):
    st_m_request = None
    if request.method == "POST":
        form = StudentMentorRequestForm(request.POST)
        if form.is_valid():
            student = Student.objects.get(id=request.user.id)
            st_m_request = form.save(commit=False)
            st_m_request.user = student.id
            st_m_request.mentor_responsible = student.mentor_responsible
            st_m_request.save()
            return redirect(reverse("users:student_mentor_request"))
    else:
        student_id = request.user.id
        st_m_requests = StudentMentorRequest.objects.filter(user=student_id)

        form = StudentMentorRequestForm()
    return render(
        request,
        "student_mentor_request.html",
        {"form": form, "requests": st_m_requests},
    )


@student_required
def delete_student_mentor_request(request, request_id):
    st_m_request = StudentMentorRequest.objects.get(id=request_id)
    print(st_m_request)
    if request.method == "POST":
        st_m_request.delete()
        return redirect(reverse("users:student_mentor_request"))
    return render(request, "student_mentor_request.html")
