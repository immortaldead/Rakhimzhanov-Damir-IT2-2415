from django.urls import path
from . import views

urlpatterns = [
    path('', views.restaurant_list, name='restaurant_list'),
    path('new/', views.restaurant_create, name='restaurant_create'),
    path('edit/<int:pk>/', views.restaurant_update, name='restaurant_update'),
    path('delete/<int:pk>/', views.restaurant_delete, name='restaurant_delete'),
    path('restaurants/<int:restaurant_id>/tables/', views.table_list, name='table_list'),
    path('tables/<int:pk>/', views.table_detail, name='table_detail'),
    path('restaurants/<int:restaurant_id>/tables/create/', views.table_create, name='table_create'),
    path('tables/<int:pk>/update/', views.table_update, name='table_update'),
    path('tables/<int:pk>/delete/', views.table_delete, name='table_delete'),
    path('profile/', views.profile, name='profile'),
    path('cancel_reservation/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('create_reservation/', views.create_reservation, name='create_reservation'),
    path('accounts/register/', views.register, name='register'),
    path('create/', views.restaurant_create, name='restaurant_create'),
]