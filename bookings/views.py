from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Restaurant, Table, Reservation

def home(request):
    """Главная страница"""
    return render(request, 'bookings/home.html')

def restaurant_list(request):
    """Список всех ресторанов"""
    restaurants = Restaurant.objects.all()
    return render(request, 'bookings/restaurant_list.html', {
        'restaurants': restaurants
    })

def table_list(request, restaurant_id):
    """Список столов в конкретном ресторане"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'bookings/table_list.html', {
        'restaurant': restaurant,
        'tables': tables
    })

def create_reservation(request):
    """Создание новой брони"""
    return HttpResponse("Форма бронирования будет здесь")

def test_view(request):
    """Тестовая страница"""
    return HttpResponse("<h1 style='color:green'>Тест успешен!</h1>")