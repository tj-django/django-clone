import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        email, password = self._get_credentials()
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                username=email,
                email=email,
                first_name="admin",
                last_name="admin",
                password=password,
            )
            self.stdout.write("Created superuser.")
        else:
            self.stderr.write("User already exists.")

    @staticmethod
    def _get_credentials():
        email = os.getenv("ADMIN_EMAIL", "admin@admin.com")
        password = os.getenv("ADMIN_PASSWORD", "admin")
        return email, password
