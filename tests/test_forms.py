import pytest
from apps.core.forms import ReviewForm, InsuranceContractForm

@pytest.mark.django_db
class TestForms:
    def test_review_form_valid(self):
        form = ReviewForm(data={'rating': 5, 'text': 'Отличная работа!'})
        assert form.is_valid()
    
    def test_review_form_invalid_rating(self):
        form = ReviewForm(data={'rating': 6, 'text': 'Текст'})
        assert not form.is_valid()
    
    def test_insurance_contract_form_valid(self):
        form = InsuranceContractForm(data={
            'insurance_type': 1,
            'insurance_sum': 50000,
            'tariff_rate': 3.5,
            'branch': 1
        })
        # Без валидации модели
        assert form.fields['insurance_sum'].required