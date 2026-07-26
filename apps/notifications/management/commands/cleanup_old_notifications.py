from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.notifications.models import Notification

class Command(BaseCommand):
    help = 'Cleans up notifications older than 30 days according to Master Contract requirement'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=30)
        deleted_count, _ = Notification.objects.filter(created_at__lt=cutoff_date).delete()
        self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Da don dep {deleted_count} thong bao cu hon 30 ngay."))
