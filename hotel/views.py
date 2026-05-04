from django.shortcuts import get_object_or_404, redirect, render
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

def room_details_booking(request, pk):
    room = get_object_or_404(Room, pk=pk)
    
    return render(request, 'hotel/room-details-booking.html', {
        'room': room,
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
    check_in_str = request.GET.get('check_in')
    check_out_str = request.GET.get('check_out')

    # Оголошуємо змінні заздалегідь
    num_nights = 0
    total_price = 0

    try:
        check_in = datetime.strptime(check_in_str, '%d %B, %Y').date()
        check_out = datetime.strptime(check_out_str, '%d %B, %Y').date()
        
        num_nights = (check_out - check_in).days
        if num_nights < 1: 
            num_nights = 1
        
        total_price = room.price * num_nights
        
    except (ValueError, TypeError):
        return redirect('rooms')

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        
        Booking.objects.create(
            room=room,
            check_in=check_in,
            check_out=check_out,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            guests=room.capacity
        )
        return redirect('home')


    return render(request, 'hotel/create_booking.html', {
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'num_nights': num_nights,    # Переконайся, що ці рядки є
        'total_price': total_price,  # Переконайся, що ці рядки є
    })