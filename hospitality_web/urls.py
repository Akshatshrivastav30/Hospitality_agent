from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Main admin interface
    path('admin/', admin.site.urls),
    
    # This connects your dashboard app to the root URL
    # It tells Django: "For the home page, look at dashboard/urls.py"
    path('', include('dashboard.urls')),
]