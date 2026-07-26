from django import forms
from apps.projects.models import Project
from apps.accounts.models import User

class ProjectForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(status=User.Status.ACTIVE),
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm min-h-[120px]'
        }),
        required=False,
        label="Người tham gia dự án"
    )

    class Meta:
        model = Project
        fields = ['name', 'description', 'manager', 'start_date', 'end_date', 'status', 'priority']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Nhập tên dự án',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Mô tả chi tiết dự án...',
                'rows': 3,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'manager': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit manager choices to active users
        self.fields['manager'].queryset = User.objects.filter(status=User.Status.ACTIVE)
        self.fields['manager'].empty_label = "-- Chưa chọn người quản lý --"

        if self.instance and self.instance.pk:
            initial_members = User.objects.filter(project_memberships__project=self.instance)
            self.fields['members'].initial = initial_members

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'Ngày kết thúc không thể trước ngày bắt đầu.')

        return cleaned_data


class AssignManagerForm(forms.Form):
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(status=User.Status.ACTIVE),
        empty_label="-- Chọn người quản lý mới --",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
        }),
        label="Người quản lý mới"
    )
