from django.db import models

from django.urls import reverse
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower 

# Create your models here.
class Customer(models.Model):
	FirstName = models.CharField(null=False, blank=False, max_length=200,  help_text='Enter your First Name')
	Surname = models.CharField(null=False, blank=False, max_length=200,  help_text='Enter your Surname')
	Email = models.EmailField(max_length=100, unique=True, null=False, blank=False help_text='Enter an Email address')
	DateRegistered = models.DateField()
	PhoneNumber = models.CharField(null=True, blank=True, max_length=12, help_text='Enter a Phone Number')	
	CountryOfOrigin = models.CharField(null=False, blank=False, max_length=50,  help_text='Enter your Country of Origin')
	PrimaryLanguage = models.CharField(null=False, blank=False, max_length=30,  help_text='Enter your Primary Language')

	def __str__(self):
        	return self.FirstName + " " + self.Surname

class CustomerTravelPreferences(models.Model):
	Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, help_text="Choose a Customer" )
	TravelPreferences = models.CharField(null=True, blank=True, max_length=30)

class TourGuide(models.Model):
	FirstName = models.CharField(null=True, blank=True, max_length=200,  help_text='Enter your First Name')
	Surname = models.CharField(null=True, blank=True, max_length=200,  help_text='Enter your Surname')
	Email = models.EmailField(max_length=100, unique=True, help_text='Enter an Email address')
	DateRegistered = models.DateField()
	PhoneNumber = models.CharField(null=True, blank=True, max_length=12, help_text='Enter a Phone Number')
	YearsofExperience = models.IntegerField(null=True, blank=True, help_text='Enter your Years of Experience')
	PrimaryLanguage = models.CharField(null=True, blank=True, max_length=30,  help_text='Enter your Primary Language')
	Biography = models.CharField(null=True, blank=True, max_length=30,  help_text='Enter a biography of yourself')

class LanguagesSpoken(models.Model):
	Guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, help_text="Choose a Guide" )
	Language = models.CharField(null=True, blank=True, max_length=30,help_text="Enter a language" )

class Booking(models.Model):
	BOOKING_STATUS_CHOICES = (
        ("PAID" , "paid"),
        ("UNPAID" , "unpaid"),
    )
	Customer = models.ForeignKey(Customer, on_delete=models.CASCADE, help_text="Choose a Customer")
	DateTimeRequested = models.DateTimeField()
	TourDate = models.DateField()
	TotalPrice = models.DecimalField(decimal_places=2, max_digits=10)
	NumberOfParticipants = models.IntegerField(null=True, blank=True, help_text='Enter the Number of Participants')
	BookingStatus = models.CharField(max_length=20, choices = BOOKING_STATUS_CHOICES)

	
	
	

	
	
	
	