from django.contrib import admin
from .models import User, Student, Mentor, Question

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Mentor)
admin.site.register(Question)
