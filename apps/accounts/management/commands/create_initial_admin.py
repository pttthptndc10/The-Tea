from django.core.management.base import BaseCommand
from apps.accounts.models import User

class Command(BaseCommand):
    help = "Creates the initial Admin user for The Tea"

    def handle(self, *args, **options):
        email = "admin@thetea.local"
        password = "adminpassword123"
        
        if not User.objects.filter(email=email).exists():
            user = User.objects.create_superuser(
                username=email,
                email=email,
                password=password,
                full_name="System Admin",
                role=User.Role.ADMIN,
                status=User.Status.ACTIVE
            )
            self.stdout.write("Created initial Admin user successfully: admin@thetea.local / adminpassword123")
        else:
            self.stdout.write("Admin user admin@thetea.local already exists.")
