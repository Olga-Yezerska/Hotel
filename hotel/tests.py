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


# =============================================================================
# 1. MODEL TESTS
# =============================================================================

@pytest.mark.django_db
class TestAmenityModel:
    """Тести для моделі Amenity."""

    def test_str_returns_name(self):
        """__str__ повертає назву зручності."""
        amenity = Amenity.objects.create(name="Wi-Fi")
        assert str(amenity) == "Wi-Fi"

    def test_creation_saves_to_db(self):
        """Зручність успішно зберігається у БД і отримує первинний ключ."""
        amenity = Amenity.objects.create(name="Pool")
        assert amenity.pk is not None
        assert amenity.name == "Pool"


@pytest.mark.django_db
class TestCategoryModel:
    """Тести для моделі Category."""

    def test_str_returns_name(self):
        """__str__ повертає назву категорії."""
        cat = Category.objects.create(name="Deluxe")
        assert str(cat) == "Deluxe"

    def test_creation_with_description(self):
        """Категорія зберігає опис без змін."""
        cat = Category.objects.create(name="Suite", description="Luxury suite rooms")
        assert cat.description == "Luxury suite rooms"

    def test_description_defaults_to_blank(self):
        """Якщо опис не переданий, він дорівнює порожньому рядку."""
        cat = Category.objects.create(name="Budget")
        assert cat.description == ""


@pytest.mark.django_db
class TestRoomModel:
    """Тести для моделі Room."""

    def test_str_returns_name(self, room):
        """__str__ повертає назву кімнати."""
        assert str(room) == "Room 101"

    def test_fields_saved_correctly(self, room):
        """Поля price, capacity та is_available зберігаються коректно."""
        assert room.price == Decimal("150.00")
        assert room.capacity == 2
        assert room.is_available is True

    def test_is_available_defaults_to_true(self, category):
        """is_available = True за замовчуванням при створенні нової кімнати."""
        room = Room.objects.create(
            name="Room 202", category=category, price=Decimal("200.00"), capacity=3
        )
        assert room.is_available is True

    def test_many_to_many_amenities(self, room):
        """До кімнати можна додати кілька зручностей через M2M."""
        wifi = Amenity.objects.create(name="Wi-Fi")
        tv = Amenity.objects.create(name="TV")
        room.amenities.add(wifi, tv)
        assert room.amenities.count() == 2
        assert wifi in room.amenities.all()


@pytest.mark.django_db
class TestBookingModel:
    """Тести для моделі Booking."""

    def test_str_format(self, existing_booking, room, today):
        """__str__ повертає '<назва кімнати> | <check_in> - <check_out>'."""
        check_in = today + timedelta(days=5)
        check_out = today + timedelta(days=10)
        expected = f"{room.name} | {check_in} - {check_out}"
        assert str(existing_booking) == expected

    def test_fields_saved_correctly(self, existing_booking):
        """Поля customer_name, customer_email та room зберігаються коректно."""
        assert existing_booking.customer_name == "Existing Guest"
        assert existing_booking.customer_email == "exist@example.com"

    def test_related_name_from_room(self, existing_booking, room):
        """Бронювання доступне через related_name 'bookings' з об'єкта кімнати."""
        assert existing_booking in room.bookings.all()


# =============================================================================
# 2. VIEW TESTS — доступність сторінок
# =============================================================================

@pytest.mark.django_db
class TestPageAvailability:
    """Перевіряємо, що основні URL повертають очікуваний HTTP-статус."""

    @pytest.mark.parametrize("url_name", ["home", "rooms", "contact", "booking"])
    def test_static_pages_return_200(self, client, url_name):
        """Статичні сторінки без параметрів повертають HTTP 200."""
        response = client.get(reverse(url_name))
        assert response.status_code == 200

    def test_room_details_returns_200(self, client, room):
        """Сторінка деталей конкретної кімнати повертає 200."""
        response = client.get(reverse("room_details", kwargs={"pk": room.pk}))
        assert response.status_code == 200

    def test_room_details_returns_404_for_unknown_pk(self, client):
        """Запит із неіснуючим pk повертає 404."""
        response = client.get(reverse("room_details", kwargs={"pk": 99999}))
        assert response.status_code == 404

    def test_rooms_by_category_returns_200(self, client, category):
        """Фільтрована сторінка кімнат за категорією повертає 200."""
        response = client.get(
            reverse("rooms_by_category", kwargs={"category_id": category.pk})
        )
        assert response.status_code == 200

    def test_create_booking_page_returns_200_with_valid_dates(self, client, room, today):
        """Сторінка бронювання повертає 200, якщо передані коректні дати."""
        check_in = (today + timedelta(days=5)).strftime("%d %B, %Y")
        check_out = (today + timedelta(days=8)).strftime("%d %B, %Y")
        response = client.get(
            reverse("create_booking", kwargs={"pk": room.pk}),
            {"check_in": check_in, "check_out": check_out},
        )
        assert response.status_code == 200


# =============================================================================
# 3. LOGIC & VALIDATION TESTS
# =============================================================================

# -----------------------------------------------------------------------------
# 3a. validate_dates 
# -----------------------------------------------------------------------------

_DATE_FMT = "%Y-%m-%d"


@pytest.mark.parametrize("ci_delta,co_delta,expected_valid,err_keyword", [
    # Коректні майбутні дати
    (3,    6,    True,  None),
    #  Заїзд у минулому
    (-1,   3,    False, "минулому"),
    #  Виїзд раніше заїзду
    (5,    2,    False, "пізніше"),
    #  Виїзд = заїзд (0 ночей)
    (3,    3,    False, None),
    #  Обидва параметри — None
    (None, None, False, None),
    #  Відсутній check_in
    (None, 3,    False, None),
    #  Відсутній check_out
    (3,    None, False, None),
], ids=[
    "valid_future_dates",
    "check_in_in_past",
    "check_out_before_check_in",
    "check_out_equals_check_in",
    "both_none",
    "missing_check_in",
    "missing_check_out",
])
def test_validate_dates(today, ci_delta, co_delta, expected_valid, err_keyword):
    """
    Параметризована перевірка validate_dates для різних комбінацій дат.
    Не потребує БД — перевіряємо лише бізнес-логіку функції.
    """
    check_in = (
        (today + timedelta(days=ci_delta)).strftime(_DATE_FMT)
        if ci_delta is not None else None
    )
    check_out = (
        (today + timedelta(days=co_delta)).strftime(_DATE_FMT)
        if co_delta is not None else None
    )

    is_valid, error = validate_dates(check_in, check_out)

    assert is_valid is expected_valid
    if err_keyword:
        assert err_keyword in error
    if expected_valid:
        assert error is None


def test_validate_dates_invalid_string_format(today):
    """Некоректний рядок формату дати → is_valid=False."""
    is_valid, _ = validate_dates("not-a-date", "also-not-a-date")
    assert is_valid is False


# -----------------------------------------------------------------------------
# 3b. Розрахунок ціни та ночей у create_booking
# -----------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.parametrize("nights", [1, 3, 7, 14], ids=["1_night", "3_nights", "7_nights", "14_nights"])
def test_price_calculation_for_different_nights(client, room, today, nights):
    """
    num_nights та total_price у контексті відповідають заданій кількості ночей.
    Тестуємо 1, 3, 7 та 14 ночей.
    """
    check_in = (today + timedelta(days=5)).strftime("%d %B, %Y")
    check_out = (today + timedelta(days=5 + nights)).strftime("%d %B, %Y")
    response = client.get(
        reverse("create_booking", kwargs={"pk": room.pk}),
        {"check_in": check_in, "check_out": check_out},
    )
    assert response.context["num_nights"] == nights
    assert response.context["total_price"] == room.price * nights


@pytest.mark.django_db
def test_create_booking_redirects_to_rooms_on_bad_dates(client, room):
    """При некоректному форматі дат — редирект 302 на сторінку rooms."""
    response = client.get(
        reverse("create_booking", kwargs={"pk": room.pk}),
        {"check_in": "garbage", "check_out": "garbage"},
    )
    assert response.status_code == 302
    assert response["Location"].endswith(reverse("rooms"))


# -----------------------------------------------------------------------------
# 3c. Конфлікти бронювань 
# -----------------------------------------------------------------------------

# existing_booking займає дні: check_in=today+5, check_out=today+10
@pytest.mark.django_db
@pytest.mark.parametrize("new_ci,new_co,expect_conflict", [
    #  Вільно — нові дати не перетинаються
    (11, 15, False),  # повністю після
    (1,  4,  False),  # повністю до
    #  Конфлікт — різні типи перекриття
    (3,  7,  True),   # перекриття початку (+3…+7 перекриває +5)
    (6,  9,  True),   # нові дати всередині існуючого
    (8,  12, True),   # перекриття кінця (+8…+12 перекриває +10)
    (3,  13, True),   # нові дати огортають існуюче
], ids=[
    "free_after_existing",
    "free_before_existing",
    "conflict_overlap_start",
    "conflict_fully_inside",
    "conflict_overlap_end",
    "conflict_wraps_existing",
])
def test_booking_conflict_scenarios(
    existing_booking, room, today, new_ci, new_co, expect_conflict
):
    """
    Параметризована перевірка алгоритму виявлення конфліктів (overlap).
    Алгоритм: нові дати конфліктують, якщо new_ci < exist_co AND new_co > exist_ci.
    """
    conflict = Booking.objects.filter(
        room=room,
        check_in__lt=today + timedelta(days=new_co),
        check_out__gt=today + timedelta(days=new_ci),
    ).exists()
    assert conflict is expect_conflict


# =============================================================================
# 4. INTEGRATION / FORM TESTS
# =============================================================================

@pytest.mark.django_db
class TestCreateBookingView:
    """Інтеграційні тести для view create_booking (POST/GET)."""

    def test_post_creates_booking_record(self, client, booking_url):
        """POST зберігає новий запис Booking у БД."""
        client.post(booking_url, {
            "customer_name": "John Smith",
            "customer_email": "john@example.com",
            "customer_phone": "+380671234567",
        })
        assert Booking.objects.count() == 1
        assert Booking.objects.first().customer_name == "John Smith"

    def test_post_booking_linked_to_correct_room(self, client, room, booking_url):
        """Створене бронювання прив'язане до правильної кімнати."""
        client.post(booking_url, {
            "customer_name": "Room Checker",
            "customer_email": "room@example.com",
            "customer_phone": "+380000000003",
        })
        assert Booking.objects.first().room == room

    def test_post_success_message_contains_customer_name(self, client, booking_url):
        """Після POST повідомлення про успіх містить ім'я клієнта."""
        response = client.post(booking_url, {
            "customer_name": "Anna Kovalenko",
            "customer_email": "anna@example.com",
            "customer_phone": "+380501234567",
        })
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert "Anna Kovalenko" in str(messages[0])

    def test_post_success_message_contains_room_name(self, client, room, booking_url):
        """Після POST повідомлення містить назву заброньованої кімнати."""
        response = client.post(booking_url, {
            "customer_name": "Test User",
            "customer_email": "test@example.com",
            "customer_phone": "+380000000001",
        })
        messages = list(get_messages(response.wsgi_request))
        assert room.name in str(messages[0])

    def test_post_success_message_contains_thank_you(self, client, booking_url):
        """Повідомлення після бронювання містить 'Дякуємо'."""
        response = client.post(booking_url, {
            "customer_name": "Thank You Tester",
            "customer_email": "ty@example.com",
            "customer_phone": "+380000000009",
        })
        messages = list(get_messages(response.wsgi_request))
        assert "Дякуємо" in str(messages[0])

    def test_get_does_not_create_booking(self, client, booking_url):
        """GET-запит на сторінку не створює запис у БД."""
        client.get(booking_url)
        assert Booking.objects.count() == 0

    def test_booking_stores_correct_dates(self, client, booking_url, today):
        """Дати у створеному бронюванні відповідають датам із URL (+10 та +13)."""
        client.post(booking_url, {
            "customer_name": "Date Checker",
            "customer_email": "date@example.com",
            "customer_phone": "+380000000002",
        })
        booking = Booking.objects.first()
        assert booking.check_in == today + timedelta(days=10)
        assert booking.check_out == today + timedelta(days=13)


@pytest.mark.django_db
class TestHomePageRedirects:
    """Тести редиректів та повідомлень про помилки на головній сторінці."""

    @pytest.mark.parametrize("ci_delta,co_delta", [
        (2, 5),
        (1, 10),
    ], ids=["short_stay", "long_stay"])
    def test_valid_dates_redirect_to_booking(self, client, today, ci_delta, co_delta):
        """Коректні дати → редирект 302 на /booking/."""
        check_in = (today + timedelta(days=ci_delta)).strftime("%Y-%m-%d")
        check_out = (today + timedelta(days=co_delta)).strftime("%Y-%m-%d")
        response = client.get(
            reverse("home"),
            {"check_in": check_in, "check_out": check_out, "capacity": 2},
        )
        assert response.status_code == 302
        assert "/booking/" in response["Location"]

    @pytest.mark.parametrize("ci_delta,co_delta", [
        (-1, 3),  # заїзд у минулому
        (5,  2),  # виїзд до заїзду
        (3,  3),  # виїзд = заїзд
    ], ids=["past_check_in", "checkout_before_checkin", "checkout_equals_checkin"])
    def test_invalid_dates_stay_on_home_with_error(self, client, today, ci_delta, co_delta):
        """Невалідні дати → статус 200 на home та непорожнє повідомлення помилки."""
        check_in = (today + timedelta(days=ci_delta)).strftime("%Y-%m-%d")
        check_out = (today + timedelta(days=co_delta)).strftime("%Y-%m-%d")
        response = client.get(
            reverse("home"),
            {"check_in": check_in, "check_out": check_out},
        )
        assert response.status_code == 200
        assert len(list(get_messages(response.wsgi_request))) > 0


@pytest.mark.django_db
class TestRoomDetailsAvailability:
    """Тести поля is_free у контексті сторінки room_details."""

    @pytest.mark.parametrize("ci_delta,co_delta,expected_free", [
        # Вільно — не перекривається з existing_booking (+5…+10)
        (11, 14, True),
        (1,  4,  True),
        # Зайнято — різні типи перекриття
        (6,  9,  False),
        (3,  7,  False),
        (8,  12, False),
    ], ids=["free_after", "free_before", "overlap_inside", "overlap_start", "overlap_end"])
    def test_is_free_with_dates(
        self, client, room, today, existing_booking, ci_delta, co_delta, expected_free
    ):
        """
        is_free у контексті room_details коректно відображає доступність.
        Формат дат для цього view: '%d %b, %Y' (наприклад '12 May, 2026').
        """
        check_in = (today + timedelta(days=ci_delta)).strftime("%d %b, %Y")
        check_out = (today + timedelta(days=co_delta)).strftime("%d %b, %Y")
        response = client.get(
            reverse("room_details", kwargs={"pk": room.pk}),
            {"check_in": check_in, "check_out": check_out},
        )
        assert response.context["is_free"] is expected_free

    def test_is_free_is_none_without_dates(self, client, room):
        """is_free = None, якщо дати не передані у запиті."""
        response = client.get(reverse("room_details", kwargs={"pk": room.pk}))
        assert response.context["is_free"] is None