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

    path('attractions/add/', views.add_attraction, name='add-attraction'),
        path('guide/listings/', views.guide_listings, name='guide_listings'),
    path('guide/listings/new/', views.guide_listing_create, name='guide_listing_create'),
    path('guide/listings/<int:listing_id>/edit/', views.guide_listing_edit, name='guide_listing_edit'),
    ]
