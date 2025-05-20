from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=True)
    is_manager = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


class Restaurant(models.Model):
    SHAPE_CHOICES = [
        ('square', 'Квадратный'),
        ('round', 'Круглый'),
        ('rectangular', 'Прямоугольный'),
    ]
    
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    description = models.TextField(blank=True, verbose_name="Описание")
    opening_time = models.TimeField(verbose_name="Время открытия")
    closing_time = models.TimeField(verbose_name="Время закрытия")
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True, verbose_name="Изображение")
    
    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables', verbose_name="Ресторан")
    number = models.CharField(max_length=10, verbose_name="Номер стола")
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Вместимость"
    )
    shape = models.CharField(max_length=20, choices=Restaurant.SHAPE_CHOICES, default='square', verbose_name="Форма")
    is_active = models.BooleanField(default=True, verbose_name="Доступен для брони")
    
    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        ordering = ['restaurant', 'number']
        unique_together = ('restaurant', 'number')
    
    def __str__(self):
        return f"Стол {self.number} ({self.capacity} пер.) - {self.restaurant.name}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('canceled', 'Отменено'),
        ('completed', 'Завершено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name="Пользователь")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations', verbose_name="Стол")
    date = models.DateField(verbose_name="Дата брони")
    time = models.TimeField(verbose_name="Время брони")
    end_time = models.TimeField(verbose_name="Время окончания", blank=True, null=True)
    guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество гостей"
    )
    special_requests = models.TextField(blank=True, verbose_name="Особые пожелания")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"
        ordering = ['-date', '-time']
        constraints = [
            models.UniqueConstraint(
                fields=['table', 'date', 'time'],
                name='unique_reservation'
            )
        ]
    
    def __str__(self):
        return f"Бронь #{self.id} на {self.date} {self.time} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if not self.end_time:
            dummy_datetime = timezone.datetime.combine(self.date, self.time)
            self.end_time = (dummy_datetime + timedelta(hours=2)).time()
        super().save(*args, **kwargs)
    
    def is_active(self):
        return self.status in ['pending', 'confirmed']


def init_restaurant_data():
    Restaurant = apps.get_model('bookings', 'Restaurant')
    Table = apps.get_model('bookings', 'Table')
    
    restaurants_data = [
        {
            'name': "Pizza from Damir",
            'address': "ул. Манаса 34",
            'phone': "+77777777777",
            'description': "Лучшая пицца в городе", 
            'opening_time': "09:00",
            'closing_time': "23:00"
        },
        {
            'name': "Burger Palace",
            'address': "ул. Гоголя 15",
            'phone': "+77775554433",
            'description': "Американские бургеры",
            'opening_time': "10:00",
            'closing_time': "22:00"
        },
        {
            'name': "Hinkali from Damir",
            'address': "ул. Пушкина 10",
            'phone': "+77771234567",
            'description': "Лучшие хинкали в городе",
            'opening_time': "11:00",
            'closing_time': "23:00"
        }
    ]

    for data in restaurants_data:
        Restaurant.objects.filter(name=data['name']).delete()
        
        restaurant = Restaurant.objects.create(**data)
        
        Table.objects.bulk_create([
            Table(
                restaurant=restaurant,
                number=str(i+1),
                capacity=[4, 6, 8][i],
                shape=['square', 'round', 'rectangular'][i],
                is_active=True
            ) for i in range(3)
        ])
        print(f"Создан ресторан: {restaurant.name} с 3 столами")


@receiver(post_migrate)
def on_migrate(sender, **kwargs):
    if sender.name == 'bookings':
        init_restaurant_data()