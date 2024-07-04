from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomAuthenticationForm
from .models import Mentor,Student


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
    return render(request, 'register.html')

@login_required
def mentor_dashboard(request):
    return render(request, 'mentor_dashboard.html')


@login_required
def student_dashboard(request):
    return render(request, 'student_dashboard.html')