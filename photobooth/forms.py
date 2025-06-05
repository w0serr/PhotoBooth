from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image', 'caption']


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
        fields = ['description', 'pricing_package', 'contact_info', 'event_date', 'guest_count']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Опишите ваши пожелания'}),
            'contact_info': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Телефон или e-mail'}),
            'event_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Примерное число гостей'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ваш отзыв...'}),
        }
