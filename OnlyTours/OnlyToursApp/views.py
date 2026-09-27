from django.shortcuts import render

# Create your views here.
def home(request):
	return render(request,'home.html')

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
	return render(request,'customerregister.html')

def guideregister(request):
	return render(request,'guideregister.html')

def login(request):
	return render(request,'login.html')
