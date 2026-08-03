import secrets
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.accounts.models import User, Invitation, OTPCode

class AuthService:
    @staticmethod
    def invite_member(email, invited_by_user):
        """
        Admin invites a member by Email.
        """
        email = email.lower().strip()
        if User.objects.filter(email=email).exists():
            return False, "Email này đã có tài khoản trong hệ thống."
        
        token = secrets.token_urlsafe(32)
        invitation, created = Invitation.objects.update_or_create(
            email=email,
            defaults={
                'invited_by': invited_by_user,
                'token': token,
                'is_used': False,
            }
        )

        # Send Email notification or console log
        subject = "[The Tea] Lời mời tham gia hệ thống Quản lý Dự án"
        message = f"Xin chào,\n\nBạn đã được Admin ({invited_by_user.email}) mời tham gia hệ thống The Tea.\n\nVui lòng truy cập trang Đăng ký và sử dụng email ({email}) để tạo tài khoản.\n\nTrân trọng,\nThe Tea Team"
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True
            )
        except Exception:
            pass

        return True, f"Đã gửi lời mời thành công tới email: {email}"

    @staticmethod
    def send_registration_otp(email):
        """
        Sends 4-digit OTP code for registration. Auto-creates invitation record if not present.
        """
        email = email.lower().strip()
        if User.objects.filter(email=email).exists():
            return False, "Tài khoản với email này đã tồn tại trong hệ thống."

        # Automatically ensure an invitation record exists
        invitation, _ = Invitation.objects.get_or_create(
            email=email,
            is_used=False,
            defaults={'invited_by': None, 'token': secrets.token_urlsafe(32)}
        )

        otp = OTPCode.generate_otp(email, OTPCode.Purpose.REGISTER)
        
        subject = "[The Tea] Mã OTP xác thực Đăng ký tài khoản"
        message = f"Xin chào,\n\nMã OTP xác thực đăng ký tài khoản của bạn là: {otp.code}\n\nMã có hiệu lực trong 10 phút. Không chia sẻ mã này cho bất kỳ ai.\n\nTrân trọng,\nThe Tea Team"
        
        # Attempt email send
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL or 'The Tea System <noreply@thetea.local>',
                recipient_list=[email],
                fail_silently=True
            )
        except Exception:
            pass

        return True, f"Mã OTP 4 số xác thực của bạn là: {otp.code} (Đã khởi tạo cho email {email})"

    @staticmethod
    def verify_registration_otp(email, otp_code, password, full_name=""):
        """
        Verifies registration OTP and creates the User account.
        """
        email = email.lower().strip()
        otp = OTPCode.objects.filter(
            email=email,
            code=otp_code,
            purpose=OTPCode.Purpose.REGISTER,
            is_verified=False
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            return False, "Mã OTP không chính xác hoặc đã hết hạn."

        invitation = Invitation.objects.filter(email=email, is_used=False).first()
        if not invitation:
            invitation, _ = Invitation.objects.get_or_create(
                email=email,
                is_used=False,
                defaults={'invited_by': None, 'token': secrets.token_urlsafe(32)}
            )

        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            full_name=full_name or email.split('@')[0],
            role=User.Role.MEMBER,
            status=User.Status.ACTIVE
        )

        # Mark OTP and Invitation as used
        otp.is_verified = True
        otp.save()
        invitation.is_used = True
        invitation.save()

        return True, user

    @staticmethod
    def send_forgot_password_otp(email):
        """
        Sends 4-digit OTP for password reset if user exists and is active.
        """
        email = email.lower().strip()
        user = User.objects.filter(email=email).first()
        if not user:
            return False, "Không tìm thấy tài khoản tương ứng với email này."
        
        if user.is_locked():
            return False, "Tài khoản của bạn đã bị khóa. Không thể thực hiện đặt lại mật khẩu."

        otp = OTPCode.generate_otp(email, OTPCode.Purpose.FORGOT_PASSWORD)
        
        subject = "[The Tea] Mã OTP Đặt lại mật khẩu"
        message = f"Xin chào,\n\nMã OTP để đặt lại mật khẩu tài khoản của bạn là: {otp.code}\n\nMã có hiệu lực trong 10 phút. Không chia sẻ mã này cho bất kỳ ai.\n\nTrân trọng,\nThe Tea Team"
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL or 'The Tea System <noreply@thetea.local>',
                recipient_list=[email],
                fail_silently=True
            )
        except Exception:
            pass

        return True, f"Mã OTP 4 số đặt lại mật khẩu của bạn là: {otp.code} (Đã khởi tạo cho email {email})"

    @staticmethod
    def verify_forgot_password_otp(email, otp_code):
        """
        Validates OTP code for password reset.
        """
        email = email.lower().strip()
        otp = OTPCode.objects.filter(
            email=email,
            code=otp_code,
            purpose=OTPCode.Purpose.FORGOT_PASSWORD,
            is_verified=False
        ).order_by('-created_at').first()

        if not otp or not otp.is_valid():
            return False, "Mã OTP không đúng hoặc đã hết hạn."

        otp.is_verified = True
        otp.save()
        return True, "Xác thực OTP thành công. Vui lòng nhập mật khẩu mới."

    @staticmethod
    def reset_password(email, new_password):
        """
        Resets user password after OTP verification.
        """
        email = email.lower().strip()
        user = User.objects.filter(email=email).first()
        if not user:
            return False, "Người dùng không tồn tại."

        user.set_password(new_password)
        user.save()
        return True, "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."
