from django.views.generic import TemplateView,ListView
from django.contrib.auth.views import LoginView     
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import CreateView, DetailView, FormView
from django.db.models import Avg, Count
from .forms import BookingForm, ReviewForm
from .models import Booking, Listings, Customer, Attractions, TourGuide, Review,TourGuideRegistration,Payment
from django.contrib.auth import login as auth_login

from django.http import HttpResponse, HttpResponseRedirect
from . import payments
from django.utils.decorators import method_decorator


# Create your views here.
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured'] = Attractions.objects.filter(IsFeatured=True).order_by('Name')[:3]
        return context


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
    login_url = reverse_lazy('login')
    
    def get_success_url(self):
        # the guide has to accept first, so the customer waits on their trips page
        return reverse('OnlyToursApp:my_trips')


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
        booking.BookingStatus = 'PENDING'
       
        return super().form_valid(form)



def booked(request,booking_id):
	customer = get_object_or_404(Customer, pk=request.user.pk)
	booking = get_object_or_404(Booking.objects.select_related('Listing', 'Listing__Guide'), pk=booking_id, Customer=customer)
	if booking.BookingStatus != 'PAID':
		return redirect('OnlyToursApp:pay', booking_id=booking.pk)
	paid_payments = Payment.objects.filter(BookingID=booking, PaymentStatus='PAID').order_by('-TransactionDate')
	payment = None
	if len(paid_payments) > 0:
		payment = paid_payments[0]
	return render(request, 'booked.html', {'booking': booking, 'payment': payment})

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


@method_decorator(login_required(login_url='login'), name='dispatch')
class ReviewView(FormView):
    template_name = 'review.html'
    form_class = ReviewForm
    success_url = reverse_lazy('OnlyToursApp:home')

    def dispatch(self, request, *args, **kwargs):
        # login_required has already run, so request.user is logged in here.
        customer = get_object_or_404(Customer, pk=request.user.pk)
        # only the customer who made the booking can review it
        self.booking = get_object_or_404(
            Booking.objects.select_related('Listing', 'Customer'),
            pk=kwargs['booking_id'], Customer=customer)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['booking'] = self.booking
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['booking'] = self.booking
        return context

    def form_valid(self, form):
        review = Review(
            Booking=self.booking,
            Rating=form.cleaned_data['Rating'],
            Comment=form.cleaned_data['Comment'],
        )
        review.save()
        return super().form_valid(form)    # redirects to home

@login_required
def guide_bookings(request):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)

    today = timezone.localdate()

    # all the booking requests for this guide's tours
    bookings = Booking.objects.filter(Listing__Guide=guide).select_related('Customer', 'Listing')

    # requests waiting for the guide to accept or decline
    pending = bookings.filter(BookingStatus='PENDING').order_by('DateTimeRequested')
    # accepted or paid tours still to come, the guide can cancel these
    upcoming = bookings.filter(BookingStatus__in=['ACCEPTED', 'PAID'], TourDate__gte=today).order_by('TourDate', 'TimeSlot')
    past = bookings.filter(BookingStatus__in=['ACCEPTED', 'PAID'], TourDate__lt=today).order_by('-TourDate', '-TimeSlot')
    # requests that were declined or cancelled
    closed = bookings.filter(BookingStatus__in=['DECLINED', 'CANCELLED']).order_by('-TourDate', '-TimeSlot')

    context = {'guide': guide, 'pending': pending, 'upcoming': upcoming, 'past': past, 'closed': closed}

    return render(request, 'guide_bookings.html', context)


@login_required
def guide_booking_accept(request, booking_id):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    # a guide can only answer requests for their own tours; anyone else's gives "not found"
    booking = get_object_or_404(Booking, pk=booking_id, Listing__Guide=guide)
    if request.method == 'POST' and booking.BookingStatus == 'PENDING':
        booking.BookingStatus = 'ACCEPTED'
        booking.save()
    return HttpResponseRedirect(reverse('OnlyToursApp:guide_bookings'))


@login_required
def guide_booking_decline(request, booking_id):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    booking = get_object_or_404(Booking, pk=booking_id, Listing__Guide=guide)
    if request.method == 'POST' and booking.BookingStatus == 'PENDING':
        booking.BookingStatus = 'DECLINED'
        booking.save()
    return HttpResponseRedirect(reverse('OnlyToursApp:guide_bookings'))


@login_required
def guide_booking_cancel(request, booking_id):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    booking = get_object_or_404(Booking, pk=booking_id, Listing__Guide=guide)
    # only accepted (or already paid) bookings can be cancelled
    if request.method == 'POST' and booking.BookingStatus in ['ACCEPTED', 'PAID']:
        booking.BookingStatus = 'CANCELLED'
        booking.save()
    return HttpResponseRedirect(reverse('OnlyToursApp:guide_bookings'))

@login_required
def guide_reviews(request):
    # reviews of this guide's own tours, newest first
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    reviews = Review.objects.filter(Booking__Listing__Guide=guide).select_related(
        'Booking__Listing', 'Booking__Customer').order_by('-DateSubmitted')
    return render(request, 'guide_reviews.html', {'guide': guide, 'reviews': reviews})


@login_required
def guide_review_respond(request, review_id):
    guide = get_object_or_404(TourGuide, pk=request.user.pk)
    # a guide can only answer reviews of their own tours; anyone else's gives "not found"
    review = get_object_or_404(Review, pk=review_id, Booking__Listing__Guide=guide)
    if request.method == 'POST':
        form = GuideResponseForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
    return redirect('OnlyToursApp:guide_reviews')


@login_required
def my_trips(request):
	# the customer's own bookings, with what they can do next (pay, receipt, review)
	customer = get_object_or_404(Customer, pk=request.user.pk)
	today = timezone.localdate()
	trips = Booking.objects.filter(Customer=customer).select_related('Listing', 'Listing__Guide').order_by('-TourDate', '-BookingID')
	for booking in trips:
		reviews = Review.objects.filter(Booking=booking)
		booking.my_review = None
		if len(reviews) > 0:
			booking.my_review = reviews[0]
		booking.can_review = booking.BookingStatus == 'PAID' and booking.TourDate < today and booking.my_review is None
	return render(request, 'my_trips.html', {'trips': trips})

@login_required
def pay(request, booking_id):
    # only the customer who made the booking can pay for it
    customer = get_object_or_404(Customer, pk=request.user.pk)
    booking = get_object_or_404(Booking.objects.select_related('Listing', 'Listing__Guide'), pk=booking_id, Customer=customer)

    if booking.BookingStatus != 'ACCEPTED' and booking.BookingStatus != 'UNPAID':
        return redirect('OnlyToursApp:my_trips')
    decline_message = ''
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            number = form.cleaned_data['card_number']
            payment = Payment(
                BookingID=booking,
                Amount=booking.TotalPrice,  # always the price saved on the booking, never from the form
                Currency='MUR',
                ExchangeRate=1,
                TransactionDate=timezone.now(),
                PaymentMethod=f'Card ending {number[-4:]}',
            )
            if number in payments.DECLINED_TEST_CARDS:
                payment.PaymentStatus = 'FAILED'
                payment.save()
                decline_message = payments.DECLINED_TEST_CARDS[number]
            else:
                payment.PaymentStatus = 'PAID'
                payment.save()
                booking.BookingStatus = 'PAID'
                booking.save()
                return redirect('OnlyToursApp:booked', booking_id=booking.pk)
    else:
        form = PaymentForm()

    return render(request, 'payment.html', {'form': form, 'booking': booking, 'decline_message': decline_message})
