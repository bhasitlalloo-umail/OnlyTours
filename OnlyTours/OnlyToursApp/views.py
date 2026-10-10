from django.shortcuts import render
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import ListView
from .models import TourGuide

# Create your views here.
def home(request):
	return render(request,'home.html')

def attractions(request):
	return render(request,'attractions.html')

class TourGuideListView(ListView):
	model = TourGuide
	template_name = 'tour_guide.html'
	context_object_name = 'tourguides'

def booknow(request):
	return render(request,'booknow.html')

def booked(request):
	return render(request,'booked.html')

def register(request):
	return render(request,'register.html')

def customerregister(request):
	if request.method == 'POST':
		form = RegisterForm(request.POST)
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
		form = RegisterForm()

	return render(request,'customerregister.html',{'form':form})

def guideregister(request):
	return render(request,'guideregister.html')

def login(request):
	return render(request,'login.html')
