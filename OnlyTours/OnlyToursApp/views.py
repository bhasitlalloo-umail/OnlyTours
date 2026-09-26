from django.shortcuts import render

# Create your views here.

def register(request):
	return render(request,'register.html')

def booked(request):
	return render(request,'booked.html')