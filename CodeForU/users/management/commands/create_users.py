# users/management/commands/create_users.py
from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = 'Update existing users to ensure compatibility with new model fields'

    def handle(self, *args, **kwargs):
        for user in User.objects.all():
            if not hasattr(user, 'saved_questions'):
                user.saved_questions.set([])
                user.save()
        self.stdout.write(self.style.SUCCESS('Successfully updated existing users'))
