from django.shortcuts import get_object_or_404, render
from datetime import datetime
from .models import Room, Booking, Category
from hotel.filters import RoomFilter
from hotel.models import Room

def index(request):
    return render(request, 'hotel/index.html', {'categories': Category.objects.all()})

def about(request):
    return render(request, 'hotel/about-us.html', {'categories': Category.objects.all()})

def blog(request):
    return render(request, 'hotel/blog.html', {'categories': Category.objects.all()})

def blog_details(request):
    return render(request, 'hotel/blog-details.html', {'categories': Category.objects.all()})

def contact(request):
    return render(request, 'hotel/contact.html', {'categories': Category.objects.all()})

def rooms(request):
    room_filter = RoomFilter(request.GET, queryset=Room.objects.all())
    return render(request, 'hotel/rooms.html', {
        'filter': room_filter,
        'categories': Category.objects.all()
    })

def room_details(request, pk):
    room = get_object_or_404(Room, pk=pk)
    is_free = None
    
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')
    
    if check_in_str and check_out_str:
        try:
            check_in = datetime.strptime(check_in_str, '%d %B, %Y').date()
            check_out = datetime.strptime(check_out_str, '%d %B, %Y').date()
            
            conflict = Booking.objects.filter(
                room=room,
                check_in__lt=check_out,
                check_out__gt=check_in
            ).exists()
            
            is_free = not conflict
        except ValueError:
            pass
    
    return render(request, 'hotel/room-details.html', {
        'room': room,
        'is_free': is_free,
        'categories': Category.objects.all()
    })

def rooms_by_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    rooms = Room.objects.filter(category=category)
    return render(request, 'hotel/rooms.html', {
        'filter': RoomFilter(request.GET, queryset=rooms),
        'category': category,
        'categories': Category.objects.all()
    })

def booking_view(request):
    room_filter = RoomFilter(request.GET, queryset=Room.objects.all())
    return render(request, 'hotel/booking.html', {
        'filter': room_filter,
        'rooms': room_filter.qs,
        'categories': Category.objects.all()
    })

def create_booking(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'hotel/create_booking.html', {'room': room})