from django import forms
from .models import ConsultationRequest


class ConsultationRequestForm(forms.ModelForm):
    class Meta:
        model = ConsultationRequest
        # status не даём заполнять с сайта — он выставится по умолчанию ('new'),
        # created_at тоже не трогаем (auto_now_add сам подставит)
        fields = ('name', 'contact', 'comment')