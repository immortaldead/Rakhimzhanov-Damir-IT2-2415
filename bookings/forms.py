from django import forms
from .models import Reservation, Restaurant, Table
from django.core.exceptions import ValidationError
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'address']

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['table', 'date', 'time', 'guests', 'special_requests']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def clean_date(self):
        data = self.cleaned_data['date']
        if data < date.today():
            raise ValidationError("Нельзя забронировать столик на прошедшую дату")
        return data
    

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['number', 'capacity', 'shape', 'is_active']
        labels = {
            'restaurant': 'Ресторан',
            'number': 'Номер стола',
            'capacity': 'Вместимость',
            'shape': 'Форма',
            'is_active': 'Доступен для брони',
        }
        widgets = {
            'restaurant': forms.Select(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например, A1'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'shape': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }