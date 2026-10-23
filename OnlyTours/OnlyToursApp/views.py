from django.views.generic import TemplateView,ListView
from django.contrib.auth.views import LoginView     
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView
from django.db.models import Avg, Count
from .forms import BookingForm, ReviewForm
from .models import Booking, Listings, Customer, Attractions, TourGuide, Review,TourGuideRegistration
from django.contrib.auth import login as auth_login


# Create your views here.
class HomeView(TemplateView):
	template_name = 'home.html'

class UserLoginView(LoginView):
	template_name = 'login.html'
def attractions(request):
	return render(request,'attractions.html')

def attractions_with_rating():
	# AverageRating is DERIVED (as in the ERD): the average of the ratings on the reviews of
	# bookings whose tour includes the attraction (same idea as TopHouseListView in week 8).
	return Attractions.objects.annotate(
		avg_rating=Avg('listings__booking__review__Rating'),
		review_count=Count('listings__booking__review'),
	)


class AttractionsListView(ListView):
	model = Attractions
	template_name = 'attractions.html'
	context_object_name = 'attractions'
	paginate_by = 6

	def get_queryset(self):
		return attractions_with_rating().order_by('-IsFeatured', 'Name')


class AttractionDetailView(DetailView):
	model = Attractions
	template_name = 'attraction_detail.html'
	context_object_name = 'attraction'

	def get_queryset(self):
		return attractions_with_rating()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		# active tours (of approved guides) that include this attraction
		context['tours'] = Listings.objects.filter(
			Attraction=self.object, ListingsStatus='ACTIVE',
			Guide__tourguideregistration__RegistrationStatus='APPROVED').order_by('TourName')
		# the latest reviews of tours that include this attraction (flagged ones are hidden)
		context['reviews'] = Review.objects.filter(
			Booking__Listing__Attraction=self.object, IsFlagged=False).order_by('-DateSubmitted')[:5]
		return context
	
class TourGuideListView(ListView):
	model = TourGuide
	template_name = 'tour_guide.html'
	context_object_name = 'tourguides'


class BookNowView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'booknow.html'
    login_url = reverse_lazy('OnlyToursApp:login')
    success_url = reverse_lazy('OnlyToursApp:booked')

    def get_context_data(self, **kwargs):
        # data for the live Trip Summary (name, guide, price of each tour)
        context = super().get_context_data(**kwargs)
        listings = Listings.objects.filter(ListingsStatus='ACTIVE').select_related('Guide')
        context['listing_data'] = {
            str(l.pk): {
                'name': l.TourName,
                'guide': f"{l.Guide.first_name} {l.Guide.last_name}",
                'price': float(l.Price),
            }
            for l in listings
        }
        return context

    def form_valid(self, form):
        # fill in the fields the user doesn't type, then let CreateView save
        booking = form.instance
        booking.Customer = get_object_or_404(Customer, pk=self.request.user.pk)
        booking.DateTimeRequested = timezone.now()
        booking.TotalPrice = booking.Listing.Price * booking.NumberOfParticipants
        booking.BookingStatus = 'UNPAID'
       
        return super().form_valid(form)



def booked(request):
	return render(request,'booked.html')

def register(request):
	return render(request,'register.html')

def customerregister(request):
	if request.method == 'POST':
		form = CustomerRegisterForm(request.POST)
		if form.is_valid():
			customer = Customer(username=form.cleaned_data['username'],
			first_name=form.cleaned_data['first_name'],
			last_name=form.cleaned_data['last_name'],
			email=form.cleaned_data['email'],
			PhoneNumber=form.cleaned_data['PhoneNumber'],
			CountryOfOrigin=form.cleaned_data['CountryOfOrigin'],
			PrimaryLanguage=form.cleaned_data['PrimaryLanguage'])
			customer.set_password(form.cleaned_data['password'])
			customer.save()
			return redirect('OnlyToursApp:home')
			
	else:	
		form = CustomerRegisterForm()

	return render(request,'customerregister.html',{'form':form})
def guideregister(request):
	if request.method == 'POST':
		form = GuideRegisterForm(request.POST)
		if form.is_valid():
			guide = TourGuide(username=form.cleaned_data['username'],
			first_name=form.cleaned_data['first_name'],
			last_name=form.cleaned_data['last_name'],
			email=form.cleaned_data['email'],
			PhoneNumber=form.cleaned_data['PhoneNumber'],
			YearsofExperience=form.cleaned_data['YearsofExperience'],
			PrimaryLanguage=form.cleaned_data['PrimaryLanguage'],
			Biography=form.cleaned_data['Biography'])
			guide.set_password(form.cleaned_data['password'])
			guide.save()
			
			registration = TourGuideRegistration(
				Guide=guide, DocumentType=form.cleaned_data['DocumentType'],
				SubmissionDate=timezone.now(), RegistrationStatus='PENDING')
			registration.save()
			auth_login(request, guide)
			return redirect('OnlyToursApp:guide_bookings')

	else:
		form = GuideRegisterForm()
	return render(request,'tourguideregister.html',{'form':form})


def login(request):
	return render(request,'login.html')


@login_required
def guide_listings(request):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    listings = Listings.objects.filter(
    Guide=guide,
    ).prefetch_related('Attraction').order_by(
    '-DateCreated', '-ListingID',
    )

    registrations = TourGuideRegistration.objects.filter(Guide=guide).order_by('-SubmissionDate')
    registration = None
   
    is_approved = TourGuideRegistration.objects.filter( Guide=guide, RegistrationStatus='APPROVED').count() > 0
        
    return render( request,
        'guide_listings.html',
        {'guide': guide, 'listings': listings,
         'is_approved': is_approved},
        )


@login_required
def guide_listing_create(request):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    form = ListingForm(
        request.POST or None,
        instance=Listings(Guide=guide),
    )

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('OnlyToursApp:guide_listings')

    return render(
        request,
        'guide_listing_form.html',
        {'form': form, 'editing': False},
    )


@login_required
def guide_listing_edit(request, listing_id):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    listing = get_object_or_404( Listings, pk=listing_id,Guide=guide,
    )
    form = ListingForm(request.POST or None, instance=listing)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('OnlyToursApp:guide_listings')

    return render( request, 'guide_listing_form.html', {'form': form, 'editing': True, 'listing': listing},
    )

class ReviewView(FormView):
    template_name = 'review.html'
    form_class = ReviewForm
    success_url = reverse_lazy('OnlyToursApp:home')

    def form_valid(self, form):
        # same pattern as customerregister: build the object from cleaned_data, then save it
        review = Review(
            Booking=form.cleaned_data['booking'],
            Rating=form.cleaned_data['Rating'],
            Comment=form.cleaned_data['Comment'],
        )
        review.save()
        return super().form_valid(form)    # redirects to home


@login_required
def guide_bookings(request):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)

    paid_bookings = Booking.objects.filter(
        Listing__Guide=guide,
        BookingStatus='PAID',
    ).select_related('Customer', 'Listing')

    today = timezone.localdate()

    context = { 'guide': guide, 'upcoming': paid_bookings.filter(  TourDate__gte=today
       ).order_by('TourDate', 'TimeSlot'),'past': paid_bookings.filter( TourDate__lt=today
        ).order_by('-TourDate', '-TimeSlot'),  }

    return render(request, 'guide_bookings.html', context)