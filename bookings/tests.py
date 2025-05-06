from django.test import TestCase
from django.contrib.auth.models import User
from .models import Restaurant, Table, Reservation
from datetime import date, time, timedelta

class RestaurantModelTest(TestCase):
    def test_create_restaurant(self):
        restaurant = Restaurant.objects.create(
            name="Pizza from Damir",
            address="Улица Манаса, 34/1",
            phone="87777777777",
            opening_time=time(10, 0),
            closing_time=time(22, 0)
        )
        self.assertEqual(Restaurant.objects.count(), 1)
        self.assertEqual(restaurant.name, "Pizza from Damir")
        self.assertEqual(str(restaurant), "Pizza from Damir")

class TableModelTest(TestCase):
    def setUp(self):
        self.restaurant = Restaurant.objects.create(
            name="Pizza from Damir",
            opening_time=time(10, 0),
            closing_time=time(22, 0)
        )

    def test_create_table(self):
        table = Table.objects.create(
            restaurant=self.restaurant,
            number="A1",
            capacity=4
        )
        self.assertEqual(Table.objects.count(), 1)
        self.assertEqual(table.number, "A1")
        self.assertEqual(table.capacity, 4)
        self.assertEqual(str(table), "Стол №A1 (вмещает 4 чел.)")

class ReservationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.restaurant = Restaurant.objects.create(
            name="Pizza from Damir",
            opening_time=time(10, 0),
            closing_time=time(22, 0)
        )
        self.table = Table.objects.create(
            restaurant=self.restaurant,
            number="A1",
            capacity=4
        )

    def test_create_reservation(self):
        reservation = Reservation.objects.create(
            user=self.user,
            table=self.table,
            date=date.today() + timedelta(days=1),
            time=time(14, 0),
            guests=2
        )
        self.assertEqual(Reservation.objects.count(), 1)
        self.assertEqual(reservation.status, 'pending')
        self.assertTrue(reservation.is_active())