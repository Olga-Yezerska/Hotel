from pyexpat.errors import messages

from django.shortcuts import get_object_or_404, redirect, render
from datetime import datetime, timezone
from .models import Room, Booking, Category
from hotel.filters import RoomFilter
from hotel.models import Room
from django.contrib import messages
from django.utils import timezone
from datetime import datetime

def index(request):
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    capacity = request.GET.get('capacity')
    
    # Дані для завантаження сторінки
    categories = Category.objects.all()
    rooms = Room.objects.all()

    # Якщо користувач натиснув кнопку (передав параметри)
    if check_in and check_out:
        is_valid, error_message = validate_dates(check_in, check_out)
        
        if not is_valid:
            #помилка — створюємо повідомлення
            messages.error(request, error_message)
            # Повертаємо ту саму сторінку index.html з повідомленням
            return render(request, 'hotel/index.html', {
                'categories': categories,
                'rooms': rooms
            })
        else:
            #якщо все добре — перекидаємо на сторінку бронювання з даними
            url = f"/booking/?check_in={check_in}&check_out={check_out}&capacity={capacity}"
            return redirect(url)

    return render(request, 'hotel/index.html', {
        'categories': categories,
        'rooms': rooms
    })

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

    if check_in_str or check_out_str: 
        is_valid, error_message = validate_dates(check_in_str, check_out_str)
        if not is_valid:
            from django.contrib import messages
            messages.error(request, error_message)
            return render(request, 'hotel/room-details.html', {
                'room': room,
                'categories': Category.objects.all()
            })
    

    if check_in_str and check_out_str:
        try:

            fmt = '%d %b, %Y' 
            check_in_dt = datetime.strptime(check_in_str, fmt).date()
            check_out_dt = datetime.strptime(check_out_str, fmt).date()
            
            conflict = Booking.objects.filter(
                room=room,
                check_in__lt=check_out_dt,
                check_out__gt=check_in_dt
            ).exists()
            
            is_free = not conflict
        except ValueError:
        
            pass
    
    return render(request, 'hotel/room-details.html', {
        'room': room,
        'is_free': is_free,
        'check_in': check_in_str, 
        'check_out': check_out_str,
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
    
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')

    # Якщо користувач почав вводити дати (натиснув фільтр)
    if check_in or check_out:
        is_valid, error_message = validate_dates(check_in, check_out)
        if not is_valid:
            messages.error(request, error_message)
            return render(request, 'hotel/booking.html', {
                'filter': room_filter,
                'rooms': Room.objects.none(),  
                'categories': Category.objects.all()
            })
    

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
        messages.success(request, f"Дякуємо, {customer_name}! Ваше бронювання номера {room}  успішно створено.")
        
    return render(request, 'hotel/create_booking.html', {
        'room': room,
        'check_in': check_in,
        'check_out': check_out,
        'num_nights': num_nights,    
        'total_price': total_price,  
    })

def validate_dates(check_in_str, check_out_str):
    if not check_in_str or not check_out_str:
        return False, "Будь ласка, оберіть обидві дати."

    try:
        check_in = None
        check_out = None
        
        formats = ['%Y-%m-%d', '%d %b, %Y']
        
        for fmt in formats:
            try:
                if not check_in:
                    check_in = datetime.strptime(check_in_str, fmt).date()
                if not check_out:
                    check_out = datetime.strptime(check_out_str, fmt).date()
            except (ValueError, TypeError):
                continue

        if not check_in or not check_out:
            return False, "Некоректний формат дат. Використовуйте календар."
        
        today = timezone.now().date()

        if check_in < today:
            return False, "Дата заїзду не може бути в минулому."
        
        if check_out <= check_in:
            return False, "Дата виїзду має бути пізніше заїзду."
            
        return True, None

    except Exception as e:
        return False, f"Помилка при обробці дат: {str(e)}"