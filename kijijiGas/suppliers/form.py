from django import forms
from .models import Suppliers

class SupplierRegistrationForm(forms.ModelForm):
    class Meta:
        model = Suppliers
        fields = ['name', 'email', 'phone', 'location', 'refill_price']
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control'}),
            'email': forms.EmailInput(attrs={'class':'form-control'}),
            'phone': forms.TextInput(attrs={'class':'form-control'}),
            'location': forms.TextInput(attrs={'class':'form-control'}),
            'refill_price': forms.NumberInput(attrs={'class':'form-control'}),
        }
