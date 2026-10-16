from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView
from .forms import BookingForm
from .models import Booking, Listings, Customer

# Create your views here.
class HomeView(TemplateView):
	template_name = 'home.html'

class UserLoginView(LoginView):
	template_name = 'login.html'
def attractions(request):
	return render(request,'attractions.html')
class AttractionsView(TemplateView):
    template_name = 'attractions.html'

def tourguides(request):
	return render(request,'tour_guide.html')


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
        booking.Guide = booking.Listing.Guide
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
