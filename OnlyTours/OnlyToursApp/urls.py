from django.urls import path
from . import views
app_name = 'OnlyToursApp'
urlpatterns = [
    path('register/', views.register, name='register'),
    path('booked/', views.booked, name='booked'),
    path('', views.homepage, name='homepage'),
    path('tourguide/', views.tourGuide, name='tourGuide'),

    ]
