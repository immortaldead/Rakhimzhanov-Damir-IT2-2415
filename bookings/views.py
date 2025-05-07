from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Restaurant, Table, Reservation
from .forms import ReservationForm


def home(request):
    """Главная страница приложения"""
    return render(request, 'bookings/home.html')


def restaurant_list(request):
    """Отображает список всех ресторанов"""
    restaurants = Restaurant.objects.all()
    return render(request, 'bookings/restaurant_list.html', {
        'restaurants': restaurants
    })


def table_list(request, restaurant_id):
    """Отображает список столов в конкретном ресторане"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'bookings/table_list.html', {
        'restaurant': restaurant,
        'tables': tables
    })


@login_required
def create_reservation(request):
    """Создание новой брони (только для авторизованных пользователей)"""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.save()
            return redirect('profile')
    else:
        form = ReservationForm()
    return render(request, 'bookings/reservation_form.html', {'form': form})


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Авторизация пользователя"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'registration/login.html')


def logout_view(request):
    """Выход из системы"""
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    """Профиль пользователя с списком его бронирований"""
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'accounts/profile.html', {
        'reservations': reservations
    })


def test_view(request):
    """Тестовая страница для проверки работы"""
    return HttpResponse("<h1 style='color:green'>Тест успешен!</h1>")