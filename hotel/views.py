from django.shortcuts import render

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
    return render(request, 'hotel/rooms.html')

def room_details(request):
    return render(request, 'hotel/room-details.html')