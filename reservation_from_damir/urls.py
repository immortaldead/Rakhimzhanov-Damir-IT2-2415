from django.contrib import admin
from django.urls import path
from bookings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('test/', views.test_view, name='test-view'),
    path('restaurants/', views.restaurant_list, name='restaurant-list'),
    path('restaurants/<int:restaurant_id>/tables/', views.table_list, name='table-list'),
    path('reservations/create/', views.create_reservation, name='reservation-create'),
]