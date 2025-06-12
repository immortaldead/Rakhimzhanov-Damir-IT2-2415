from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=True, verbose_name=_("Клиент"))
    is_manager = models.BooleanField(default=False, verbose_name=_("Менеджер"))
    is_admin = models.BooleanField(default=False, verbose_name=_("Админ"))

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")


class Restaurant(models.Model):
    SHAPE_CHOICES = [
        ('square', _('Квадратный')),
        ('round', _('Круглый')),
        ('rectangular', _('Прямоугольный')),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name=_("Название"))
    address = models.TextField(verbose_name=_("Адрес"))
    phone = models.CharField(max_length=20, verbose_name=_("Телефон"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    opening_time = models.TimeField(verbose_name=_("Время открытия"))
    closing_time = models.TimeField(verbose_name=_("Время закрытия"))
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True, verbose_name=_("Изображение"))

    class Meta:
        verbose_name = _("Ресторан")
        verbose_name_plural = _("Рестораны")
        ordering = ['name']

    def __str__(self):
        return self.name


class Table(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='tables', verbose_name=_("Ресторан"))
    number = models.CharField(max_length=10, verbose_name=_("Номер стола"))
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name=_("Вместимость")
    )
    shape = models.CharField(max_length=20, choices=Restaurant.SHAPE_CHOICES, default='square', verbose_name=_("Форма"))
    is_active = models.BooleanField(default=True, verbose_name=_("Доступен для брони"))

    class Meta:
        verbose_name = _("Стол")
        verbose_name_plural = _("Столы")
        ordering = ['restaurant', 'number']
        unique_together = ('restaurant', 'number')

    def __str__(self):
        return f"{_('Стол')} {self.number} ({self.capacity} {_('пер.')}) - {self.restaurant.name}"


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Ожидает подтверждения')),
        ('confirmed', _('Подтверждено')),
        ('canceled', _('Отменено')),
        ('completed', _('Завершено')),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations', verbose_name=_("Пользователь"))
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations', verbose_name=_("Стол"))
    date = models.DateField(verbose_name=_("Дата брони"))
    time = models.TimeField(verbose_name=_("Время брони"))
    end_time = models.TimeField(verbose_name=_("Время окончания"), blank=True, null=True)
    guests = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name=_("Количество гостей"))
    special_requests = models.TextField(blank=True, verbose_name=_("Особые пожелания"))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name=_("Статус"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Дата создания"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Дата обновления"))

    class Meta:
        verbose_name = _("Бронь")
        verbose_name_plural = _("Брони")
        ordering = ['-date', '-time']
        constraints = [
            models.UniqueConstraint(fields=['table', 'date', 'time'], name='unique_reservation')
        ]

    def __str__(self):
        return f"{_('Бронь')} #{self.id} - {self.date} {self.time} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if not self.end_time:
            dummy_datetime = timezone.datetime.combine(self.date, self.time)
            self.end_time = (dummy_datetime + timedelta(hours=2)).time()
        super().save(*args, **kwargs)

    def is_active(self):
        return self.status in ['pending', 'confirmed']


# --- Автозаполнение данных после миграции ---
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
                number=str(i + 1),
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
