from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.i18n import set_language
from bookings import views
from django.shortcuts import redirect
from django.utils import translation


urlpatterns = [
    path('set_language/', set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),  
]


urlpatterns += [
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]

urlpatterns += [
    *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
]

from django.conf.urls.i18n import i18n_patterns

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('restaurants/', views.restaurant_list, name='restaurant-list'),
    path('restaurants/<int:restaurant_id>/tables/', views.table_list, name='table-list'),
    path('reservations/create/', views.create_reservation, name='reservation-create'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/profile/', views.profile, name='profile'),
    path('restaurants/<int:pk>/', views.restaurant_detail, name='restaurant-detail'),
    path('edit/<int:pk>/', views.restaurant_update, name='restaurant_update'),
    path('restaurants/', include('bookings.urls')), 
    path('accounts/', include('users.urls')),
)

def redirect_to_language(request):
    user_language = translation.get_language_from_request(request)
    return redirect(f'/{user_language}/')

urlpatterns += [
    path('', redirect_to_language),
]