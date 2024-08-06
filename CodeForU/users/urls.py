from django.contrib import admin
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # path('register/', views.register,name='register'),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("admin_dashboard/", admin.site.urls, name="admin_dashboard"),
    path("mentor_dashboard/", views.mentor_dashboard, name="mentor_dashboard"),
    path("student_dashboard/", views.student_dashboard, name="student_dashboard"),
    path("transition_stu/", views.transition_stu, name="transition_stu"),
    path("transition_men/", views.transition_men, name="transition_men"),
    path("mentor_studentlist/", views.mentor_studentlist, name="mentor_studentlist"),
    path("student_profile/", views.student_profile, name="student_profile"),
    path("mentor_profile/", views.mentor_profile, name="mentor_profile"),
    path("logout/", views.logout_view, name="logout"),
    path("submit-help-request/", views.submit_help_request, name="submit_help_request"),
    path(
        "delete-help-request/<int:request_id>/",
        views.delete_help_request,
        name="delete_help_request",
    ),
    path("questions_list/", views.questions_list, name="questions_list"),
    path('questions/<int:question_id>/answer/', views.answer_question, name='answer_question'),
]
