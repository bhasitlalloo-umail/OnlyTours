from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('booked/', views.booked, name='booked'),
    ]
