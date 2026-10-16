from django import forms
from django.utils import timezone
from .models import Customer,Booking,Listings
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(forms.ModelForm):

	class Meta:
		model = Customer
		fields = ['username','password','first_name','last_name','email','PhoneNumber','CountryOfOrigin','PrimaryLanguage']
		widgets = {'password':forms.PasswordInput}




class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['Listing', 'TourDate', 'TimeSlot', 'NumberOfParticipants', 'SpecialRequests']
        labels = {
            'Listing': 'Select Tour',
            'TourDate': 'Preferred Date',
            'TimeSlot': 'Preferred Time',
            'NumberOfParticipants': 'Number of Guests',
            'SpecialRequests': 'Anything else we should know?',
        }
        widgets = {
            'TourDate': forms.DateInput(attrs={'type': 'date'}),
            'TimeSlot': forms.TimeInput(attrs={'type': 'time'}),
            'NumberOfParticipants': forms.NumberInput(attrs={'min': 1, 'max': 20}),
            'SpecialRequests': forms.Textarea(attrs={
                'rows': 4, 'maxlength': 500,
                'placeholder': 'Optional: dietary needs, mobility considerations, special requests...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # only active tours can be booked
        self.fields['Listing'].queryset = Listings.objects.filter(ListingsStatus='ACTIVE')
        self.fields['Listing'].empty_label = 'Choose a tour'
        # the model allows blank guests; the form must not
        self.fields['NumberOfParticipants'].required = True

    def clean_TourDate(self):
        date = self.cleaned_data['TourDate']
        if date < timezone.localdate():
            raise forms.ValidationError('Please select a date today or later.')
        return date

    def clean_NumberOfParticipants(self):
        n = self.cleaned_data['NumberOfParticipants']
        if n < 1 or n > 20:
            raise forms.ValidationError('Number of guests must be between 1 and 20.')
        return n		
    