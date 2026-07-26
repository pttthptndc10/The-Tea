import uuid
from django.db import models
from apps.projects.models import Project
from apps.accounts.models import User

class Task(models.Model):
    """
    Task Model for The Tea System
    """
    class Status(models.TextChoices):
        TODO = 'TODO', 'Chưa thực hiện'
        IN_PROGRESS = 'IN_PROGRESS', 'Đang thực hiện'
        COMPLETED = 'COMPLETED', 'Hoàn thành'
        CANCELLED = 'CANCELLED', 'Đã hủy'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Thấp'
        MEDIUM = 'MEDIUM', 'Trung bình'
        HIGH = 'HIGH', 'Cao'
        URGENT = 'URGENT', 'Khẩn cấp'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks", verbose_name="Dự án")
    
    title = models.CharField(max_length=255, verbose_name="Tên nhiệm vụ")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    additional_notes = models.TextField(blank=True, verbose_name="Ghi chú bổ sung")
    
    start_date = models.DateField(verbose_name="Ngày bắt đầu")
    end_date = models.DateField(verbose_name="Ngày kết thúc")
    
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.TODO, 
        verbose_name="Trạng thái"
    )
    priority = models.CharField(
        max_length=20, 
        choices=Priority.choices, 
        default=Priority.MEDIUM, 
        verbose_name="Độ ưu tiên"
    )
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="created_tasks",
        verbose_name="Người tạo"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_cancelled(self):
        return self.status == self.Status.CANCELLED

    def __str__(self):
        return f"[{self.project.name}] {self.title} ({self.get_status_display()})"


class TaskAssignee(models.Model):
    """
    Multi-assignee junction model for Tasks
    """
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignees")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_tasks")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'user')

    def __str__(self):
        return f"{self.user.email} -> Task: {self.task.title}"
