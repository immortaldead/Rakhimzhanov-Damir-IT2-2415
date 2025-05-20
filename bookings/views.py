from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponse
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Restaurant, Table, Reservation
from .forms import ReservationForm, RestaurantForm, TableForm
from django.urls import path
from . import views



User = get_user_model()  

class CustomRegisterForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


def register(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('login')
    else:
        form = CustomRegisterForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверные учетные данные')
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('login')




def test_view(request):
    return HttpResponse("<h1 style='color:green'>Тест успешен!</h1>")


def table_detail(request, pk):
    table = get_object_or_404(Table, pk=pk)
    return render(request, 'bookings/table_detail.html', {
        'table': table
    })


def table_create(request, restaurant_id):
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
    table = get_object_or_404(Table, pk=pk)
    if request.method == 'POST':
        restaurant_id = table.restaurant.id
        table.delete()
        return redirect('table_list', restaurant_id=restaurant_id)

    return render(request, 'bookings/table_confirm_delete.html', {
        'table': table
    })


def table_list(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'bookings/table_list.html', {
        'restaurant': restaurant,
        'tables': tables
    })


def home(request):
    return render(request, 'bookings/home.html')


@login_required
def create_reservation(request):
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
        if table_id:
            table = get_object_or_404(Table, id=table_id)
            initial = {'table': table_id}
        else:
            initial = {}
        form = ReservationForm(initial=initial)

    return render(request, 'bookings/reservation_form.html', {'form': form})


def restaurant_list(request):
    restaurants = Restaurant.objects.all()
    return render(request, 'bookings/restaurant_list.html', {
        'restaurants': restaurants
    })


def restaurant_detail(request, pk): 
    restaurant = get_object_or_404(Restaurant, pk=pk)
    tables = Table.objects.filter(restaurant=restaurant)
    return render(request, 'bookings/restaurant_detail.html', {
        'restaurant': restaurant,
        'tables': tables
    })


@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    if reservation.status != 'canceled':
        reservation.status = 'canceled'
        reservation.save()
        messages.success(request, 'Бронирование отменено!')
    else:
        messages.warning(request, 'Это бронирование уже отменено!')
    
    return redirect('profile')


@login_required
def profile(request):
    reservations = Reservation.objects.filter(user=request.user).select_related('table__restaurant')
    return render(request, 'accounts/profile.html', {
        'reservations': reservations
    })


@login_required
def restaurant_create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save()
            messages.success(request, 'Ресторан успешно добавлен!')
            return redirect('restaurant_detail', pk=restaurant.pk)
    else:
        form = RestaurantForm()
    
    return render(request, 'bookings/restaurant_form.html', {
        'form': form,
        'is_new': True
    })
    
    
@login_required
def restaurant_update(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)

    if request.method == 'POST':
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ресторан успешно обновлен!')
            return redirect('restaurant_detail', pk=restaurant.pk)
    else:
        form = RestaurantForm(instance=restaurant)
    
    return render(request, 'bookings/restaurant_form.html', {
        'form': form,
        'is_new': False,
        'restaurant': restaurant
    })


def init_test_data():
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
        

@login_required
def restaurant_create(request):
    if request.method == 'POST':
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save()
            messages.success(request, 'Ресторан успешно создан!')
            return redirect('restaurant_detail', pk=restaurant.pk)
    else:
        form = RestaurantForm()
    
    return render(request, 'bookings/restaurant_form.html', {
        'form': form,
        'is_new': True
    })
    

@login_required
def restaurant_delete(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.method == 'POST':
        restaurant.delete()
        messages.success(request, 'Ресторан удалён.')
        return redirect('restaurant_list')
    return render(request, 'bookings/restaurant_confirm_delete.html', {
        'restaurant': restaurant
    })


urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('<int:pk>/', views.restaurant_detail, name='restaurant_detail'),
    path('create/', views.restaurant_create, name='restaurant_create'),
    path('edit/<int:pk>/', views.restaurant_update, name='restaurant_update'),
]