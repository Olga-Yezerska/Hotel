from django.shortcuts import get_object_or_404, render

from hotel.filters import RoomFilter
from hotel.models import Room

def index(request):
    return render(request, 'hotel/index.html')

def about(request):
    return render(request, 'hotel/about-us.html')

def blog(request):
    return render(request, 'hotel/blog.html')

def blog_details(request):
    return render(request, 'hotel/blog-details.html')

def contact(request):
    return render(request, 'hotel/contact.html')

def rooms(request):
    rooms = Room.objects.all()
    return render(request, 'hotel/rooms.html', {'rooms': rooms})

def room_details(request):
    return render(request, 'hotel/room-details.html')   

def booking_view(request):
    queryset = Room.objects.all()
    room_filter = RoomFilter(request.GET, queryset=queryset)
    
    context = {
        'filter': room_filter,
        'rooms': room_filter.qs,
    }
    return render(request, 'hotel/booking.html', context)