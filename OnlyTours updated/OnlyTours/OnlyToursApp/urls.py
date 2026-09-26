from django.urls import path
from . import views

app_name = 'OnlyToursApp'

urlpatterns = [
    # Main pages (already designed)
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('attractions/', views.attractions, name='attractions'),
    path('customerregistration/', views.customerReg, name='customerReg'),

    # These destinations are referenced by nav links / buttons in the
    # templates but don't have a real page designed yet. They render
    # a small "coming soon" placeholder for now so every link on the
    # site is clickable and resolves to a real URL instead of a 404.
    # Swap each one out for a real view + template as it gets built.
    path('tour-guide-registration/', views.tourGuideReg, name='tourGuideReg'),
    path('book-now/', views.book_now, name='book_now'),
    path('tour-guide/', views.tour_guide, name='tour_guide'),
    path('login/', views.log_in, name='log_in'),
]
