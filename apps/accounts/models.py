import random
import string
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    """
    Custom User Model for The Tea System
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MEMBER = 'MEMBER', 'Member'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Đang hoạt động'
        LOCKED = 'LOCKED', 'Đã khóa'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, blank=True, verbose_name="Họ và tên")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER, verbose_name="Vai trò")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

    def is_locked(self):
        return self.status == self.Status.LOCKED

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser or self.is_staff

    def __str__(self):
        return f"{self.full_name or self.email} ({self.get_role_display()})"


class Invitation(models.Model):
    """
    Tracks email invitations sent by Admin to allow registration
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="Email được mời")
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="sent_invitations")
    token = models.CharField(max_length=64, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mời {self.email} (Đã dùng: {self.is_used})"


class OTPCode(models.Model):
    """
    4-digit OTP codes for Registration and Password Reset
    """
    class Purpose(models.TextChoices):
        REGISTER = 'REGISTER', 'Đăng ký tài khoản'
        FORGOT_PASSWORD = 'FORGOT_PASSWORD', 'Quên mật khẩu'

    email = models.EmailField()
    code = models.CharField(max_length=4)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    @classmethod
    def generate_otp(cls, email, purpose, valid_minutes=10):
        # Invalidate old unverified OTPs for same email & purpose
        cls.objects.filter(email=email, purpose=purpose, is_verified=False).delete()
        code = f"{random.randint(1000, 9999)}"
        expires_at = timezone.now() + timedelta(minutes=valid_minutes)
        return cls.objects.create(
            email=email,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )

    def is_valid(self):
        return not self.is_verified and timezone.now() <= self.expires_at

    def __str__(self):
        return f"OTP {self.code} cho {self.email} ({self.purpose})"
