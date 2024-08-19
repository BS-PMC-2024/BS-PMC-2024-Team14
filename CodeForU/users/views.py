import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .decorators import mentor_required, student_required
from .forms import (
    CodeVerificationForm,
    CustomAuthenticationForm,
    EmailForm,
    HelpRequestForm,
    SetNewPasswordForm,
    StudentMentorRequestForm,
    UserRegistrationForm,
)
from .models import HelpRequest, Mentor, Question, Student, StudentMentorRequest, User
import openai
from dotenv import load_dotenv

from openai import OpenAI
load_dotenv()


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
                    mentor = Mentor.objects.get(user_ptr_id=user.id)
                    if not mentor.is_approved:
                        messages.error(request, "Your account is not approved yet.")
                        return redirect("users:login")
                    messages.success(request, "")
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
                # Authentication failed, check if the email exists
                if not User.objects.filter(email=email).exists():
                    messages.error(request, "Oops, Email does not exist.")
                else:
                    messages.error(request, "Oops, wrong password, try again!.")
        else:
            email = form.cleaned_data.get("username")
            curr_user = None
            try:
                curr_user = User.objects.get(email=email)
            except Exception:
                curr_user = None
            if not curr_user:
                messages.error(request, "Oops, Email does not exist.")
            else:
                messages.error(request, "Oops, wrong password, try again!.")
            # messages.error(request,form.errors)
            # print("Form is not valid:", )
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
                    level=1,  # Add additional fields for students here
                    mentor_responsible=res_mentor.id,
                )
                student.set_password(form.cleaned_data["password"])
                student.save()

            # messages.success(request, "Registration successful.")
            return redirect("users:login")
        else:
            print("Registration failed. Please correct the errors below.")
            # messages.error(
            #     request, "Registration failed. Please correct the errors below."
            # )
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


@login_required(login_url="/users/login")
@mentor_required
def mentor_dashboard(request):
    mentor = Mentor.objects.get(user_ptr_id=request.user.id)
    print(f"user id:{request.user.id}")
    print(mentor)
    return render(request, "mentor_dashboard.html", {"mentor": mentor})


@login_required(login_url="/users/login")
@student_required
def student_dashboard(request):
    student = Student.objects.get(user_ptr_id=request.user.id)

    print(f"user id:{request.user.id}")
    print(student)
    return render(request, "student_dashboard.html", {"student": student})


def transition_stu(request):
    return render(request, "transition_stu.html")


def transition_men(request):
    return render(request, "transition_men.html")


@login_required(login_url="/users/login")
def mentor_studentlist(request):
    # Query all students from the database
    students = Student.objects.filter(mentor_responsible=request.user.id)

    # Pass the student list to the template context
    context = {"students": students}

    return render(request, "mentor_studentlist.html", context)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("users:login")
    return redirect("homepage")


@login_required(login_url="/users/login/")
@student_required
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


@student_required
def student_level_up(request):
    user_id = request.user.id
    student = Student.objects.get(id=user_id)
    request_obj = StudentMentorRequest(
        user = user_id,
        mentor_responsible=student.mentor_responsible,
        subject="Ask for level up",
        message="Please can you raise my level?",
        is_resolved=False
    )
    request_obj.save()
    return redirect("users:student_profile")


@login_required(login_url="/users/login/")
@mentor_required
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
def mentor_requests_view(request):
    if request.user.is_mentor:
        requests = StudentMentorRequest.objects.filter(mentor_responsible=request.user.id)
    else:
        requests = StudentMentorRequest.objects.filter(user=request.user.id)
    
    context = {
        'requests': requests
    }
    
    return render(request, 'mentor_requests.html', context)


@mentor_required
def add_response(request, request_id):
    mentor_request = get_object_or_404(StudentMentorRequest, id=request_id, mentor_responsible=request.user.id)

    if request.method == 'POST':
        response = request.POST.get('response')
        if response:
            mentor_request.response = response
            mentor_request.is_resolved = True  # Assuming adding a response resolves the request
            mentor_request.save()
            mentor = request.user.mentor
            student = Student.objects.get(id=mentor_request.user)
            student.add_notification(f"New Response from Mentor {mentor.first_name} {mentor.last_name} On Request ID:{mentor_request.id} ")
            student.save()

    return redirect('users:mentor_requests')


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
    all_questions = Question.objects.all()
    
    # Filter questions where id is equal to original_question_id
    questions = [q for q in all_questions if q.id == q.original_question_id]
    user_level = None
    if request.user.is_student:
        student = Student.objects.get(id=request.user.id)
        user_level = student.level

    return render(
        request,
        "questions_list.html",
        {"questions": questions, "user_level": user_level},
    )


from django.shortcuts import get_object_or_404



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

            mentor = Mentor.objects.get(id=student.mentor_responsible)
            mentor.add_notification(f"New Request from student {student.first_name} {student.last_name}")
            mentor.save()
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


@student_required
def student_feedback(request):
    user = request.user

    if user.is_student:
        student = Student.objects.get(id=user.id)

        if request.method == "POST":
            if "rating" in request.POST:
                # Handle the "Rate Us" form submission
                rating = request.POST.get("rating")
                student.rating = int(rating)
            elif "mentor_rating" in request.POST:
                # Handle the "Rate Your Mentor" form submission
                mentor_rating = request.POST.get("mentor_rating")
                student.mentor_rating = int(mentor_rating)

            student.save()
            return redirect(reverse("users:student_dashboard"))

    return redirect(reverse("users:student_dashboard"))


@student_required
def reset_level_updated(request):
    if request.method == "POST":
        student = request.user.student
        student.level_updated = False
        student.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)


@mentor_required
def level_up_view(request, student_id):
    student = Student.objects.get(id=student_id)
    student.level = student.level + 1
    student.level_updated = True
    student.save()
    return redirect("users:mentor_studentlist")


from django.views import View


# users/views.py
class PasswordResetRequestView(View):
    def get(self, request):
        if "reset_code" in request.session:
            del request.session["reset_code"]
        if "uidb64" in request.session:
            del request.session["uidb64"]
        if "token" in request.session:
            del request.session["token"]
        return render(request, "password_reset_email.html", {"form": EmailForm()})

    def post(self, request):
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            reset_code = str(random.randint(1000, 9999))
            request.session["reset_code"] = reset_code
            request.session["uidb64"] = urlsafe_base64_encode(force_bytes(user.pk))
            request.session["token"] = default_token_generator.make_token(user)
            print(f"Generated reset code: {reset_code}")
            send_mail(
                "Password Reset Code",
                f"Your password reset code is {reset_code}",
                "codeforu14@gmail.com",
                [email],
                fail_silently=False,
            )
            print("Email sent successfully")
            return redirect("users:verify_code")
        except User.DoesNotExist:
            messages.error(request, "Email not found.")
            print("Email not found")
            return render(request, "password_reset_email.html", {"form": EmailForm()})
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            print(f"An error occurred: {str(e)}")
            return render(request, "password_reset_email.html", {"form": EmailForm()})


class CodeVerificationView(View):
    def get(self, request):
        return render(
            request, "password_reset_code.html", {"form": CodeVerificationForm()}
        )

    def post(self, request):
        code = request.POST.get("code")
        if code == request.session.get("reset_code"):
            return redirect("users:set_new_password")
        else:
            messages.error(request, "Invalid verification code.")
            return render(
                request, "password_reset_code.html", {"form": CodeVerificationForm()}
            )


class SetNewPasswordView(View):
    def get(self, request):
        return render(request, "set_new_password.html", {"form": SetNewPasswordForm()})

    def post(self, request):
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            uidb64 = request.session.get("uidb64")
            token = request.session.get("token")
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                user.set_password(form.cleaned_data["new_password"])
                user.save()
                # messages.success(request, 'Your password has been reset successfully.')
                list(messages.get_messages(request))
                return redirect("users:login")
        # messages.error(request, 'Failed to reset password. Please try again.')
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, error)
        return render(request, "set_new_password.html", {"form": form})


@login_required(login_url="/users/login/")
def get_hint(request, question_id):
    # Fetch the question text using the question_id
    question = get_object_or_404(Question, id=question_id)

    # Set up OpenAI API key and create a client
    client = OpenAI()

    try:
        # Send the question to OpenAI and ask for a hint
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides hints, not complete answers, and make them two rows long to four not more"},
                {"role": "user", "content": f"Please provide a hint for this question: {question.question_text}"}
            ]
        )

        # Access the hint from the response
        hint_message = response.choices[0].message.content
        return JsonResponse({"hint": hint_message})

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {e}"})
    
@login_required(login_url="/users/login/")
def answer_question(request, question_id):
    # Fetch the original question using the ID provided in the URL
    original_question = get_object_or_404(Question, id=question_id)
    print("question id is : ")
    print(question_id)
    
    # Check if the student already has a copy of the question
    question = Question.objects.filter(
        answered_by=request.user.id,
        original_question_id=original_question.id
    ).first()
    if not question:
        # Create a copy of the question for the student with the original question ID
            question = Question.objects.create(
                user=request.user.student.mentor_responsible,
                answered_by=request.user.id,
                original_question_id=original_question.id,
                question_text=original_question.question_text,
                level=original_question.level
            )

    
    if request.method == 'POST':
      

        
        code_answer = request.POST.get('code_answer')
        print("im in the post method ")
        # Save the answer to the copied question
        question.answered_by = request.user.id
        question.answer_text = code_answer
        question.graded = False  # Reset grading status on resubmission
        question.grade = None
        question.notes = ""
        question.save()

        # Optionally notify the mentor
        student = request.user.student
        mentor = Mentor.objects.get(id=student.mentor_responsible)
        mentor.add_notification(f"New submission from {student.first_name} {student.last_name}")
        mentor.save()
      
        # Implement notification or email if needed

        return redirect(reverse('users:questions_list'))

    return render(request, 'answer_question.html', {'question': question})

@login_required(login_url="/users/login/")
@student_required
def student_submissions(request):
    student = request.user.student
    questions = Question.objects.filter(answered_by=student.id, answered_by__isnull=False)

    return render(request, 'student_submissions.html', {'questions': questions})


@login_required(login_url="/users/login/")
@mentor_required
def mentor_submissions(request):
    mentor = request.user.mentor
    # Get all students assigned to this mentor
    students = Student.objects.filter(mentor_responsible=mentor.id)
    

    # Manually filter questions related to those students
    questions = []
    for student in students:
        student_questions = Question.objects.filter(answered_by=student.id, answered_by__isnull=False)
        questions.extend(student_questions)

    print("hello")

    return render(request, 'mentor_submissions.html', {'questions': questions})

@login_required(login_url="/users/login/")
@mentor_required
def grade_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    print("im in the grade view")
    if request.method == 'POST':
        grade = request.POST.get('grade')
        notes = request.POST.get('notes')
         # Convert the grade to an integer
        try:
            grade = int(grade)
        except ValueError:
            grade = 0  # Set a default value or handle the error as needed
        
        # Ensure grade is within the allowed range
        if grade > 100:
            grade = 100
        elif grade < 0:
            grade = 0
        question.grade = grade
        question.notes = notes
        question.graded = True
        question.save()

        # Optionally, notify the student about the grading
        # student = User.objects.get(id=question.answered_by)
        # Send notification or email
        student = User.objects.get(id=question.answered_by)
        student.add_notification("Your submission has been graded")
        
        
        
        return redirect('users:mentor_submissions')

    return render(request, 'grade_question.html', {'question': question})

@login_required(login_url="/users/login/")
def clear_notifications(request):
    user = request.user
    user.notifications = 0
    user.notification_message = ""
    user.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def get_hint_for_grading(request, question_id):
    try:
        question = Question.objects.get(id=question_id)
        client = OpenAI()

        # Generate a prompt to assist in grading
        prompt = f"Given the question: '{question.question_text}' and the student's answer: '{question.answer_text}', suggest feedback or help the mentor grade the answer."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a grading assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        hint = response.choices[0].message.content
        return JsonResponse({'hint': hint})
    except Question.DoesNotExist:
        return JsonResponse({'error': 'Question not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
