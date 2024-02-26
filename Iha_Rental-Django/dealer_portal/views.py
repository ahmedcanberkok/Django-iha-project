from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from dealer_portal.models import *
from customer_portal.models import *
from django.contrib.auth.decorators import login_required

def index(request):
    if not request.user.is_authenticated:
        return render(request, 'dealer/login.html')
    else:
        return render(request, 'dealer/home_page.html')

def login(request):
    return render(request, 'dealer/login.html')

def auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'dealer/home_page.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                dealer = Dealer.objects.get(dealer=user)
            except Dealer.DoesNotExist:
                dealer = None
            if dealer is not None:
                login(request, user)
                return render(request, 'dealer/home_page.html')
        return render(request, 'dealer/login_failed.html')

def logout_view(request):
    logout(request)
    return render(request, 'dealer/login.html')

def register(request):
    return render(request, 'dealer/register.html')

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
            return render(request, 'dealer/registration_error.html')
        try:
            area = Area.objects.get(city=city, postcode=postcode)
        except Area.DoesNotExist:
            area = None
        if area is not None:
            dealer = Dealer.objects.create(dealer=user, mobile=mobile, area=area)
        else:
            area = Area.objects.create(city=city, postcode=postcode)
            dealer = Dealer.objects.create(dealer=user, mobile=mobile, area=area)
        return render(request, 'dealer/registered.html')
    else:
        return render(request, 'dealer/register.html')

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        iha_name = request.POST['iha_name']
        brand = request.POST['brand']
        model = request.POST['model']
        weight = request.POST['weight']
        category = request.POST['category']
        dealer = Dealer.objects.get(dealer=request.user)
        city = request.POST['city'].lower()
        postcode = request.POST['postcode']
        description = request.POST['description']

        try:
            area = Area.objects.get(city=city, postcode=postcode)
        except Area.DoesNotExist:
            area = None

        if area is not None:
            vehicle = Vehicles.objects.create(iha_name=iha_name, brand=brand, model=model, weight=weight, category=category, dealer=dealer, area=area, description=description)
        else:
            area = Area.objects.create(city=city, postcode=postcode)
            vehicle = Vehicles.objects.create(iha_name=iha_name, brand=brand, model=model, weight=weight, category=category, dealer=dealer, area=area, description=description)

        vehicle.save()
        return render(request, 'dealer_portal/vehicle_added.html')
    else:
        return render(request, 'dealer_portal/add_vehicle.html')

@login_required
def manage_vehicles(request):
    dealer = Dealer.objects.get(dealer=request.user)
    vehicle_list = Vehicles.objects.filter(dealer=dealer)
    return render(request, 'dealer/manage.html', {'vehicle_list': vehicle_list})

@login_required
def order_list(request):
    dealer = Dealer.objects.get(dealer=request.user)
    orders = Orders.objects.filter(dealer=dealer)
    order_list = [o for o in orders if not o.is_complete]
    return render(request, 'dealer/order_list.html', {'order_list': order_list})

@login_required
def complete(request):
    if request.method == 'POST':
        order_id = request.POST['id']
        order = Orders.objects.get(id=order_id)
        order.is_complete = True
        order.save()
        vehicle = order.vehicle
        vehicle.is_available = True
        vehicle.save()
    return HttpResponseRedirect('/dealer_portal/order_list/')

@login_required
def history(request):
    dealer = Dealer.objects.get(dealer=request.user)
    orders = Orders.objects.filter(dealer=dealer)
    return render(request, 'dealer/history.html', {'wallet': dealer.wallet, 'order_list': orders})

@login_required
def delete(request):
    if request.method == 'POST':
        veh_id = request.POST['id']
        vehicle = Vehicles.objects.get(id=veh_id)
        vehicle.delete()
    return HttpResponseRedirect('/dealer_portal/manage_vehicles/')
