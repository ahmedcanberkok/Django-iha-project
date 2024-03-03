from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Customer, Area, Orders, Vehicles

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'customer/login.html')
    else:
        return render(request, 'customer/home_page.html')

def login(request):
    return render(request, 'customer/login.html')

def auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'customer/home_page.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            try:
                customer = Customer.objects.get(user=user)
            except Customer.DoesNotExist:
                customer = None
            if customer is not None:
                return render(request, 'customer/home_page.html')
        return render(request, 'customer/login_failed.html')

def logout_view(request):
    logout(request)
    return render(request, 'customer/login.html')

def register(request):
    return render(request, 'customer/register.html')

def registration(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        mobile = request.POST['mobile']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        city = request.POST['city'].lower()
        postcode = request.POST['postcode']
        try:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname, last_name=lastname)
        except:
            return render(request, 'customer/registration_error.html')
        try:
            area = Area.objects.get(city=city, postcode=postcode)
        except Area.DoesNotExist:
            area = Area.objects.create(city=city, postcode=postcode)
        customer = Customer.objects.create(user=user, mobile=mobile, area=area)
        return render(request, 'customer/registered.html')
    else:
        return render(request, 'customer/register.html')

@login_required
def search(request):
    return render(request, 'customer/search.html')

@login_required
def search_results(request):
    if request.method == 'POST':
        city = request.POST['city'].lower()
        vehicles_list = []
        areas = Area.objects.filter(city=city)
        for area in areas:
            vehicles = Vehicles.objects.filter(area=area)
            for vehicle in vehicles:
                if vehicle.is_available:
                    vehicle_dict = {'name': vehicle.name, 'brand': vehicle.brand, 'model': vehicle.model, 'weight': vehicle.weight, 'category': vehicle.category}
                    vehicles_list.append(vehicle_dict)
        request.session['vehicles_list'] = vehicles_list
        return render(request, 'customer/search_results.html')
    else:
        return HttpResponseBadRequest("Method Not Allowed")

@login_required
def rent_vehicle(request):
    if request.method == 'POST':
        vehicle_id = request.POST['id']
        vehicle = Vehicles.objects.get(id=vehicle_id)
        cost_per_day = int(vehicle.weight) 
        return render(request, 'customer/confirmation.html', {'vehicle': vehicle, 'cost_per_day': cost_per_day})
    else:
        return HttpResponseBadRequest("Method Not Allowed")

@login_required
def confirm(request):
    if request.method == 'POST':
        vehicle_id = request.POST['id']
        username = request.user
        user = User.objects.get(username=username)
        days = request.POST['days']
        vehicle = Vehicles.objects.get(id=vehicle_id)
        if vehicle.is_available:
            dealer = vehicle.dealer
            rent = int(vehicle.weight)  * int(days)
            dealer.wallet += rent
            dealer.save()
            try:
                order = Orders.objects.create(vehicle=vehicle, dealer=dealer, user=user, rent=rent, days=days)
            except:
                order = Orders.objects.get(vehicle=vehicle, dealer=dealer, user=user, rent=rent, days=days)
            vehicle.is_available = False
            vehicle.save()
            return render(request, 'customer/confirmed.html', {'order': order})
        else:
            return render(request, 'customer/order_failed.html')
    else:
        return HttpResponseBadRequest("Method Not Allowed")

@login_required
def manage(request):
    user = request.user
    orders = Orders.objects.filter(user=user, is_complete=False)
    order_list = [{'id': o.id, 'rent': o.rent, 'vehicle': o.vehicle, 'days': o.days, 'dealer': o.dealer} for o in orders]
    return render(request, 'customer/manage.html', {'order_list': order_list})

@login_required
def update_order(request):
    if request.method == 'POST':
        order_id = request.POST['id']
        order = Orders.objects.get(id=order_id)
        vehicle = order.vehicle
        vehicle.is_available = True
        vehicle.save()
        dealer = order.dealer
        dealer.wallet -= int(order.rent)
        dealer.save()
        order.delete()
        cost_per_day = int(vehicle.weight) 
        return render(request, 'customer/confirmation.html', {'vehicle': vehicle, 'cost_per_day': cost_per_day})
    else:
        return HttpResponseBadRequest("Method Not Allowed")

@login_required
def delete_order(request):
    if request.method == 'POST':
        order_id = request.POST['id']
        order = Orders.objects.get(id=order_id)
        dealer = order.dealer
        dealer.wallet -= int(order.rent)
        dealer.save()
        vehicle = order.vehicle
        vehicle.is_available = True
        vehicle.save()
        order.delete()
        return HttpResponseRedirect('/customer_portal/manage/')
    else:
        return HttpResponseBadRequest("Method Not Allowed")
