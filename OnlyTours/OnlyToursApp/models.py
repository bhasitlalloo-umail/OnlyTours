from django.db import models

from django.urls import reverse
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower 

# Create your models here.
class Customer(models.Model):
	FirstName = models.CharField(null=False, blank=False, max_length=200,  help_text='Enter your First Name')
	Surname = models.CharField(null=False, blank=False, max_length=200,  help_text='Enter your Surname')
	Email = models.EmailField(max_length=100, unique=True, null=False, blank=False, help_text='Enter an Email address')
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


class Attractions(models.Model):

    

	DIFFICULTY_LEVEL_CHOICES = (("EASY", "Easy"),
		("MODERATE", "Moderate"),
		("DIFFICULT", "Difficult"),	)

	AttractionID = models.AutoField(primary_key=True, help_text='Unique ID for the attraction')
	Name = models.CharField(null=False, blank=False, max_length=200, help_text='Enter the name of the attraction')
	Description = models.TextField(null=False, blank=False, help_text='Enter a description of the attraction')
	Region = models.CharField(null=False, blank=False, max_length=100, help_text='Enter the region of the attraction')
	IsFeatured = models.BooleanField(default=False, help_text='Indicate whether the attraction is featured')
	Longitude = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=7, help_text='Enter the longitude of the attraction')
	Latitude = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=7, help_text='Enter the latitude of the attraction')
	Distance = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, help_text='Enter the distance to the attraction')
	DifficultyLevel = models.CharField(null=True, blank=True, max_length=50, choices=DIFFICULTY_LEVEL_CHOICES, help_text='Select the difficulty level of the attraction')
	Type = models.CharField(null=False, blank=False, max_length=100, help_text='Enter the type of attraction')
	DateAdded = models.DateField(null=False, blank=False, help_text='Enter the date the attraction was added')

	def __str__(self):
		return self.Name

class Listings(models.Model):
	LISTING_STATUS_CHOICES = (
		("ACTIVE", "active"),
		("INACTIVE", "inactive"),
	)
	ListingID = models.AutoField(primary_key=True, help_text='Unique ID for the listing')
	Guide = models.ForeignKey(TourGuide, on_delete=models.CASCADE, help_text="Choose a Guide")
	TourName = models.CharField(null=False, blank=False, max_length=200, help_text='Enter the name of the tour')
	LDescription = models.TextField(null=False, blank=False, help_text='Enter a description of the tour')
	Duration = models.DecimalField(null=False, blank=False, max_digits=4, decimal_places=1, help_text='Enter the duration of the tour in hours')
	MeetingPoint = models.CharField(null=False, blank=False, max_length=200, help_text='Enter the meeting point of the tour')
	Price = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2, help_text='Enter the price per person')
	AvailabilityDate = models.DateField(null=False, blank=False, help_text='Enter the date the tour is available')
	ListingsStatus = models.CharField(max_length=20, choices=LISTING_STATUS_CHOICES, help_text='Select the status of the listing')
	DateCreated = models.DateField(null=False, blank=False, help_text='Enter the date the listing was created')

	def __str__(self):
		return self.TourName

class ListingAttractions(models.Model):
	Listing = models.ForeignKey(Listings, on_delete=models.CASCADE, help_text="Choose a Listing")
	Attraction = models.ForeignKey(Attractions, on_delete=models.CASCADE, help_text="Choose an Attraction")
	
	
	
	