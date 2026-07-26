from django.core.management.base import BaseCommand
from apps.accounts.models import User

class Command(BaseCommand):
    help = "Creates the initial Admin user for The Tea"

    def handle(self, *args, **options):
        admins = [
            ("admin@thetea.local", "adminpassword123", "System Admin"),
            ("pttthptndc10@gmail.com", "adminpassword123", "Admin PTT"),
        ]
        
        for email, password, full_name in admins:
            if not User.objects.filter(email=email).exists():
                user = User.objects.create_superuser(
                    username=email,
                    email=email,
                    password=password,
                    full_name=full_name,
                    role=User.Role.ADMIN,
                    status=User.Status.ACTIVE
                )
                self.stdout.write(f"Created Admin user successfully: {email}")
            else:
                user = User.objects.get(email=email)
                user.role = User.Role.ADMIN
                user.is_staff = True
                user.is_superuser = True
                user.save()
                self.stdout.write(f"Updated Admin user successfully: {email}")
