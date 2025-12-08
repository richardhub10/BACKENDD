from django.apps import AppConfig
import os
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError


class ItemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'items'

    def ready(self):
        # Auto-create a superuser from environment variables if not present.
        # This runs at startup and is safe on Render. It ignores errors while DB is migrating.
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not (username and email and password):
            return

        try:
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password)
        except OperationalError:
            # Database not ready (e.g., during migrate); ignore.
            pass
