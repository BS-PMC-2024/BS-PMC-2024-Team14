from django.contrib import admin

from .models import HelpRequest, Mentor, Student, User

admin.site.register(User)
admin.site.register(Student)
admin.site.register(Mentor)
admin.site.register(HelpRequest)

