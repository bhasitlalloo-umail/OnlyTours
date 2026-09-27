from django.urls import path
from . import views
app_name = 'OnlyToursApp'
urlpatterns = [
    path('', views.home, name='home'),
    path('attractions/',views.attractions, name='attractions'),
    path('tourguides/', views.tourguides, name='tourguides'),
    path('booknow/',views.booknow, name='booknow'),
    path('booked/', views.booked, name='booked'),
<<<<<<< HEAD
    path('register/', views.register, name='register'),
    path('customerregister/',views.customerregister, name='customerregister'),
    path('guideregister/',views.guideregister, name='guideregister'),
    path('login/',views.login, name='login'),
=======
    path('book-now/',views.booknow,name='booknow'),
    path('', views.homepage, name='homepage'),
    path('tourguide/', views.tourGuide, name='tourGuide'),

>>>>>>> rishabh
    ]
