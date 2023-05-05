from django import forms
from django.core.validators import MinValueValidator

class UserInfoForm(forms.Form):
	age = forms.FloatField(label='年齢', validators=[MinValueValidator(18)])
	height = forms.FloatField(label='身長')
	weight = forms.FloatField(label='体重')