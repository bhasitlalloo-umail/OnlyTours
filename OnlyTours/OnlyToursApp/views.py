from django.shortcuts import render

# Create your views here.

def register(request):
	return render(request,'register.html')

def booked(request):
	return render(request,'booked.html')

def homepage(request):
	return render(request,'homepage.html')

def tourGuide(request):
	return render(request,'tour_guide.html')


def attractions(request):
    return render(request, 'attractions.html')


def customerReg(request):
    return render(request, 'customerReg.html')
