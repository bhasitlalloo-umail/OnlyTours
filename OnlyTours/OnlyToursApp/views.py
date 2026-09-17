from django.shortcuts import render

# Create your views here.

def register(request):
	return render(request,'register.html')

def admin(request):
	return render(request,'admin.html')