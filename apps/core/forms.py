from django import forms
from .models import Review, InsuranceContract

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} звезд") for i in range(1, 6)]),
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
        }

class InsuranceContractForm(forms.ModelForm):
    class Meta:
        model = InsuranceContract
        fields = ['insurance_type', 'insurance_sum', 'tariff_rate', 'branch']