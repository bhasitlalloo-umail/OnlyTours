from django.views.generic import TemplateView
from django.contrib.auth.views import LoginView
from .forms import *
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
class HomeView(TemplateView):
	template_name = 'home.html'

class UserLoginView(LoginView):
	template_name = 'login.html'
def attractions(request):
	return render(request,'attractions.html')

def tourguides(request):
	return render(request,'tour_guide.html')

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

def tourguideregister(request):
	return render(request,'tourguideregister.html')

def login(request):
	return render(request,'login.html')
