# users/decorators.py

from functools import wraps

from django.http import HttpResponseForbidden

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
                return HttpResponseForbidden(
                    "You do not have permission to access this page!!."
                )
        except:
            return HttpResponseForbidden(
                "You do not have permission to access this page."
            )

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
                return HttpResponseForbidden(
                    "You do not have permission to access this page!!."
                )
        except:
            return HttpResponseForbidden(
                "You do not have permission to access this page."
            )

    return _wrapped_view
