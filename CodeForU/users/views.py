from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm
from .models import Mentor,Student
from .forms import UserRegistrationForm

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
        # Add more fake IDs as needed
    ]


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                print(f"User {user.email} authenticated successfully")
                if user.is_superuser:
                    return redirect('admin:index')  # Ensure the admin URL is correct
                
                # Check if the user is a mentor
                try:
                    Mentor.objects.get(user_ptr_id=user.id)
                    return redirect('users:mentor_dashboard')
                except Mentor.DoesNotExist:
                    pass
                
                # Check if the user is a student
                try:
                    Student.objects.get(user_ptr_id=user.id)
                    return redirect('users:student_dashboard')
                except Student.DoesNotExist:
                    pass

                #return redirect('users:student_dashboard')
                
                # If user is neither a mentor nor a student
                messages.error(request, 'Invalid role')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            print('Form is not valid:', form.errors)
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})

def register_view(request):
    mentor_ids = get_mentor_ids()  # Assuming you have a function to get mentor IDs

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            '''
            if user.passport_id in mentor_ids:  # Check if passport ID is in the list of mentor IDs
                mentor = Mentor.objects.create(
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    birth_date=user.birth_date,
                    phone=user.phone,
                    gender=user.gender,
                    passport_id=user.passport_id,
                    additional_field_mentor='Additional Mentor Field Value'  # Add additional fields for mentors here
                )
                mentor.set_password(form.cleaned_data['password'])
                mentor.save()
            else:
            '''
            student = Student.objects.create(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                birth_date=user.birth_date,
                phone=user.phone,
                gender=user.gender,
                passport_id=user.passport_id,
                level=0  # Add additional fields for students here
            )
            student.set_password(form.cleaned_data['password'])
            student.save()

            messages.success(request, "Registration successful.")
            return redirect('users:login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def mentor_dashboard(request):
    return render(request, 'mentor_dashboard.html')


@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')