import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.accounts.models import User, Invitation, DirectMessage
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
    Registration Single-Screen View: Handles Email input, OTP request & Single-screen Completion.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = RegisterStep1Form(request.POST if request.method == 'POST' else None)

    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        otp_code = request.POST.get('otp_code', '').strip()

        if otp_code:
            # Complete registration in single screen
            if password != confirm_password:
                messages.error(request, "Mật khẩu xác nhận không trùng khớp.")
            else:
                success, result = AuthService.verify_registration_otp(
                    email=email,
                    otp_code=otp_code,
                    password=password,
                    full_name=full_name
                )
                if success:
                    messages.success(request, "Đăng ký tài khoản thành công! Vui lòng đăng nhập.")
                    return redirect('accounts:login')
                else:
                    messages.error(request, result)
        else:
            if form.is_valid():
                success, msg = AuthService.send_registration_otp(email)
                if success:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
            else:
                messages.error(request, "Vui lòng kiểm tra lại thông tin đăng ký.")

    return render(request, 'accounts/register.html', {'form': form})


def register_step2_otp_view(request):
    """
    Backwards-compatible redirect for Registration Step 2.
    """
    return redirect('accounts:register')


def forgot_password_step1_view(request):
    """
    Forgot Password Single-Screen View: Handles Email input, OTP request & Single-screen Reset.
    """
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    form = ForgotPasswordForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST':
        email = request.POST.get('email', '').lower().strip()
        otp_code = request.POST.get('otp_code', '').strip()
        new_password = request.POST.get('new_password', '')

        if otp_code and new_password:
            # Single-screen password reset completion
            v_success, v_msg = AuthService.verify_forgot_password_otp(email, otp_code)
            if not v_success:
                messages.error(request, v_msg)
            else:
                r_success, r_msg = AuthService.reset_password(email, new_password)
                if r_success:
                    messages.success(request, "Đặt lại mật khẩu thành công! Vui lòng đăng nhập bằng mật khẩu mới.")
                    return redirect('accounts:login')
                else:
                    messages.error(request, r_msg)
        else:
            if form.is_valid():
                success, msg = AuthService.send_forgot_password_otp(email)
                if success:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
            else:
                messages.error(request, "Vui lòng nhập Email hợp lệ.")

    return render(request, 'accounts/forgot_password.html', {'form': form})


def forgot_password_step2_otp_view(request):
    """
    Backwards-compatible redirect for Forgot Password Step 2.
    """
    return redirect('accounts:forgot_password')


@csrf_exempt
def resend_otp_api_view(request):
    """
    AJAX API to send/resend 4-digit OTP for Registration or Forgot Password.
    Returns JSON response.
    """
    import json
    data = {}
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except Exception:
            pass
    else:
        data = request.POST

    email = data.get('email', '').strip().lower()
    purpose = data.get('purpose', 'FORGOT_PASSWORD')

    if not email:
        return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập địa chỉ email.'}, status=400)

    if purpose == 'REGISTER':
        success, msg = AuthService.send_registration_otp(email)
    else:
        success, msg = AuthService.send_forgot_password_otp(email)

    if success:
        import re
        otp_match = re.search(r'\b\d{4}\b', msg)
        otp_code = otp_match.group(0) if otp_match else ''
        return JsonResponse({'status': 'success', 'message': msg, 'email': email, 'otp_code': otp_code})
    else:
        return JsonResponse({'status': 'error', 'message': msg}, status=400)


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


@login_required
def members_overview_view(request):
    """
    Overview page of all system members, their assigned projects, tasks, and chat trigger.
    Accessible to all authenticated users.
    """
    from apps.projects.models import Project
    from apps.tasks.models import Task

    members = User.objects.filter(status=User.Status.ACTIVE).prefetch_related(
        'managed_projects',
        'project_memberships__project',
        'assigned_tasks__task__project'
    ).order_by('-created_at')

    members_data = []
    total_projects_count = Project.objects.count()
    total_tasks_count = Task.objects.count()

    for m in members:
        managed_projs = list(m.managed_projects.all())
        participated_projs = [pm.project for pm in m.project_memberships.all() if pm.project not in managed_projs]
        all_user_projs = managed_projs + participated_projs

        assigned_tasks = [ta.task for ta in m.assigned_tasks.all()]

        members_data.append({
            'user': m,
            'managed_projects': managed_projs,
            'participated_projects': participated_projs,
            'all_projects': all_user_projs,
            'assigned_tasks': assigned_tasks,
            'project_count': len(all_user_projs),
            'task_count': len(assigned_tasks),
        })

    context = {
        'members_data': members_data,
        'total_members': len(members),
        'total_projects_count': total_projects_count,
        'total_tasks_count': total_tasks_count,
    }
    return render(request, 'accounts/members_overview.html', context)


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


@login_required
def get_direct_messages_api_view(request, target_user_id):
    """
    API View: Fetch all messages between request.user and target_user.
    """
    target_user = get_object_or_404(User, id=target_user_id)
    
    # Mark messages from target_user to request.user as read
    DirectMessage.objects.filter(sender=target_user, recipient=request.user, is_read=False).update(is_read=True)

    msgs = DirectMessage.objects.filter(
        (Q(sender=request.user) & Q(recipient=target_user)) |
        (Q(sender=target_user) & Q(recipient=request.user))
    ).select_related('sender').order_by('created_at')

    messages_list = [
        {
            'id': str(m.id),
            'sender_id': str(m.sender.id),
            'sender_name': m.sender.display_name,
            'sender_initial': m.sender.initial_letter,
            'is_me': m.sender == request.user,
            'content': m.content,
            'is_read': m.is_read,
            'created_at': m.created_at.strftime('%H:%M %d/%m')
        }
        for m in msgs
    ]

    return JsonResponse({
        'status': 'success',
        'target_user': {
            'id': str(target_user.id),
            'name': target_user.display_name,
            'email': target_user.email,
            'initial': target_user.initial_letter
        },
        'messages': messages_list
    })


@login_required
@require_POST
def send_direct_message_api_view(request):
    """
    API View: Send a direct message to a target user.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
    except Exception:
        data = request.POST

    recipient_id = data.get('recipient_id')
    content = (data.get('content') or '').strip()

    if not recipient_id or not content:
        return JsonResponse({'status': 'error', 'message': 'Nội dung tin nhắn không được để trống.'}, status=400)

    recipient = get_object_or_404(User, id=recipient_id)

    if recipient == request.user:
        return JsonResponse({'status': 'error', 'message': 'Không thể gửi tin nhắn cho chính mình.'}, status=400)

    msg = DirectMessage.objects.create(
        sender=request.user,
        recipient=recipient,
        content=content
    )

    # Notify recipient
    try:
        from apps.notifications.models import Notification
        Notification.objects.create(
            user=recipient,
            title=f"Tin nhắn mới từ {request.user.display_name}",
            message=content[:100],
            link="/accounts/members/overview/"
        )
    except Exception:
        pass

    return JsonResponse({
        'status': 'success',
        'message': {
            'id': str(msg.id),
            'sender_id': str(request.user.id),
            'sender_name': request.user.display_name,
            'sender_initial': request.user.initial_letter,
            'is_me': True,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%H:%M %d/%m')
        }
    })

