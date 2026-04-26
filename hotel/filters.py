import django_filters
from django import forms
from .models import Room, Category, Amenity

class RoomFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Price From',
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Min price...'
        })
    )

    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Price To',
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Max price...'
        })
    )

    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        empty_label="All Categories",
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    amenities = django_filters.ModelMultipleChoiceFilter(
        queryset=Amenity.objects.all(),
        # Використовуємо CheckboxSelectMultiple, якщо хочете галочки, 
        # або SelectMultiple з класом для списку
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'amenity-checkbox'
        })
    )

    is_available = django_filters.BooleanFilter(
        widget=forms.Select(choices=[
            ('', 'Any Status'),
            (True, 'Available Only'),
            (False, 'Occupied'),
        ], attrs={'class': 'form-control'})
    )

    check_in = django_filters.DateFilter(
        input_formats=['%d %B %Y'], # Формат для "29 April 2026"
        widget=forms.DateInput(attrs={
            'class': 'date-input', 
            'placeholder': 'Check In',
            'autocomplete': 'off'
        })
    )
    
    check_out = django_filters.DateFilter(
        input_formats=['%d %B %Y'], # Формат для "29 April 2026"
        widget=forms.DateInput(attrs={
            'class': 'date-input', 
            'placeholder': 'Check Out',
            'autocomplete': 'off'
        })
    )

    capacity = django_filters.NumberFilter(
        field_name='capacity',
        lookup_expr='gte',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Guests'
        })
    )
    class Meta:
        model = Room
        fields = ['category', 'amenities', 'is_available']