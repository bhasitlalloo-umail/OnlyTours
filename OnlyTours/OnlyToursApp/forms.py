from django import forms
from django.utils import timezone
from .models import Customer,TourGuide,Booking,Listings
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm
from .models import Booking
from .models import Review

class CustomerRegisterForm(forms.ModelForm):
	class Meta:
		model = Customer
		fields = ['username','password','first_name','last_name','email','PhoneNumber','CountryOfOrigin','PrimaryLanguage']
		widgets = {'password':forms.PasswordInput}

class GuideRegisterForm(forms.ModelForm):
	class Meta:
		model = TourGuide
		fields = ['username','password','first_name','last_name','email','PhoneNumber','YearsofExperience','PrimaryLanguage','Biography']
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
   





RATING_CHOICES = [
    (5, '5 ★'),
    (4, '4 ★'),
    (3, '3 ★'),
    (2, '2 ★'),
    (1, '1 ★'),
]


class ReviewForm(forms.ModelForm):
    # not stored on Review: only used to find the customer's booking
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )
    booking_id = forms.IntegerField(
        min_value=1, label='Booking Number',
        widget=forms.NumberInput(attrs={'placeholder': 'e.g. 12'}),
    )

    class Meta:
        model = Review
        fields = ['Rating', 'Comment']
        labels = {'Rating': 'Your Rating', 'Comment': 'Your Review'}
        widgets = {
            'Rating': forms.RadioSelect(choices=RATING_CHOICES),
            'Comment': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Tell us about your tour...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['Comment'].required = True    # the model allows blank, the review form shouldn't

    def clean_Comment(self):
        comment = self.cleaned_data['Comment'].strip()
        if len(comment) < 10:
            raise forms.ValidationError('Please write at least 10 characters.')
        return comment

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        booking_id = cleaned.get('booking_id')
        if email and booking_id:
            # the email must belong to a customer already in the database,
            # and the booking must belong to that customer
            booking = Booking.objects.filter(pk=booking_id, Customer__email__iexact=email).first()
            if booking is None:
                raise forms.ValidationError(
                    "We couldn't find that booking under this email address."
                )
            if Review.objects.filter(Booking=booking).exists():
                raise forms.ValidationError('This booking has already been reviewed.')
            cleaned['booking'] = booking
        return cleaned