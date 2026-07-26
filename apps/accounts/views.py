from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from apps.accounts.models import User, Invitation
from apps.accounts.forms import (
    LoginForm, RegisterStep1Form, OTPVerifyForm,
    ForgotPasswordForm, ResetPasswordForm, InviteMemberForm
)
from apps.accounts.services.auth_service import AuthService

def login_view(request):
    """
    User Login View with status lock check and Remember Me.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data['remember_me']

            user = authenticate(request, username=email, password=password)

            if user is not None:
                if user.is_locked():
                    messages.error(request, "Tài khoản của bạn đã bị khóa. Vui lòng liên hệ Admin.")
                    return render(request, 'accounts/login.html', {'form': form})

                login(request, user)
                if remember_me:
                    # Remember for 2 weeks
                    request.session.set_expiry(1209600)
                else:
                    # Expire on browser close
                    request.session.set_expiry(0)

                messages.success(request, f"Đăng nhập thành công! Chào mừng {user.full_name or user.email}.")
                return redirect('dashboard:index')
            else:
                messages.error(request, "Email hoặc mật khẩu không chính xác.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    Logout view
    """
    logout(request)
    messages.info(request, "Bạn đã đăng xuất khỏi hệ thống.")
    return redirect('accounts:login')


def register_step1_view(request):
    """
    Registration Step 1: Input Email (must be invited), Password & Confirm Password.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = RegisterStep1Form(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            full_name = form.cleaned_data['full_name']
            password = form.cleaned_data['password']

            success, msg = AuthService.send_registration_otp(email)
            if success:
                # Store in session for step 2
                request.session['reg_email'] = email
                request.session['reg_full_name'] = full_name
                request.session['reg_password'] = password
                messages.success(request, msg)
                return redirect('accounts:register_otp')
            else:
                messages.error(request, msg)
    else:
        form = RegisterStep1Form()

    return render(request, 'accounts/register.html', {'form': form})


def register_step2_otp_view(request):
    """
    Registration Step 2: Input 4-digit OTP code to complete registration.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    reg_email = request.session.get('reg_email')
    reg_password = request.session.get('reg_password')
    reg_full_name = request.session.get('reg_full_name', '')

    if not reg_email or not reg_password:
        messages.warning(request, "Vui lòng nhập thông tin đăng ký trước.")
        return redirect('accounts:register')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            success, result = AuthService.verify_registration_otp(
                email=reg_email,
                otp_code=otp_code,
                password=reg_password,
                full_name=reg_full_name
            )
            if success:
                # Clear session
                request.session.pop('reg_email', None)
                request.session.pop('reg_password', None)
                request.session.pop('reg_full_name', None)

                messages.success(request, "Đăng ký tài khoản thành công! Vui lòng đăng nhập.")
                return redirect('accounts:login')
            else:
                messages.error(request, result)
    else:
        form = OTPVerifyForm()

    return render(request, 'accounts/verify_otp.html', {
        'form': form,
        'email': reg_email,
        'title': 'Xác thực OTP Đăng ký',
        'subtitle': f'Mã OTP 4 số đã được gửi tới email {reg_email}'
    })


def forgot_password_step1_view(request):
    """
    Forgot Password Step 1: Input Email.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            success, msg = AuthService.send_forgot_password_otp(email)
            if success:
                request.session['forgot_email'] = email
                messages.success(request, msg)
                return redirect('accounts:forgot_password_otp')
            else:
                messages.error(request, msg)
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/forgot_password.html', {'form': form})


def forgot_password_step2_otp_view(request):
    """
    Forgot Password Step 2: Input 4-digit OTP.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    forgot_email = request.session.get('forgot_email')
    if not forgot_email:
        messages.warning(request, "Vui lòng nhập Email để quên mật khẩu trước.")
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            otp_code = form.cleaned_data['otp_code']
            success, msg = AuthService.verify_forgot_password_otp(forgot_email, otp_code)
            if success:
                request.session['forgot_otp_verified'] = True
                messages.success(request, msg)
                return redirect('accounts:reset_password')
            else:
                messages.error(request, msg)
    else:
        form = OTPVerifyForm()

    return render(request, 'accounts/verify_otp.html', {
        'form': form,
        'email': forgot_email,
        'title': 'Xác thực OTP Quên Mật Khẩu',
        'subtitle': f'Mã OTP 4 số đã được gửi tới email {forgot_email}'
    })


def reset_password_step3_view(request):
    """
    Forgot Password Step 3: Set New Password.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    forgot_email = request.session.get('forgot_email')
    forgot_verified = request.session.get('forgot_otp_verified')

    if not forgot_email or not forgot_verified:
        messages.error(request, "Phiên xác thực không hợp lệ.")
        return redirect('accounts:forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['password']
            success, msg = AuthService.reset_password(forgot_email, new_password)
            if success:
                request.session.pop('forgot_email', None)
                request.session.pop('forgot_otp_verified', None)
                messages.success(request, msg)
                return redirect('accounts:login')
            else:
                messages.error(request, msg)
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/reset_password.html', {'form': form})


# ==========================================
# ADMIN USER MANAGEMENT VIEWS
# ==========================================

@login_required
def member_list_view(request):
    """
    Admin View: List members, Pending Invitations, Invite Member form, Action Modals.
    """
    if not request.user.is_admin():
        messages.error(request, "Bạn không có quyền truy cập trang Quản lý thành viên.")
        return redirect('dashboard:index')

    members = User.objects.all().order_by('-created_at')
    invitations = Invitation.objects.filter(is_used=False).order_by('-created_at')
    invite_form = InviteMemberForm()

    context = {
        'members': members,
        'invitations': invitations,
        'invite_form': invite_form
    }
    return render(request, 'accounts/member_list.html', context)


@login_required
@require_POST
def invite_member_view(request):
    """
    Admin View: Send Invitation Email.
    """
    if not request.user.is_admin():
        messages.error(request, "Chỉ Admin mới có quyền mời thành viên.")
        return redirect('dashboard:index')

    form = InviteMemberForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        success, msg = AuthService.invite_member(email, request.user)
        if success:
            messages.success(request, msg)
        else:
            messages.error(request, msg)
    else:
        messages.error(request, "Vui lòng nhập Email hợp lệ.")

    return redirect('accounts:member_list')


@login_required
@require_POST
def toggle_user_status_view(request, user_id):
    """
    Admin View: Lock or Unlock account (with confirmation).
    """
    if not request.user.is_admin():
        messages.error(request, "Không có quyền thực hiện.")
        return redirect('dashboard:index')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Bạn không thể tự khóa tài khoản của chính mình.")
        return redirect('accounts:member_list')

    if target_user.status == User.Status.ACTIVE:
        target_user.status = User.Status.LOCKED
        messages.warning(request, f"Đã khóa tài khoản {target_user.email}.")
    else:
        target_user.status = User.Status.ACTIVE
        messages.success(request, f"Đã mở khóa tài khoản {target_user.email}.")
    
    target_user.save()
    return redirect('accounts:member_list')


@login_required
@require_POST
def delete_user_view(request, user_id):
    """
    Admin View: Delete account (with confirmation).
    """
    if not request.user.is_admin():
        messages.error(request, "Không có quyền thực hiện.")
        return redirect('dashboard:index')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Bạn không thể xóa tài khoản của chính mình.")
        return redirect('accounts:member_list')

    email = target_user.email
    target_user.delete()
    messages.success(request, f"Đã xóa tài khoản {email} khỏi hệ thống.")
    return redirect('accounts:member_list')


@login_required
@require_POST
def change_user_role_view(request, user_id):
    """
    Admin View: Change role between ADMIN and MEMBER.
    """
    if not request.user.is_admin():
        messages.error(request, "Không có quyền thực hiện.")
        return redirect('dashboard:index')

    target_user = get_object_or_404(User, id=user_id)
    new_role = request.POST.get('role')

    if new_role in [User.Role.ADMIN, User.Role.MEMBER]:
        target_user.role = new_role
        target_user.save()
        messages.success(request, f"Đã đổi vai trò của {target_user.email} thành {target_user.get_role_display()}.")
    else:
        messages.error(request, "Vai trò không hợp lệ.")

    return redirect('accounts:member_list')


@login_required
@require_POST
def transfer_admin_view(request, user_id):
    """
    Admin View: Transfer Admin rights to another member.
    """
    if not request.user.is_admin():
        messages.error(request, "Không có quyền thực hiện.")
        return redirect('dashboard:index')

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "Bạn đã là Admin.")
        return redirect('accounts:member_list')

    # Assign Admin to target user, demote current admin to Member
    target_user.role = User.Role.ADMIN
    target_user.save()

    request.user.role = User.Role.MEMBER
    request.user.save()

    messages.success(request, f"Đã chuyển quyền Admin cho {target_user.email}. Vai trò của bạn hiện là Member.")
    return redirect('dashboard:index')
