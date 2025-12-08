from django.apps import AppConfig
import os
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError
from django.db.models.signals import post_migrate


class ItemsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'items'

    def ready(self):
        # Register a post_migrate hook to create/reset the superuser AFTER DB is ready,
        # which avoids Django's warning about querying during app initialization.
        def ensure_superuser(sender, **kwargs):
            username = os.getenv('DJANGO_SUPERUSER_USERNAME') or 'admin'
            email = os.getenv('DJANGO_SUPERUSER_EMAIL') or 'admin@example.com'
            password = os.getenv('DJANGO_SUPERUSER_PASSWORD') or 'admin'
            try:
                User = get_user_model()
                user = User.objects.filter(username=username).first()
                if user is None:
                    User.objects.create_superuser(username=username, email=email, password=password)
                    print(f"[startup] Superuser '{username}' created.")
                else:
                    user.set_password(password)
                    user.email = email or user.email
                    user.is_superuser = True
                    user.is_staff = True
                    user.save()
                    print(f"[startup] Superuser '{username}' password reset and flags ensured.")
            except OperationalError:
                # If migrations are still running for auth, silently ignore.
                pass

        post_migrate.connect(ensure_superuser, sender=self)
