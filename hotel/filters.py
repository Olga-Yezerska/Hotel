import django_filters
from .models import Room, Category, Amenity

class RoomFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )

    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all()
    )

    amenities = django_filters.ModelMultipleChoiceFilter(
        queryset=Amenity.objects.all()
    )

    class Meta:
        model = Room
        fields = ['category', 'amenities', 'is_available']