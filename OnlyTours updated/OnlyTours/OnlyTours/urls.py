"""
OnlyTours project URL configuration.

Everything user-facing lives in OnlyToursApp; this file just wires
the admin site and hands everything else off to that app.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('OnlyToursApp.urls', namespace='OnlyToursApp')),
]
