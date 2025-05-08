from django.urls import path, include
from bookings import views


urlpatterns = [
    path('', views.home, name='home'),
    path('restaurants/', views.restaurant_list, name='restaurant-list'),
    path('restaurants/<int:restaurant_id>/tables/', views.table_list, name='table-list'),
    path('reservations/create/', views.create_reservation, name='reservation-create'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant-detail'),
    path('restaurants/<int:restaurant_id>/', views.restaurant_detail, name='restaurant-detail'),
    path('restaurants/', include('bookings.urls')),
]