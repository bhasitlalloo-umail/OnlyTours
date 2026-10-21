from django.views.generic import TemplateView,ListView
from django.contrib.auth.views import LoginView     
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView
from django.shortcuts import render


from django.contrib.auth.decorators import login_required, permission_required

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView

from .models import Booking, Listings, Customer,Attractions,TourGuide

# Create your views here.
class HomeView(TemplateView):
	template_name = 'home.html'

class UserLoginView(LoginView):
	template_name = 'login.html'
def attractions(request):
	return render(request,'attractions.html')
class AttractionsView(TemplateView):
    template_name = 'attractions.html'

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
                'guide': f"{l.Guide.FirstName} {l.Guide.Surname}",
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
		
			return redirect('OnlyToursApp:home')
			
	else:	
		form = GuideRegisterForm()
	return render(request,'tourguideregister.html',{'form':form})

def login(request):
	return render(request,'login.html')


@login_required
@permission_required('OnlyToursApp.add_attractions', raise_exception=True)

def add_attraction(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = AddAttractionForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required 
            attraction=Attractions( Name=form.cleaned_data['name'],
            
            Description = form.cleaned_data["description"],
            Region = form.cleaned_data["region"],
            IsFeatured = form.cleaned_data["is_featured"],
            Longitude = form.cleaned_data["longitude"],
            Latitude = form.cleaned_data["latitude"],
            Distance = form.cleaned_data["distance"],
            DifficultyLevel = form.cleaned_data["difficulty_level"],
            Type = form.cleaned_data["type"],
            DateAdded = form.cleaned_data["date_added"],
            AverageRating=form.cleaned_data["average_rating"], )
			
            attraction.save()

            # redirect to a new URL:
            return redirect('OnlyToursApp:home')
    else:
        form = AddAttractionForm()

    active_class = 'owners'
    context = {
        'form': form,
         'active_class': active_class,    }
	
    return render(request, 'addattractions.html', context)




from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, redirect

from .forms import AddAttractionForm
from .models import Attractions


@login_required
@permission_required('OnlyToursApp.add_attractions', raise_exception=True)
def add_attraction(request):
    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = AddAttractionForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            attraction = Attractions(
                Name=form.cleaned_data['name'],

                Description=form.cleaned_data["description"],
                Region=form.cleaned_data["region"],
                IsFeatured=form.cleaned_data["is_featured"],
                Longitude=form.cleaned_data["longitude"],
                Latitude=form.cleaned_data["latitude"],
                Distance=form.cleaned_data["distance"],
                DifficultyLevel=form.cleaned_data["difficulty_level"],
                Type=form.cleaned_data["type"],
                DateAdded=form.cleaned_data["date_added"],
                AverageRating=form.cleaned_data["average_rating"],
            )
            attraction.save()

            # redirect to a new URL:
            return redirect('OnlyToursApp:home')
    else:
        form = AddAttractionForm()

    active_class = 'owners'
    context = {
        'form': form,
        'active_class': active_class,
    }

    return render(request, 'addattractions.html', context)

@login_required
def guide_listings(request):
	# the guide's own tours (the ERD's "Tour Guide creates Listings")
	guide = get_object_or_404(TourGuide, pk=request.user.pk)
	context = {'guide': guide, 'listings': Listings.objects.filter(Guide=guide).order_by('-DateCreated', '-ListingID')}
	context.update(registration_context(guide))
	return render(request, 'guide_listings.html', context)


@login_required
def guide_listing_create(request):
	guide = get_object_or_404(TourGuide, pk=request.user.pk)
	if not is_approved(guide):
		return redirect('OnlyToursApp:guide_listings')
	# the guide is set on the new listing here, so it can never come from the form
	form = ListingForm(request.POST or None, instance=Listings(Guide=guide))
	if request.method == 'POST' and form.is_valid():
		form.save()
		return redirect('OnlyToursApp:guide_listings')
	return render(request, 'guide_listing_form.html', {'form': form, 'editing': False})

@login_required
def guide_listing_edit(request, listing_id):
	guide = get_object_or_404(TourGuide, pk=request.user.pk)
	# a guide can only open their own listings; anyone else's gives "not found"
	listing = get_object_or_404(Listings, pk=listing_id, Guide=guide)
	if not is_approved(guide):
		return redirect('OnlyToursApp:guide_listings')
	form = ListingForm(request.POST or None, instance=listing)
	if request.method == 'POST' and form.is_valid():
		form.save()
		return redirect('OnlyToursApp:guide_listings')
	return render(request, 'guide_listing_form.html', {'form': form, 'editing': True, 'listing': listing})