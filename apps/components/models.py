import uuid
from django.db import models
from apps.projects.models import Project

class Component(models.Model):
    """
    Component / Material (Linh kiện) Model for The Tea System
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="components", verbose_name="Dự án")
    
    name = models.CharField(max_length=255, verbose_name="Tên linh kiện")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    unit_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Đơn giá (VNĐ)")
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Thành tiền (VNĐ)")
    
    shop = models.CharField(max_length=255, blank=True, verbose_name="Shop / Cửa hàng mua")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto calculate total_price = quantity * unit_price
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.project.name}] {self.name} x{self.quantity} ({self.total_price:,.0f} VNĐ)"
