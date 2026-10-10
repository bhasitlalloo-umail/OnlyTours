from django.urls import path
from . import views
app_name = 'OnlyToursApp'
urlpatterns = [
    path('', views.home, name='home'),
    path('attractions/',views.attractions, name='attractions'),
    path('tourguides/', views.TourGuideListView.as_view(), name='tourguides'),
    path('booknow/',views.booknow, name='booknow'),
    path('booked/', views.booked, name='booked'),
    path('register/', views.register, name='register'),
    path('customerregister/',views.customerregister, name='customerregister'),
    path('guideregister/',views.guideregister, name='guideregister'),
    path('login/',views.login, name='login'),
    ]
