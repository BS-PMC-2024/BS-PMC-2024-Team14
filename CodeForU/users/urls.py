from django.contrib import admin
from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    # path('register/', views.register,name='register'),
    path('login/', views.login_view,name='login'),
    path('register/', views.register_view,name='register'),
    path('admin_dashboard/', admin.site.urls, name='admin_dashboard'),
    path('mentor_dashboard/', views.mentor_dashboard, name='mentor_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('logout/', views.logout_view,name='logout'),
   
]