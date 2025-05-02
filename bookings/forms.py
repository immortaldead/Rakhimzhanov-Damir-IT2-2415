from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
from datetime import date

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