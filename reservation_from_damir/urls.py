from django.contrib import admin
from django.urls import path
from bookings import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('restaurants/', views.RestaurantListView.as_view(), name='restaurant-list'),
    path('restaurants/<int:restaurant_id>/tables/', views.TableListView.as_view(), name='table-list'),
    path('reservations/create/', views.ReservationCreateView.as_view(), name='reservation-create'),
]
