from django import forms
from apps.accounts.models import User

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'name@company.com',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition text-sm'
        })
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent transition text-sm'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        label="Ghi nhớ đăng nhập"
    )


class RegisterStep1Form(forms.Form):
    email = forms.EmailField(
        label="Email (đã nhận lời mời từ Admin)",
        widget=forms.EmailInput(attrs={
            'placeholder': 'your_invited_email@company.com',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )
    full_name = forms.CharField(
        label="Họ và tên",
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nguyễn Văn A',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Tối thiểu 6 ký tự',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )
    confirm_password = forms.CharField(
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập lại mật khẩu',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and len(password) < 6:
            self.add_error('password', 'Mật khẩu phải chứa ít nhất 6 ký tự.')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Mật khẩu xác nhận không khớp.')
        return cleaned_data


class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(
        label="Mã OTP 4 số",
        max_length=4,
        min_length=4,
        widget=forms.TextInput(attrs={
            'placeholder': '1234',
            'class': 'w-full text-center text-2xl font-bold tracking-widest py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500'
        })
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email tài khoản",
        widget=forms.EmailInput(attrs={
            'placeholder': 'email@company.com',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label="Mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mật khẩu mới (tối thiểu 6 ký tự)',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )
    confirm_password = forms.CharField(
        label="Xác nhận mật khẩu mới",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Nhập lại mật khẩu mới',
            'class': 'w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and len(password) < 6:
            self.add_error('password', 'Mật khẩu phải có ít nhất 6 ký tự.')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Mật khẩu xác nhận không khớp.')
        return cleaned_data


class InviteMemberForm(forms.Form):
    email = forms.EmailField(
        label="Email thành viên muốn mời",
        widget=forms.EmailInput(attrs={
            'placeholder': 'member@company.com',
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        })
    )
