from django import forms
from django.contrib.auth.models import User
from .models import CustomerProfile

class CustomerSignupForm(forms.ModelForm):
    county = forms.CharField(max_length=100)
    area = forms.CharField(max_length=100)
    exact_location = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password','location']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            CustomerProfile.objects.create(
                user=user,
                county=self.cleaned_data['county'],
                area=self.cleaned_data['area'],
                exact_location=self.cleaned_data['exact_location']
            )
        return user
