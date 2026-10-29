from django.urls import path
from .views import HomeView
from . import views

app_name = 'OnlyToursApp'
urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('attractions/', views.AttractionsListView.as_view(), name='attractions'),
    path('attractions/<int:pk>/', views.AttractionDetailView.as_view(), name='attraction_detail'),    
    path('tourguides/', views.TourGuideListView.as_view(), name='tourguides'),
    path('booknow/',views.BookNowView.as_view(), name='booknow'),
    path('booked/<int:booking_id>/', views.booked, name='booked'),
    path('register/', views.register, name='register'),
    path('customerregister/',views.customerregister, name='customerregister'),
    path('guideregister/', views.GuideRegisterView.as_view(), name='guideregister'),


    path('guide/listings/', views.guide_listings, name='guide_listings'),
    path('guide/listings/new/', views.guide_listing_create, name='guide_listing_create'),
    path('guide/listings/<int:listing_id>/edit/', views.guide_listing_edit, name='guide_listing_edit'),
    path('review/<int:booking_id>/', views.ReviewView.as_view(), name='review'),
path('guide/bookings/', views.guide_bookings, name='guide_bookings'),
    path('guide/bookings/<int:booking_id>/accept/', views.guide_booking_accept, name='guide_booking_accept'),
    path('guide/bookings/<int:booking_id>/decline/', views.guide_booking_decline, name='guide_booking_decline'),
    path('guide/bookings/<int:booking_id>/cancel/', views.guide_booking_cancel, name='guide_booking_cancel'),
    path('guide/reviews/', views.guide_reviews, name='guide_reviews'),
    path('guide/reviews/<int:review_id>/respond/', views.guide_review_respond, name='guide_review_respond'),

    path('trips/', views.my_trips, name='my_trips'),
    path('pay/<int:booking_id>/', views.pay, name='pay'),
    ]
