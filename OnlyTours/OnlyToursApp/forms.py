from django import forms
from .models import Customer
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(forms.ModelForm):

	class Meta:
		model = Customer
		fields = ['username','password','first_name','last_name','email','PhoneNumber','CountryOfOrigin','PrimaryLanguage']
		widgets = {'password':forms.PasswordInput}