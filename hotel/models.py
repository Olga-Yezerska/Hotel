from django.db import models

# Create your models here.

class Amenity(models.Model):
    name = models.CharField(max_length = 100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length = 100)
    description = models.TextField(blank = True)

    def __str__(self):
        return self.name
    
class Room(models.Model):
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
    name = models.CharField(max_length=50)
    description = models.TextField()
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    photo = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.name
