from django.contrib import admin

# Register your models here.

from .models import Amenity, Category, Room, HotelInfo

admin.site.register(Amenity)
admin.site.register(Category)
admin.site.register(Room)
admin.site.register(HotelInfo)
