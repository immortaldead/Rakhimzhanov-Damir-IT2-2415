from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from .models import Restaurant, Table, Reservation
from .forms import ReservationForm, RestaurantForm, TableForm


def test_view(request):
    """Тестовая страница для проверки работы"""
    return HttpResponse("<h1 style='color:green'>Тест успешен!</h1>")


def table_detail(request, pk):
    """Детальный просмотр стола"""
    table = get_object_or_404(Table, pk=pk)
    return render(request, 'bookings/table_detail.html', {
        'table': table
    })


def table_create(request, restaurant_id):
    """Создание нового стола для ресторана"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.restaurant = restaurant
            table.save()
            return redirect('table_list', restaurant_id=restaurant.id)
    else:
        form = TableForm()

    return render(request, 'bookings/table_form.html', {
        'form': form,
        'restaurant': restaurant,
        'is_new': True
    })


def table_update(request, pk):
    """Редактирование стола"""
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        form = TableForm(request.POST, instance=table)
        if form.is_valid():
            form.save()
            return redirect('table_list', restaurant_id=table.restaurant.id)
    else:
        form = TableForm(instance=table)

    return render(request, 'bookings/table_form.html', {
        'form': form,
        'restaurant': table.restaurant,
        'is_new': False
    })


def table_delete(request, pk):
    """Удаление стола"""
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        restaurant_id = table.restaurant.id
        table.delete()
        return redirect('table_list', restaurant_id=restaurant_id)

    return render(request, 'bookings/table_confirm_delete.html', {
        'table': table
    })

def table_list(request, restaurant_id):
    """Отображает список столов в конкретном ресторане"""
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'bookings/table_list.html', {
        'restaurant': restaurant,
        'tables': tables
    })


def home(request):
    """Главная страница приложения"""
    return render(request, 'bookings/home.html')


def restaurant_list(request):
    """Отображает список всех ресторанов"""
    restaurants = Restaurant.objects.all()
    return render(request, 'bookings/restaurant_list.html', {
        'restaurants': restaurants
    })


def restaurant_detail(request, pk): 
    """Детальная информация о ресторане"""
    restaurant = get_object_or_404(Restaurant, pk=pk)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'bookings/restaurant_detail.html', {
        'restaurant': restaurant,
        'tables': tables
    })


@login_required
def create_reservation(request):
    """Создание бронирования"""
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = form.save(commit=False)
                reservation.user = request.user
                reservation.save()
                messages.success(request, 'Бронирование успешно создано!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Ошибка при создании брони: {str(e)}')
    else:
        table_id = request.GET.get('table_id')
        initial = {'table': table_id} if table_id else {}
        form = ReservationForm(initial=initial)
    
    return render(request, 'bookings/reservation_form.html', {'form': form})

def restaurant_create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('restaurant_list')
    else:
        form = RestaurantForm()
    return render(request, 'bookings/restaurant_form.html', {'form': form})

def restaurant_update(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            return redirect('restaurant_list')
    else:
        form = RestaurantForm(instance=restaurant)
    return render(request, 'restaurants/form.html', {'form': form})

def restaurant_delete(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    restaurant.delete()
    return redirect('restaurant-list')

def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Авторизация пользователя"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверные учетные данные')
    return render(request, 'registration/login.html')


def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('home')


@login_required
def profile(request):
    """Профиль пользователя"""
    reservations = Reservation.objects.filter(user=request.user).select_related('table__restaurant')
    return render(request, 'accounts/profile.html', {
        'reservations': reservations
    })

    


def init_test_data():
    """Инициализация тестовых данных"""
    if not Restaurant.objects.exists():
        restaurant = Restaurant.objects.create(
            name="Pizza from Damir",
            address="ул. Манаса 34",
            phone="+77771234567",
            description="Лучшая пицца в городе",
            opening_time="09:00:00",
            closing_time="23:00:00"
        )
        
        
        
        
        Table.objects.bulk_create([
            Table(restaurant=restaurant, number="1", capacity=4, shape="square"),
            Table(restaurant=restaurant, number="2", capacity=6, shape="round"),
            Table(restaurant=restaurant, number="VIP", capacity=8, shape="rectangular")
        ])


if __name__ == "__main__":
    init_test_data()