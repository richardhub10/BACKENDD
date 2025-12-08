import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Force-set the Django superuser password from environment variables."

    def handle(self, *args, **options):
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not (username and password):
            self.stdout.write(self.style.WARNING("DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set; skipping."))
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email or ''
        })
        user.is_staff = True
        user.is_superuser = True
        if email:
            user.email = email
        user.set_password(password)
        user.save()
        if created:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' created and password set."))
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' password reset and flags ensured."))
