from django import forms
from apps.tasks.models import Task
from apps.accounts.models import User
from apps.projects.models import Project

class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(status=User.Status.ACTIVE),
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm min-h-[100px]'
        }),
        required=False,
        label="Người thực hiện (Chọn nhiều người)"
    )

    class Meta:
        model = Task
        fields = ['project', 'title', 'notes', 'additional_notes', 'start_date', 'end_date', 'status', 'priority']
        widgets = {
            'project': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'title': forms.TextInput(attrs={
                'placeholder': 'Nhập tên nhiệm vụ',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'notes': forms.Textarea(attrs={
                'placeholder': 'Ghi chú công việc...',
                'rows': 2,
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'additional_notes': forms.Textarea(attrs={
                'placeholder': 'Ghi chú bổ sung (nếu có)...',
                'rows': 2,
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
        project = kwargs.pop('project', None)
        super().__init__(*args, **kwargs)

        self.fields['start_date'].required = True
        self.fields['start_date'].error_messages = {'required': '⚠️ Bắt buộc phải chọn Ngày bắt đầu để tạo phân công lịch!'}
        self.fields['end_date'].required = True
        self.fields['end_date'].error_messages = {'required': '⚠️ Bắt buộc phải chọn Ngày kết thúc để tạo phân công lịch!'}

        if project:
            self.fields['project'].initial = project
            # Filter assignees to users in the project
            project_user_ids = project.memberships.values_list('user_id', flat=True)
            self.fields['assignees'].queryset = User.objects.filter(id__in=project_user_ids, status=User.Status.ACTIVE)

        if self.instance and self.instance.pk:
            initial_assignees = User.objects.filter(assigned_tasks__task=self.instance)
            self.fields['assignees'].initial = initial_assignees

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if not start_date:
            self.add_error('start_date', '⚠️ Bắt buộc phải chọn Ngày bắt đầu rõ ràng cho nhiệm vụ!')
        if not end_date:
            self.add_error('end_date', '⚠️ Bắt buộc phải chọn Ngày kết thúc rõ ràng cho nhiệm vụ!')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', '⚠️ Ngày kết thúc không thể trước ngày bắt đầu.')

        return cleaned_data
