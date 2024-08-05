# chat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_page, name='chat_page'),
    path('test-openai/', views.test_openai_api),
   
    
]
