from django import forms
from apps.components.models import Component

class ComponentForm(forms.ModelForm):
    class Meta:
        model = Component
        fields = ['name', 'quantity', 'unit_price', 'shop', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Tên linh kiện',
                'class': 'w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm bg-white'
            }),
            'quantity': forms.NumberInput(attrs={
                'min': 1,
                'class': 'w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm bg-white'
            }),
            'unit_price': forms.NumberInput(attrs={
                'min': 0,
                'step': 1000,
                'placeholder': '0',
                'class': 'w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm bg-white'
            }),
            'shop': forms.TextInput(attrs={
                'placeholder': 'Tên shop / Link mua',
                'class': 'w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm bg-white'
            }),
            'notes': forms.TextInput(attrs={
                'placeholder': 'Ghi chú thêm...',
                'class': 'w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm bg-white'
            }),
        }
