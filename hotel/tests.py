from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.messages import get_messages
from django.urls import reverse
from django.utils import timezone

from .models import Amenity, Booking, Category, Room
from .views import validate_dates


# =============================================================================
# ФІКСТУРИ 
# =============================================================================

@pytest.fixture
def today():
    """Повертає поточну дату (без часу)."""
    return timezone.now().date()


@pytest.fixture
def category(db):
    """Базова категорія кімнат."""
    return Category.objects.create(name="Standard", description="Standard rooms")


@pytest.fixture
def room(category):
    """Базова кімната, прив'язана до фікстури category."""
    return Room.objects.create(
        name="Room 101",
        category=category,
        price=Decimal("150.00"),
        capacity=2,
        is_available=True,
    )


@pytest.fixture
def existing_booking(room, today):
    """
    Готове бронювання room на дні +5…+10 від сьогодні.
    Використовується у тестах конфліктів та доступності.
    """
    return Booking.objects.create(
        room=room,
        check_in=today + timedelta(days=5),
        check_out=today + timedelta(days=10),
        guests=2,
        customer_name="Existing Guest",
        customer_email="exist@example.com",
        customer_phone="+380000000000",
    )


@pytest.fixture
def booking_url(room, today):
    """
    Повертає URL create_booking із вбудованими query-параметрами
    check_in (+10 днів) та check_out (+13 днів).
    """
    check_in = (today + timedelta(days=10)).strftime("%d %B, %Y")
    check_out = (today + timedelta(days=13)).strftime("%d %B, %Y")
    base = reverse("create_booking", kwargs={"pk": room.pk})
    return f"{base}?check_in={check_in}&check_out={check_out}"


