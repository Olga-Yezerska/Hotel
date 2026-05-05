from django.db import models

# Create your models here.

class Amenity(models.Model):
    """
    Таблиця зручностей
    """
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

class Category(models.Model):
    """
    Таблиця категорії кімнат (Стандарт, Люкс і тд)
    """
    name = models.CharField(max_length = 100)
    description = models.TextField(blank = True)

    def __str__(self):
        return self.name
    
class Room(models.Model):
    """
    Таблиця кімнат

    category: ForeignKey — багато кімнат до однієї категорії
    amenities: ManyToManyField — кімната може мати кілька зручностей, і одна зручність може бути у кількох кімнатах.
    """
    name = models.CharField(max_length = 50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='rooms')
    amenities = models.ManyToManyField(Amenity, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    capacity = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to='rooms/', blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class HotelInfo(models.Model):
    """
    Загальна інформація про готель
    """
    name = models.CharField(max_length=50)
    description = models.TextField()
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    photo = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Booking(models.Model):
    """
    Таблиця інформації про бронювання кімнати
 
    room: ForeignKey — бронювання прив'язане до конкретної кімнати
    """
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField()

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.room.name} | {self.check_in} - {self.check_out}"
