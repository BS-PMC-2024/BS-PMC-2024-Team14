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
    path("submit_help_request/", views.submit_help_request, name="submit_help_request"),
    path(
        "delete-help-request/<int:request_id>/",
        views.delete_help_request,
        name="delete_help_request",
    ),
    path("questions_list/", views.questions_list, name="questions_list"),
    path(
        "questions/<int:question_id>/answer/",
        views.answer_question,
        name="answer_question",
    ),
    path(
        "student_mentor_request/",
        views.student_mentor_request,
        name="student_mentor_request",
    ),
    path(
        "delete_student_mentor_request/<int:request_id>/",
        views.delete_student_mentor_request,
        name="delete_student_mentor_request",
    ),
    path("student_feedback/",views.student_feedback,name="student_feedback"),
    path('reset_level_updated/', views.reset_level_updated, name='reset_level_updated'),
    path('level_up/<int:student_id>/', views.level_up_view, name='level_up'),
    path('password_reset/', views.PasswordResetRequestView.as_view(), name='password_reset'),
    path('password_reset/verify/', views.CodeVerificationView.as_view(), name='verify_code'),
    path('password_reset/set_new_password/', views.SetNewPasswordView.as_view(), name='set_new_password'),
    path('questions/<int:question_id>/hint/', views.get_hint, name='get_hint'),
    path('student_submissions/', views.student_submissions, name='student_submissions'),
    path('mentor_submissions/', views.mentor_submissions, name='mentor_submissions'),
    path("questions/<int:question_id>/grade/", views.grade_question, name="grade_question"),
    path('clear_notifications/', views.clear_notifications, name='clear_notifications'),
    path('questions/<int:question_id>/hint-for-grading/', views.get_hint_for_grading, name='get_hint_for_grading'),
    path("student_level_up/", views.student_level_up, name="student_level_up"),


]