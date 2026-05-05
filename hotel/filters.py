import django_filters
from django import forms
from .models import Room, Category, Amenity, Booking
from datetime import datetime

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
        method='filter_check_in',
        input_formats=['%d %B, %Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'date-input',
            'placeholder': 'Check In',
            'autocomplete': 'off'})
    )
    
    check_out = django_filters.DateFilter(
        method='filter_check_out',
        input_formats=['%d %B, %Y'],
        widget=forms.DateInput(attrs={
            'class': 'date-input',
            'placeholder': 'Check Out',
            'autocomplete': 'off'})
    )

    capacity = django_filters.NumberFilter(
        field_name='capacity',
        lookup_expr='gte',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Guests'
        })
    )

    def filter_check_in(self, queryset, name, value):
        check_out_str = self.data.get('check_out')
        if value and check_out_str:
            try:
                check_out = datetime.strptime(check_out_str, '%d %B, %Y').date()
            except ValueError: 
                return queryset
            booked_rooms = Booking.objects.filter(
                check_in__lt=check_out,
                check_out__gt=value
            ).values_list('room_id', flat=True)
            return queryset.exclude(id__in=booked_rooms)
        return queryset

    def filter_check_out(self, queryset, name, value):
        return queryset

    class Meta:
        model = Room
        fields = ['category', 'amenities', 'is_available']