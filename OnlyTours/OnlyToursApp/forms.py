from django import forms
from .models import Customer,TourGuide
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm


class CustomerRegisterForm(forms.ModelForm):

<<<<<<< Updated upstream
    class Meta:
        model = Customer
        fields = ['username','password','first_name','last_name','email','PhoneNumber','CountryOfOrigin','PrimaryLanguage']
=======
	class Meta:
		model = Customer
		fields = ['username','password','first_name','last_name','email','PhoneNumber','CountryOfOrigin','PrimaryLanguage']
		widgets = {'password':forms.PasswordInput}

class GuideRegisterForm(forms.ModelForm):

	class Meta:
		model = TourGuide
		fields = ['username','password','first_name','last_name','email','PhoneNumber','YearsofExperience','PrimaryLanguage','Biography']
		widgets = {'password':forms.PasswordInput}	
>>>>>>> Stashed changes
