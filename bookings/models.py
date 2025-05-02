from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Restaurant(models.Model):
    name = models.CharField(max_length=100, verbose_name="Pizza with Damir")
    address = models.TextField(verbose_name="Улица Манаса, 34/1")
    phone = models.CharField(max_length=20, verbose_name="87475777100")
    description = models.TextField(blank=True, verbose_name="Лучшая пицца в городе")
    opening_time = models.TimeField(verbose_name="8:00", null=True, blank=True)
    closing_time = models.TimeField(verbose_name="8:30", null=True, blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True, verbose_name="Изображение")
    
    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"
    
    def __str__(self):
        return self.name

class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables', verbose_name="Ресторан")
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер стола")
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name="Вместимость"
    )
    is_active = models.BooleanField(default=True, verbose_name="Доступен для брони")
    
    class Meta:
        verbose_name = "Стол"
        verbose_name_plural = "Столы"
        ordering = ['number']
    
    def __str__(self):
        return f"Стол {self.number} ({self.capacity} персон) - {self.restaurant.name}"

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
        # Автоматически устанавливаем время окончания брони (+2 часа от времени начала)
        if not self.end_time:
            from datetime import timedelta
            dummy_datetime = timezone.datetime.combine(self.date, self.time)
            self.end_time = (dummy_datetime + timedelta(hours=2)).time()
        super().save(*args, **kwargs)
    
    def is_active(self):
        return self.status in ['pending', 'confirmed']