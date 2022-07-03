import requests
import copy

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from geopy import distance

from foodcartapp.models import Product, Restaurant, Order
from locations.locator import fetch_coordinates
from locations.models import Location

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant
                            in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item
               in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant
                                in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = (Order.objects.filter(status__in=['COOKING', 'UNPROCESSED'])
                   .select_related('assigned_restaurant')
                   .prefetch_related('elements__product')
                   .count_total_sums().order_by('-status', 'id'))
    restaurants = Restaurant.objects.prefetch_related('menu_items__product')
    customer_addresses = {order.address for order in orders}
    existed_locations = list(Location.objects.filter(address__in=customer_addresses)
                                             .values())
    existed_addresses = {location['address'] for location in existed_locations}
    new_addresses = customer_addresses - existed_addresses
    new_locations = []
    for address in new_addresses:
        coords = fetch_coordinates(address)
        if coords:
            lat, lon = coords
            new_locations.append(Location(
                address=address,
                lat=lat,
                lon=lon
            ))
        else:
            new_locations.append(
                Location(address=address),
                lat=None,
                lon=None
            )
    if new_locations:
        Location.objects.bulk_create(new_locations)
        existed_locations.extend(new_locations)
    for order in orders:
        order.client_coords = None
        if order.assigned_restaurant:
            continue
        for location in existed_locations:
            if location['address'] == order.address:
                order.client_coords = location['lat'], location['lon']
        order.restaurants = [copy.copy(restaurant) for restaurant in
                                restaurants.available(order)]
        for restaurant in order.restaurants:
            restaurant_coords = restaurant.lat, restaurant.lon
            if all(coord for coord in order.client_coords) and \
                all(coord for coord in restaurant_coords):
                try:
                    restaurant.distance = distance.distance(
                        restaurant_coords, order.client_coords
                    ).km
                except ValueError:
                    restaurant.distance = None
            else:
                restaurant.distance = None
        if all(restaurant.distance for restaurant
                in order.restaurants):
            order.restaurants.sort(key=lambda restaurant:
                                    restaurant.distance)
        order.visual_status = order.get_status_display()
        order.visual_payment = order.get_payment_display()
    return render(request, template_name='order_items.html', context={
        "order_items": orders
    })
