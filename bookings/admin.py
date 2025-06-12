from django.contrib import admin
from .models import Restaurant, Table, Reservation, CustomUser
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
User = get_user_model()

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_customer', 'is_manager', 'is_admin')
    fieldsets = UserAdmin.fieldsets + (
        (_("Роли"), {'fields': ('is_customer', 'is_manager', 'is_admin')}),
    )

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
