from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Request, PricingPackage

class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class RequestForm(forms.ModelForm):
    pricing_package = forms.ModelChoiceField(
        queryset=PricingPackage.objects.all(),
        label='Выберите пакет услуг',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Request
        fields = ['description', 'pricing_package']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Опишите ваши пожелания'}),
        }
