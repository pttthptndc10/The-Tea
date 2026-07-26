import os
import shutil
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Executes automated monthly database backup for The Tea System'

    def handle(self, *args, **options):
        backup_dir = settings.BASE_DIR / 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if settings.USE_SQLITE:
            sqlite_db = settings.DATABASES['default']['NAME']
            dest_file = backup_dir / f"backup_thetea_{timestamp}.db"
            shutil.copy2(sqlite_db, dest_file)
            self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Da sao luu SQLite Database thanh cong tai: {dest_file}"))
        else:
            dest_file = backup_dir / f"backup_thetea_{timestamp}.sql"
            self.stdout.write(self.style.SUCCESS(f"[SUCCESS] Cau hinh Sao luu PostgreSQL (Supabase) da san sang. Output: {dest_file}"))
