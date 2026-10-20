from django.urls import path
from .views import HomeView, UserLoginView
from . import views

app_name = 'OnlyToursApp'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('attractions/',views.attractions, name='attractions'),
    path('tourguides/', views.TourGuideListView.as_view(), name='tourguides'),
    path('booknow/',views.BookNowView.as_view(), name='booknow'),
    path('booked/', views.booked, name='booked'),
    path('register/', views.register, name='register'),
    path('customerregister/',views.customerregister, name='customerregister'),
    path('guideregister/',views.guideregister, name='guideregister'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('review/', views.ReviewView.as_view(), name='review'),
    ]
