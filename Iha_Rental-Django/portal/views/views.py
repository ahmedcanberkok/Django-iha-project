from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.models import User
from .models import Customer, Dealer, Uas, Lease

# Customer views

def customer_index(request):
    if not request.user.is_authenticated:
        return render(request, 'customer/login.html')
    else:
        return render(request, 'customer/home_page.html')

def customer_login(request):
    return render(request, 'customer/login.html')

def customer_auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'customer/home_page.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return HttpResponseBadRequest("Kullanıcı adı veya parola eksik.")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                customer = Customer.objects.get(user=user)
            except Customer.DoesNotExist:
                customer = None

            if customer is not None:
                login(request, user)
                return render(request, 'customer/home_page.html')
        return render(request, 'customer/login_failed.html')

def customer_logout_view(request):
    logout(request)
    return render(request, 'customer/login.html')

def customer_register(request):
    return render(request, 'customer/register.html')

def customer_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        city = request.POST.get('city').lower()

        if not all([username, password, phone, firstname, lastname, email, city]):
            return HttpResponseBadRequest("Eksik veya hatalı veri.")

        try:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname, last_name=lastname)
        except:
            return render(request, 'customer/registration_error.html')
        
        customer = Customer.objects.create(user=user, phone=phone, city=city)
        
        return render(request, 'customer/registered.html')
    else:
        return render(request, 'customer/register.html')

# Diğer customer view fonksiyonlarını ekleyin...

# Dealer views

def dealer_index(request):
    if not request.user.is_authenticated:
        return render(request, 'dealer/login.html')
    else:
        return render(request, 'dealer/home_page.html')

def dealer_login(request):
    return render(request, 'dealer/login.html')

def dealer_auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'dealer/home_page.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return HttpResponseBadRequest("Kullanıcı adı veya parola eksik.")
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                dealer = Dealer.objects.get(user=user)
            except Dealer.DoesNotExist:
                dealer = None

            if dealer is not None:
                login(request, user)
                return render(request, 'dealer/home_page.html')
        return render(request, 'dealer/login_failed.html')

def dealer_logout_view(request):
    logout(request)
    return render(request, 'dealer/login.html')

def dealer_register(request):
    return render(request, 'dealer/register.html')

def dealer_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        city = request.POST.get('city').lower()

        if not all([username, password, phone, firstname, lastname, email, city]):
            return HttpResponseBadRequest("Eksik veya hatalı veri.")

        try:
            user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname, last_name=lastname)
        except:
            return render(request, 'dealer/registration_error.html')
        
        dealer = Dealer.objects.create(user=user, phone=phone, city=city)
        
        return render(request, 'dealer/registered.html')
    else:
        return render(request, 'dealer/register.html')

# Diğer dealer view fonksiyonlarını ekleyin...

# Ortak views

# İşte bu kısımda ortak olan view fonksiyonları bulunabilir
# Örneğin, arama, kiralama, sipariş listesi gibi işlemler bu bölümde yer alabilir.

# Diğer ortak view fonksiyonlarını ekleyin...
