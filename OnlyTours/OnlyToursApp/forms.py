from django import forms
from django.utils import timezone
from .models import Customer,TourGuide,Booking,Listings
from django.core.validators import MinLengthValidator
from django.contrib.auth.forms import UserCreationForm
from .models import Booking
from .models import Review
from .import payments
import re
from django.contrib.auth.models import User

DOCUMENT_TYPE_CHOICES = [
    ('NATIONAL_ID', 'National ID card'),
    ('PASSPORT', 'Passport'),
    ('GUIDE_LICENCE', 'Tour guide licence'),
]

class CustomerRegisterForm(forms.ModelForm):
	class Meta:
		model = Customer
		fields = ['username','password','first_name','last_name','email','PhoneNumber','CountryOfOrigin','PrimaryLanguage']
		widgets = {'password':forms.PasswordInput}

class GuideRegisterForm(UserCreationForm):
    # not a TourGuide field: the view saves it on TourGuideRegistration
    DocumentType = forms.ChoiceField(
        label='Verification document',
        choices=[('', 'Select a document type')] + DOCUMENT_TYPE_CHOICES,
    )

    class Meta(UserCreationForm.Meta):
        model = TourGuide
        fields = ['username', 'first_name', 'last_name', 'email', 'PhoneNumber',
                  'YearsofExperience', 'PrimaryLanguage', 'Biography']
        widgets = {'Biography': forms.Textarea(attrs={'rows': 4, 'maxlength': 500})}

    field_order = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email',
                   'PhoneNumber', 'PrimaryLanguage', 'YearsofExperience', 'Biography', 'DocumentType']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # the model allows blank for these; the registration form must not
        for name in ['first_name', 'last_name', 'email', 'PhoneNumber',
                     'YearsofExperience', 'PrimaryLanguage', 'Biography']:
            self.fields[name].required = True

    def _clean_name(self, field, label):
        value = self.cleaned_data[field].strip()
        if not re.fullmatch(r"[A-Za-z\s'-]{2,30}", value):
            raise forms.ValidationError(
                f'{label} must contain letters only (2-30 characters, no numbers or special characters).')
        return value

    def clean_first_name(self):
        return self._clean_name('first_name', 'First name')

    def clean_last_name(self):
        return self._clean_name('last_name', 'Last name')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_PhoneNumber(self):
        phone = self.cleaned_data['PhoneNumber'].strip()
        if not re.fullmatch(r'\+?[0-9\s\-]{7,15}', phone):
            raise forms.ValidationError('Enter a valid phone number (7-15 digits, may include + and spaces).')
        return phone

    def clean_PrimaryLanguage(self):
        language = self.cleaned_data['PrimaryLanguage'].strip()
        if not re.fullmatch(r"[A-Za-z\s'-]{2,30}", language):
            raise forms.ValidationError('Enter a language name using letters only.')
        return language

    def clean_YearsofExperience(self):
        years = self.cleaned_data['YearsofExperience']
        if years < 0 or years > 60:
            raise forms.ValidationError('Years of experience must be between 0 and 60.')
        return years

    def clean_Biography(self):
        bio = self.cleaned_data['Biography'].strip()
        if len(bio) < 20:
            raise forms.ValidationError('Please write at least 20 characters about yourself.')
        return bio

    def clean_password1(self):
        # on top of AUTH_PASSWORD_VALIDATORS in settings.py
        password = self.cleaned_data.get('password1')
        if password and (not re.search('[A-Za-z]', password) or not re.search('[0-9]', password)):
            raise forms.ValidationError('Password must contain both letters and numbers.')
        return password

    
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

class PaymentForm(forms.Form):
    card_name = forms.CharField(label='Name on card', max_length=60)
    card_number = forms.CharField(label='Card number', max_length=19,
                                  help_text='16 digits, for example 4242 4242 4242 4242')
    expiry = forms.CharField(label='Expiry date', max_length=5,
                             help_text='MM/YY, for example 08/29')
    cvv = forms.CharField(label='CVV', max_length=3, widget=forms.PasswordInput,
                          help_text='The 3 digits on the back of the card')

    def clean_card_number(self):
        number = self.cleaned_data['card_number'].replace(' ', '')
        if not number.isdigit() or len(number) != 16:
            raise forms.ValidationError('Enter a 16-digit card number.')
        if not payments.luhn_valid(number):
            raise forms.ValidationError('This card number is not valid. Please check it.')
        return number

    def clean_expiry(self):
        expiry = self.cleaned_data['expiry']
        parts = expiry.split('/')
        if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit() or len(parts[1]) != 2:
            raise forms.ValidationError('Enter the expiry date as MM/YY.')
        month = int(parts[0])
        year = 2000 + int(parts[1])
        if not 1 <= month <= 12:
            raise forms.ValidationError('The month must be between 01 and 12.')
        today = timezone.localdate()
        if (year, month) < (today.year, today.month):
            raise forms.ValidationError('This card has expired.')
        return expiry

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']
        if not cvv.isdigit() or len(cvv) != 3:
            raise forms.ValidationError('The CVV should be 3 digits.')
        return cvv
		



DIFFICULTY_LEVEL_CHOICES = (("EASY", "Easy"),
        ("MODERATE", "Moderate"),
        ("DIFFICULT", "Difficult"),	)




class ListingForm(forms.ModelForm):
      class Meta:
        model = Listings
        fields = ['TourName', 'LDescription', 'Duration', 'MeetingPoint', 'Price',
                  'AvailabilityDate', 'ListingsStatus', 'Attraction']
        labels = {
            'TourName': 'Tour name',
            'LDescription': 'Description',
            'Duration': 'Duration (hours)',
            'MeetingPoint': 'Meeting point',
            'Price': 'Price per person (Rs)',
            'AvailabilityDate': 'Available from',
            'ListingsStatus': 'Status',
            'Attraction': 'Attractions this tour visits',
        }
        widgets = {
            'AvailabilityDate': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'LDescription': forms.Textarea(attrs={'rows': 4}),
            'Attraction': forms.CheckboxSelectMultiple,
        }
   





RATING_CHOICES = [
    (5, '5 ★'),
    (4, '4 ★'),
    (3, '3 ★'),
    (2, '2 ★'),
    (1, '1 ★'),
]


class ReviewForm(forms.ModelForm):
    # not stored on Review: only used to confirm who is reviewing
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = Review
        fields = ['Rating', 'Comment']
        labels = {'Rating': 'Your Rating', 'Comment': 'Your Review'}
        widgets = {
            'Rating': forms.RadioSelect(choices=RATING_CHOICES),
            'Comment': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Tell us about your tour...'}),
        }

    def __init__(self, *args, booking=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.booking = booking                      # the booking from the URL, given by the view
        self.fields['Comment'].required = True      # the model allows blank, the review form shouldn't

    def clean_Comment(self):
        comment = self.cleaned_data['Comment'].strip()
        if len(comment) < 10:
            raise forms.ValidationError('Please write at least 10 characters.')
        return comment

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        if email and self.booking is not None:
            # the email must be the one registered for the customer who made this booking
            if email.lower() != self.booking.Customer.email.lower():
                raise forms.ValidationError(
                    "This email doesn't match the customer who made this booking."
                )
            if Review.objects.filter(Booking=self.booking).exists():
                raise forms.ValidationError('This booking has already been reviewed.')

            return cleaned
            
        cleaned['booking'] = Booking

        return cleaned

class GuideResponseForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['GuideResponse']
        widgets = {'GuideResponse': forms.Textarea( attrs={'rows': 3, 'maxlength': 1000, 'required': 'required'})}

