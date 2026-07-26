from django import forms
from apps.purchases.models import PurchaseSession
from apps.projects.models import Project

class PurchaseSessionForm(forms.ModelForm):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=forms.SelectMultiple(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm min-h-[120px]'
        }),
        required=False,
        label="Danh sách dự án tham gia phiên mua sắm"
    )

    class Meta:
        model = PurchaseSession
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Ví dụ: Phiên mua sắm vật tư Quý 3/2026',
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            initial_projects = Project.objects.filter(purchase_sessions__session=self.instance)
            self.fields['projects'].initial = initial_projects
