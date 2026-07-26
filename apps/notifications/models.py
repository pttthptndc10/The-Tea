import uuid
from django.db import models
from apps.accounts.models import User

class Notification(models.Model):
    """
    In-App Notification Model for The Tea System
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications", verbose_name="Người nhận")
    
    title = models.CharField(max_length=255, verbose_name="Tiêu đề thông báo")
    message = models.TextField(verbose_name="Nội dung")
    link = models.CharField(max_length=500, blank=True, verbose_name="Đường dẫn xem chi tiết")
    
    is_read = models.BooleanField(default=False, verbose_name="Đã đọc")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{'ĐÃ ĐỌC' if self.is_read else 'CHƯA ĐỌC'}] {self.user.email}: {self.title}"
