import uuid
from django.db import models
from apps.accounts.models import User

class Project(models.Model):
    """
    Project Model for The Tea System
    """
    class Status(models.TextChoices):
        NOT_STARTED = 'NOT_STARTED', 'Chưa bắt đầu'
        IN_PROGRESS = 'IN_PROGRESS', 'Đang thực hiện'
        ON_HOLD = 'ON_HOLD', 'Tạm dừng'
        COMPLETED = 'COMPLETED', 'Hoàn thành'
        CANCELLED = 'CANCELLED', 'Đã hủy'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Thấp'
        MEDIUM = 'MEDIUM', 'Trung bình'
        HIGH = 'HIGH', 'Cao'
        URGENT = 'URGENT', 'Khẩn cấp'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Tên dự án")
    description = models.TextField(blank=True, verbose_name="Mô tả dự án")
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="created_projects",
        verbose_name="Người tạo"
    )
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="managed_projects",
        verbose_name="Người quản lý"
    )
    
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")
    
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.NOT_STARTED, 
        verbose_name="Trạng thái"
    )
    priority = models.CharField(
        max_length=20, 
        choices=Priority.choices, 
        default=Priority.MEDIUM, 
        verbose_name="Độ ưu tiên"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_unmanaged(self):
        """
        Returns True if the project manager is missing (e.g. deleted user).
        """
        return self.manager is None or self.manager.status == User.Status.LOCKED

    def get_progress_percentage(self):
        """
        Calculates progress percentage = (Completed Tasks / Total Tasks) * 100
        Cancelled tasks count towards total tasks but NOT towards completed tasks.
        Example: 4 total tasks (2 completed, 2 cancelled) => 2/4 = 50%.
        """
        if not hasattr(self, 'tasks'):
            return 100 if self.status == self.Status.COMPLETED else 0
        try:
            total = self.tasks.count()
            if total == 0:
                return 100 if self.status == self.Status.COMPLETED else 0
            completed = self.tasks.filter(status='COMPLETED').count()
            return round((completed / total) * 100)
        except Exception:
            return 100 if self.status == self.Status.COMPLETED else 0

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class ProjectMember(models.Model):
    """
    Project Member junction model
    """
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="project_memberships")
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

    def __str__(self):
        return f"{self.user.email} -> {self.project.name}"
