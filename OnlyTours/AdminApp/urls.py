from django.urls import path
from . import views

app_name = 'AdminApp'

urlpatterns = [
    path('', views.index, name='index'),
]