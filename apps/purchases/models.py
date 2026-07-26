import uuid
from django.db import models
from django.db.models import Sum
from apps.projects.models import Project
from apps.accounts.models import User

class PurchaseSession(models.Model):
    """
    Purchase Session (Phiên mua sắm) Model for The Tea System
    """
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Đang mở'
        CLOSED = 'CLOSED', 'Đã đóng'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name="Tên phiên mua sắm")
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.OPEN, 
        verbose_name="Trạng thái phiên"
    )
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="created_purchase_sessions",
        verbose_name="Người tạo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_amount(self):
        """
        Calculates total cost across all projects linked to this purchase session.
        """
        total = self.session_projects.aggregate(Sum('snapshot_amount'))['snapshot_amount__sum'] or 0
        return total

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


class PurchaseSessionProject(models.Model):
    """
    Junction table linking Projects to a PurchaseSession with snapshot cost
    """
    id = models.BigAutoField(primary_key=True)
    session = models.ForeignKey(PurchaseSession, on_delete=models.CASCADE, related_name="session_projects")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="purchase_sessions")
    snapshot_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Tổng tiền dự án (VNĐ)")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'project')

    def save(self, *args, **kwargs):
        # Auto compute snapshot_amount from project components total cost
        comp_total = self.project.components.aggregate(Sum('total_price'))['total_price__sum'] or 0
        self.snapshot_amount = comp_total
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.session.name} -> {self.project.name} ({self.snapshot_amount:,.0f} VNĐ)"
