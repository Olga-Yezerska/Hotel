"""
URL configuration for hotel_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hotel import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='home'),
    path('contact/', views.contact, name='contact'),
    path('rooms/', views.rooms, name='rooms'),
    path('booking/', views.booking_view, name='booking'),
    path('rooms/<int:pk>/', views.room_details, name='room_details'),
    path('roomsbooking/<int:pk>/', views.room_details_booking, name='room_details_booking'),
    path('rooms/category/<int:category_id>/', views.rooms_by_category, name='rooms_by_category'),
    path('rooms/<int:pk>/book/', views.create_booking, name='create_booking'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)