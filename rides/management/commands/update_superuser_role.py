from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Updates the superuser role to admin'

    def handle(self, *args, **options):
        try:
            superuser = User.objects.get(username='admin')
            superuser.role = 'admin'
            superuser.save()
            self.stdout.write(self.style.SUCCESS('Successfully updated superuser role to admin'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Superuser with username "admin" does not exist')) 