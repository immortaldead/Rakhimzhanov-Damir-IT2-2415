from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Restaurant, Table, Reservation  
from .forms import ReservationForm

class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'bookings/restaurant_list.html'

class TableListView(ListView):
    model = Table
    template_name = 'bookings/table_list.html'
    
    def get_queryset(self):
        restaurant = get_object_or_404(Restaurant, pk=self.kwargs['restaurant_id'])
        return Table.objects.filter(restaurant=restaurant, is_active=True)

class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'bookings/reservation_create.html'
    success_url = '/reservations/'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)