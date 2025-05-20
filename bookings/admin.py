from django.contrib import admin
from .models import Restaurant, Table, Reservation
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

admin.site.register(User, UserAdmin)

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone')
    search_fields = ('name', 'address')

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'restaurant', 'capacity', 'is_active')
    list_filter = ('restaurant', 'is_active')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'table', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'table__number')