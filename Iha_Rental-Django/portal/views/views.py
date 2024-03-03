from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.models import User
from .models import Customer, Dealer, Uas, Lease

# Customer views

def customer_index(request):
    if not request.user.is_authenticated:
        return render(request, 'customer_login.html')
    else:
        return render(request, 'customer_home_page.html')

def customer_login(request):
    return render(request, 'customer_login.html')

def customer_auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'customer_home_page.html')
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
                return render(request, 'customer_home_page.html')
        return render(request, 'customer_login_failed.html')

def customer_logout_view(request):
    logout(request)
    return render(request, 'customer_login.html')

def customer_register(request):
    return render(request, 'customer_register.html')

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
            return render(request, 'customer_registration_error.html')
        
        customer = Customer.objects.create(user=user, phone=phone, city=city)
        
        return render(request, 'customer_registered.html')
    else:
        return render(request, 'customer_register.html')

@login_required
def customer_search(request):
    return render(request, 'customer_search.html')

@login_required
def customer_search_result(request):
    if request.method == 'POST':

        model = request.POST.get('model')
        brand = request.POST.get('brand')
        city = request.POST.get('city')
        category = request.POST.get('category')
        length = request.POST.get('length')
        wingspan = request.POST.get('wingspan')
        max_speed = request.POST.get('max_speed')
       range = request.POST.get('range')

        if not any([model, brand, city, category, length, wingspan, max_speed, range]):
        uas_list = Uas.objects.filter(is_available=True)
        else:
          filter_params = {'is_available': True}
            if model:
                filter_params['model_icontains'] = model 
            if brand:
                filter_params['brand_icontains'] = brand 
            if city:
                filter_params['city_icontains'] = city
            if category:
                filter_params['category_icontains'] = category
            if length:
                filter_params['length_icontains'] = length
            if wingspan:
                filter_params['wingspan_icontains'] = wingspan
            if max_speed:
                filter_params['max_speed_icontains'] = max_speed
            if range:
                filter_params['range_icontains'] = range

               #Filteleri Uygula 
            uas_list = Uas.objects.filter(**filter_params)
        return render(request, 'customer_search_result.html', {'uas_list': uas_list})
    else:
        return render(request, 'customer_search.html')


@login_required
def customer_leasing(request):
    if request.method == 'POST':
        #Formdan gelen Kiralama bilgilerini al
        uas_id = request.POST.get('uas_id')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        if not all([uas_id, start_date, start_time, end_date, end_time]):
            return HttpResponseBadRequest("Eksik veya hatalı veri.")
        try:
            uas = Uas.objects.get(pk=uas_id)
        except Uas.DoesNotExist:
            return HttpResponseBadRequest("Geçersiz UAS ID'si.")

         # Kiralama başlangıç ve bitiş tarihini ve saatini birleştir
        start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M")
        #Kiralma süresini hesapla
        lease_duration_seconds = (end_datetime - start_datetime).total_seconds()
        #Kiralama süresi 1 saatten az olamaz
         if lease_duration_seconds < 3600:
            return HttpResponseBadRequest("Kiralama süresi en az 1 saat olmalıdır.")
       
       total_days = lease_duration_seconds // (24 * 3600)
        total_hours = (lease_duration_seconds % (24 * 3600)) // 3600

        #ihanın saatlik kira maliyetini hesapla
        hourly_cost = uas.hourly_cost
         # İhanın kanat açıklığı ve uzunluğunun çarpımının 2 katı
        wingspan_length_double = uas.wingspan * uas.length * 2
        #ihanın günlük kira maliyetini hesapla
        daily_cost = hourly_cost * wingspan_length_double
        #ihanın toplam kira maliyetini hesapla
        total_cost = daily_cost * total_days + (hourly_cost * wingspan_length_double * total_hours)
        #Kiralama kaydını oluştur
        lease = Lease.objects.create(
            uas=uas,
             customer=request.user.customer,
              start_datetime=start_datetime, 
              end_datetime=end_datetime, 
              total_cost=total_cost)

        #ihanın durumunu değiştir
        uas.is_available = False
        uas.save()
        #Kullanıcıya kiralama bilgilerini göster, Onay sayfasına yönlendir
        return render(request, 'customer_leased.html')
    else:
        return render(request, 'customer_leased_failed.html')

    
@login_required
def customer_confirm_lease(request):
    if request.method == 'POST':
        lease_id = request.POST.get('lease_id')
        if not lease_id:
            return HttpResponseBadRequest("Eksik veya hatalı veri.")
        try:
            lease = Lease.objects.get(pk=lease_id)
        except Lease.DoesNotExist:
            return HttpResponseBadRequest("Geçersiz Lease ID'si.")

        #Kiralama bilgilerini göster ve ihanın kullanıcıya atanmasını sağla
        lease.lease_customer = request.user.customer
        lease.save()

        return redirect('lease_confirmation')  # Kiralama başarılı sayfasına yönlendir
    else:
        return HttpResponseBadRequest("Method Not Allowed")

@login_required
def customer_manage_leases(request):
    customer = Customer.objects.get(customer=request.user)
    leases = Lease.objects.filter(customer=customer, is_complete=False)
    leases_list = [{'id': l.id, 'uas': l.uas, 'start_datetime': l.start_datetime, 'end_datetime': l.end_datetime, 'total_cost': l.total_cost} for l in leases]
    return render(request, 'customer_manage_leases.html', {'leases': leases})

@login_required
def customer_update_lease(request):
    if request.method == 'POST':
        lease_id = request.POST.get('lease_id')
        action = request.POST.get('action') # Kullanıcın yapmak istediği işlemi belirten alan
        if not lease_id or not action:
            return HttpResponseBadRequest("Eksik veya hatalı veri.")
        try:
            lease = Lease.objects.get(pk=lease_id)
        except Lease.DoesNotExist:
            return HttpResponseBadRequest("Geçersiz Lease ID'si.")

  if action == 'complete':  # Eğer kullanıcı kiralama kaydını tamamlamak istiyorsa
            #Kiralama kaydının tamamlanması
            lease.is_complete = True
            lease.save()
            uas=lease.uas
            uas.is_available = True
            uas.save()
            return HttpResponseRedirect('customer_manage_leases') #Kiralama kayıtlarını gösteren sayfaya yönlendir
           

        elif action == 'extend': # Kullanıcı kiralama süresini uzatmak istiyorsa
           #Eğer Lease süresi zaten sona ermişse, uzatma işlemi yapılamaz
            if lease.end_datetime <= timezone.now():
                return HttpResponseBadRequest("Kiralama süresi zaten sona ermiş.")
            
            #Eğer Lease süresi henüz bitmemişse, uzatma işlemi yapılır
            #Uztatma işlemi için gerekli verilerin alınması
            new_end_date = request.POST.get('new_end_date')
            new_end_time = request.POST.get('new_end_time')

            if not new_end_date or not new_end_time:
                return HttpResponseBadRequest("Yeni bitiş tarihi ve saatini belirtmelisiniz.")
            try:
                new_end_datetime = datetime.strptime(f"{new_end_date} {new_end_time}", "%Y-%m-%d %H:%M")
            except ValueError:
                return HttpResponseBadRequest("Geçersiz tarih veya saat formatı.")
            #Kiralama süresinin uzatılması
            if new_end_datetime <= lease.end_datetime:
                lease.lease_duration_seconds = (lease.end_datetime - lease.start_datetime).total_seconds()
                lease.total_cost = lease.total_cost * (lease.lease_duration_seconds / (lease.lease_duration_seconds + (new_end_datetime - lease.end_datetime).total_seconds()))
                lease.end_datetime = new_end_datetime
                lease.save()
                return HttpResponseRedirect('customer_manage_leases')
            else:
                return HttpResponseBadRequest("Yeni bitiş tarihi, mevcut bitiş tarihinden önce olamaz.")
      
       if action == 'delete':  # Eğer kullanıcı kiralama kaydını silmek istiyorsa
    # Dealer'ın kazancını güncelleme
    dealer = lease.uas.dealer
    dealer.wallet -= lease.total_cost
    dealer.save()
    
    # Kiralama kaydının silinmesi
    lease.delete()
    return HttpResponseRedirect('customer_manage_leases')
else:
    return HttpResponseBadRequest("Geçersiz işlem.")

 else:
    return HttpResponseBadRequest("Method Not Allowed")

# Yapacağınız güncellemelere göre customer view fonksiyonlarını ekleyebilirsiniz...







# Dealer views

def dealer_index(request):
    if not request.user.is_authenticated:
        return render(request, 'dealer_login.html')
    else:
        return render(request, 'dealer_home_page.html')

def dealer_login(request):
    return render(request, 'dealer_login.html')

def dealer_auth_view(request):
    if request.user.is_authenticated:
        return render(request, 'dealer_home_page.html')
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
                return render(request, 'dealer_home_page.html')
        return render(request, 'dealer_login_failed.html')

def dealer_logout_view(request):
    logout(request)
    return render(request, 'dealer_login.html')

def dealer_register(request):
    return render(request, 'dealer_register.html')

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
            return render(request, 'dealer_registration_error.html')
        
        dealer = Dealer.objects.create(user=user, phone=phone, city=city)
        
        return render(request, 'dealer_registered.html')
    else:
        return render(request, 'dealer_register.html')

# Diğer dealer view fonksiyonlarını ekleyin...
@login_required
def dealer_add_uas(request):
    if request.method == 'POST':
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        range = request.POST.get('range')
        wingspan = request.POST.get('wingspan')
        length = request.POST.get('length')
        max_speed = request.POST.get('max_speed')
        category = request.POST.get('category')
        if not all([brand, model, range, wingspan, length, max_speed, category]):
            return HttpResponseBadRequest("Eksik veya hatalı veri.")
        uas = Uas.objects.create(brand=brand, model=model, range=range, wingspan=wingspan, length=length, max_speed=max_speed, category=category, dealer=request.user.dealer)
        return render(request, 'dealer_uas_added.html')
    else:
        return render(request, 'dealer_home_page.html')

@login_required
def dealer_manage_uas(request):
    dealer = Dealer.objects.get(dealer=request.user)
    uas_list = Uas.objects.filter(dealer=request.user.dealer)
    return render(request, 'dealer_manage.html', {'uas_list': uas_list})

@login_required
def dealer_order_list(request):
    dealer = Dealer.objects.get(dealer=request.user)
    order_list = Lease.objects.filter(dealer=request.user.dealer,is_complete=False)
    return render(request, 'dealer_order_list.html', {'order_list': order_list})

@login_required
def dealer_complete_order(request:)
if request.method == 'POST':
    order_id = request.POST.get('order_id')
    if not order_id:
        return HttpResponseBadRequest("Eksik veya hatalı veri.")
        try:
            order = Lease.objects.get(pk=order_id)
            except Lease.DoesNotExist:
                return HttpResponseBadRequest("Geçersiz Lease ID'si.")

            lease.is_complete = True
            lease.save()
            uas=lease.uas
            uas.is_available = True
            uas.save()
            return HttpResponseRedirect('/portal/dealer_order_list')


    @login_required
def dealer_history(request):
    dealer = Dealer.objects.get(dealer=request.user)
    orders = Lease.objects.filter(dealer=dealer)
    return render(request, 'dealer_history.html', {'orders': orders})










# Ortak views

# İşte bu kısımda ortak olan view fonksiyonları bulunabilir
# Örneğin, arama, kiralama, sipariş listesi gibi işlemler bu bölümde yer alabilir.

# Diğer ortak view fonksiyonlarını ekleyin...
