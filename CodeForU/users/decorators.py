# users/decorators.py

from functools import wraps

from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from .models import Mentor, Student


def mentor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            if request.user.is_authenticated and Mentor.objects.get(
                user_ptr_id=request.user.id
            ):

                return view_func(request, *args, **kwargs)
            else:
                return redirect('homepage')
        except:
            return redirect('homepage')

    return _wrapped_view


def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            if request.user.is_authenticated and Student.objects.get(
                user_ptr_id=request.user.id
            ):

                return view_func(request, *args, **kwargs)
            else:
                return redirect('homepage')
        except:
            return redirect('homepage')

    return _wrapped_view
