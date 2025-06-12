from django.urls import path
from . import views

urlpatterns = [
    # временный путь, чтобы Django не ругался
    path('', views.profile, name='profile'),  # или другой view, который у тебя есть
]
