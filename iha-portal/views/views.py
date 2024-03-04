from django.contrib.auth.models import User
from django.contrib.auth import Q
from .models import Customer, Dealer, Uas, Lease
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.utils import IntegrityError
from django.urls import reverse
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import Q
from .models import Customer, Dealer, Uas, Lease
from django_brutebuster.exceptions import BruteBusterFailureLimitReached


def index(request):
    #Ana sayfa için index.html şablonunu render et
    return render(request, 'index.html')



# Customer views

def customer_index(request):
    # Kullanıcı nesnesinin oturum açık olup olmadığını kontrol et
    if not request.user.is_authenticated:
        #Oturm açık değilse, kullanıcıyı giriş sayfasına yönlendir
        return render(request, 'customer_login.html')
    else:
        #Oturum açık ise, kullanıcıyı müşteri ana sayfasına yönlendir
        return render(request, 'customer_home_page.html')

def customer_login(request):
    return render(request, 'customer_login.html')

@login_required
def customer_auth_view(request):
    #Eğer kullanıcı oturum açık ise, müşteri ana sayfasına yönlendir
    if request.user.is_authenticated:
        return render(request, 'customer_home_page.html')
    else:
        #Oturm açık değilse, kullanıcı adı ve parolayı al ve kimlik doğrulama işlemi yap
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password:
            return HttpResponseBadRequest("Kullanıcı adı veya parola eksik.")

        try:
            user = authenticate(request, username=username, password=password)
        except BruteBusterFailureLimitReached: # Eğer kullanıcı başarısız giriş denemesi sınırını aştıysa
            return HttpResponseBadRequest("Çok fazla başarısız giriş denemesi. Lütfen 10 saniye bekleyin.")
        
        if user is not None:
            try:
                customer = Customer.objects.get(user=user)
            except Customer.DoesNotExist:
                customer = None

            if customer is not None:
                #Kullanıcı doğrulandıysa, oturum aç ve müşteri ana sayfasına yönlendir
                login(request, user)
                return render(request, 'customer_home_page.html')
            #Doğrulama başarısız ise, kullanıcıyı giriş sayfasına yönlendir
        return render(request, 'customer_login_failed.html')

def customer_logout_view(request):
    #Kullanıcının oturumunu kapat ve giriş sayfasına yönlendir
    logout(request)
    return render(request, 'customer_login.html')

def customer_register(request):
    ## Müşteri kaydı için kayıt formunu gösteren views fonksiyonu
    return render(request, 'customer_register.html')


# Müşteri kaydı için formu işleyen ve müşteri nesnesi oluşturan views fonksiyonu
def customer_registration(request):
    if request.method == 'POST':
        #Formdan gelen verileri al
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        city = request.POST.get('city').lower()

        #Formdan gelen verilerin eksik olup olmadığını kontrol et
        if not all([username, password, phone, firstname, lastname, email, city]):
            return HttpResponseBadRequest("Eksik veya hatalı veri.")

        try:
            #Yeni kullanıcı nesnesi oluştur
            user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname, last_name=lastname)
        except IntegrityError:
            return HttpResponseBadRequest("Bu kullanıcı adı zaten kullanılıyor.Lütfen başka bir kullanıcı adı seçin.")
        except Exception as e:
            #Herhangi bir hata durumunda, hata mesajını göster.
            return render(request, 'customer_registration_error.html', {'error_message': str(e)})
        
        #Yeni müşteri nesnesi oluştur.
        customer = Customer.objects.create(user=user, phone=phone, city=city)
        
        return render(request, 'customer_registered.html') #Başarılı işlem sonrasında customer_registered.html şablonuna yönlendir.
    else:
        return render(request, 'customer_register.html') #Kayıt formunu gösteren sayfaya yönlendir.


#Müşterinin İHA arama sayfasını gösteren views fonksiyonu
@login_required
def customer_search(request):
    return render(request, 'customer_search.html')


#Müşterinin İHA arama sonuçlarını gösteren views fonksiyonu
@login_required
def customer_search_result(request):
    if request.method == 'POST':
        #Formdan gelen arama parametrelerini al
        model = request.POST.get('model')
        brand = request.POST.get('brand')
        city = request.POST.get('city')
        category = request.POST.get('category')
        length = request.POST.get('length')
        wingspan = request.POST.get('wingspan')
        max_speed = request.POST.get('max_speed')
       reach = request.POST.get('reach')

        #Eğer hiçbir parametre girilmemişse, tüm İHA'ları getir.
        if not any([model, brand, city, category, length, wingspan, max_speed, reach]):
        uas_list = Uas.objects.filter(is_available=True)
        else:
            #Boş olmayan parametreleri filtrele
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
        if reach:
            filter_params['reach_icontains'] = reach

               #Filteleri Uygula 
        uas_list = Uas.objects.filter(**filter_params)
        return render(request, 'customer_search_result.html', {'uas_list': uas_list})
    else:
        #POST İsteği yapılmamışsı arama formunu göster.
        return render(request, 'customer_search.html')


#Müşterinin İHA kiralama işlemini gerçekleştiren ve kiralama kaydını oluşturan views fonksiyonu
@login_required
def customer_leasing(request):
    if request.method == 'POST':
        #Formdan gelen Kiralama bilgilerini al
        uas_id = request.POST.get('uas_id')
        start_date = request.POST.get('start_date')
        start_time = request.POST.get('start_time')
        end_date = request.POST.get('end_date')
        end_time = request.POST.get('end_time')
        #Eksik veri kontrolü yap
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
        #POST İsteği yapılmamışsa, kiralama başarısız sayfasına yönlendir.
        return render(request, 'customer_leased_failed.html')

    # Müşterinin kiralama işlemini onaylayan ve İHA'yı kullanıcıya atayan views fonksiyonu
@login_required
def customer_confirm_lease(request):
    if request.method == 'POST':
        #Formdan gelen Kiralama ID'sini al.
        lease_id = request.POST.get('lease_id')
        #Eksik veri kontrolü yap
        if not lease_id:
            return HttpResponseBadRequest("Eksik veya hatalı veri.")
        try:
            #Kiralama kimliği ile kiralama kaydını getir.
            lease = Lease.objects.get(pk=lease_id)
        except Lease.DoesNotExist:
            return HttpResponseBadRequest("Geçersiz Lease ID'si.")

        # Kiralama kaydını müşteriye ata ve kaydet
        lease.lease_customer = request.user.customer
        lease.save()

        return HttpResponseRedirect('customer_lease_confirmed')  # Kiralama başarılı sayfasına yönlendir
    else:
                # POST isteği dışında bir istek alındığında, Hatalı İstek yanıtı gönder
        return HttpResponseBadRequest("Method Not Allowed")

## Müşterinin yönettiği tamamlanmamış kiralama kayıtlarını listeleme işlemini gerçekleştiren views fonksiyonu
@login_required
def customer_manage_leases(request):
    #Giriş yapan kullanıcının ilişkili olduğu müşteri nesnesini al
    customer = Customer.objects.get(customer=request.user)
    #Müşteriye ait tamamlanmamış kiralama kayıtlarını getir.
    leases = Lease.objects.filter(customer=customer, is_complete=False)

    #Kiralama kayıtlarını bir listede topla
    leases_list = [{'id': l.id, 'uas': l.uas, 'start_datetime': l.start_datetime, 'end_datetime': l.end_datetime, 'total_cost': l.total_cost} for l in leases]
    #Kiralama kayıtlarını gösteren sayfaya yönlendir
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
            #Uzatma işlemi için gerekli verilerin alınması
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
   if request.user.is_authenticated: # Eğer kullanıcı zaten oturum açmışsa
        return render(request, 'dealer_home_page.html') #Dealer ana sayfasına yönlendir
    else: # Oturum açık değilse
        #Kullanıcı adı ve parolayı al ve kimlik doğrulama işlemi yap
        username = request.POST.get('username')
        password = request.POST.get('password')
        if not username or not password: # Eğer kullanıcı adı veya parola eksikse
            return HttpResponseBadRequest("Kullanıcı adı veya parola eksik.")
        try:      
            user = authenticate(request, username=username, password=password) # Kullanıcıyı kimlik doğrulama işlemine tabi tut
        except BruteBusterFailureLimitReached: # Eğer kullanıcı başarısız giriş denemesi sınırını aştıysa
            return HttpResponseBadRequest("Çok fazla başarısız giriş denemesi. Lütfen 10 saniye bekleyin.")
        
        if user is not None:
            try:
                dealer = Dealer.objects.get(user=user)  # Kullanıcıya ait dealer nesnesini al
            except Dealer.DoesNotExist: # Eğer dealer nesnesi bulunamazsa
                dealer = None

            if dealer is not None: # Eğer dealer nesnesi varsa
                login(request, user) # Kullanıcıyı oturum açık olarak işaretle
                return render(request, 'dealer_home_page.html') #Dealer ana sayfasına yönlendir
        return render(request, 'dealer_login_failed.html') #Doğrulama başarısız ise, kullanıcıyı login_failed sayfasına yönlendir

def dealer_logout_view(request): # Kullanıcıyı oturumdan çıkaran views fonksiyonu
    logout(request) # Kullanıcının oturumunu kapat
    return render(request, 'dealer_login.html') #Giriş sayfasına yönlendir

def dealer_register(request): # Dealer kaydı için kayıt formunu gösteren views fonksiyonu
    return render(request, 'dealer_register.html') #Dealer kayıt formunu gösteren sayfaya yönlendir

def dealer_registration(request):
       """
    Dealer kaydı oluşturan view fonksiyonu. Kullanıcı POST isteği gönderdiğinde, formdan gelen verileri kullanarak
    yeni bir dealer kullanıcı hesabı ve dealer profili oluşturur. Eğer veriler eksik veya hatalı ise uygun bir hata
    mesajı döndürür. Başarılı bir şekilde kayıt tamamlandığında, kullanıcıyı dealer_registered  sayfasına yönlendirir.
    """
    if request.method == 'POST':
        #Formdan gelen verileri al
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        city = request.POST.get('city').lower()

        #Formdan gelen verilerin eksik olup olmadığını kontrol et
        if not all([username, password, phone, firstname, lastname, email, city]):
            return HttpResponseBadRequest("Eksik veya hatalı veri.")

        try:
            #Yeni kullanıcı nesnesi oluştur
            user = User.objects.create_user(username=username, password=password, email=email, first_name=firstname, last_name=lastname)
            except IntegrityError:
                return HttpResponseBadRequest("Bu kullanıcı adı zaten kullanılıyor.Lütfen başka bir kullanıcı adı seçin.")
        except Exception as e:
            #Diğer istisnai durumlar için hata mesajı döndür.
            return render(request, 'dealer_registration_error.html')
        
        #Yeni dealer nesnesi oluştur.
        dealer = Dealer.objects.create(user=user, phone=phone, city=city)
        
        #Başarılı kayıt sonrasında dealer_registered.html sayfasına yönlendir.
        return render(request, 'dealer_registered.html')
    else:
        return render(request, 'dealer_register.html') #Kayıt formunu gösteren sayfaya yönlendir.

@login_required
def dealer_add_uas(request): # İHA ekleme formunu gösteren views fonksiyonu
    if request.method == 'POST':
        #Formdan gelen verileri al
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        reach = request.POST.get('reach')
        wingspan = request.POST.get('wingspan')
        length = request.POST.get('length')
        max_speed = request.POST.get('max_speed')
        category = request.POST.get('category')
        #Gerekli tüm alanlar doldurulmuş mu kontrol et.
        if not all([brand, model, reach, wingspan, length, max_speed, category]):
           #Eğer eksik alan varsa, hata mesajı göster
            return HttpResponseBadRequest("Eksik veya hatalı veri.")
        
        #Uas nesnesini oluştur ve veritabanına kaydet.
        uas = Uas.objects.create(brand=brand, model=model, reach=reach, wingspan=wingspan, length=length, max_speed=max_speed, category=category, dealer=request.user.dealer)
        #Başarılı işlem sonrasında dealer_uas_added.html şablonuna yönlendir
        return HttpResponseRedirect(reverse('dealer_uas_added'))  # dealer_uas_added.html şablonuna yönlendir
    else:
        return render(request, 'dealer_add_uas_page.html')

@login_required
#Dealer'ın eklediği İHA'ları listele ve silme işlemi yap
def dealer_uas_list(request):

    dealer = request.user.dealer # Giriş yapan kullanıcının ilişkili olduğu dealer nesnesini al

    if request.method == 'POST':
        uas_id = request.POST.get('id') # Silinecek İHA'nın kimliğini al
        try:
            uas = Uas.objects.get(id=uas_id, dealer=dealer)
            uas.delete() # İHA'yı sil
        except Uas.DoesNotExist:
         # İHA bulunamadı veya kullanıcıya ait değil, hiçbir şey yapma
            pass
        
        # İşlem tamamlandıktan sonra aynı sayfaya geri yönlendir
        return redirect('dealer_uas_list')

    else:
        # Dealer'a ait olan tüm İHA'ları al
        uas_list = Uas.objects.filter(dealer=dealer)
        return render(request, 'dealer_uas_list.html', {'uas_list': uas_list}) # İHA listesini gösteren sayfaya yönlendir

@login_required
def dealer_lease_list(request):
    #Giriş yapan kullanıcının ilişkili olduğu bayi nesnesini al.
    dealer = Dealer.objects.get(dealer=request.user)
    #Tamamlanmamış kiralama kayıtlarını filtrele
    lease_list = Lease.objects.filter(dealer=request.user.dealer,is_complete=False)
    #Şablon dosyasına kiralama kayıtlarını gönder.
    return render(request, 'dealer_lease_list.html', {'lease_list': lease_list})


@login_required
def dealer_complete_lease(request): # Kiralama kaydını tamamlama işlemini gerçekleştiren views fonksiyonu
    if request.method == 'POST':
        order_id = request.POST.get('order_id') # Formdan gelen kiralama kimliğini al
        if not order_id: # Eğer kiralama kimliği eksikse
            return HttpResponseBadRequest("Eksik veya hatalı veri.") # Hata mesajı döndür

        try:
            lease = Lease.objects.get(pk=order_id) # Kiralama kimliği ile kiralama kaydını al
        except Lease.DoesNotExist: # Eğer kiralama kaydı bulunamazsa
            return HttpResponseBadRequest("Geçersiz Lease ID'si.") # Hata mesajı döndür

        # Koşul: Kiralama süresi bitmiş olmalı
        if lease.is_expired: # Eğer kiralama süresi bitmişse
            lease.is_complete = True # Kiralama kaydını tamamla
            lease.save() # Kiralama kaydını kaydet

            # İlgili İHA'yı tekrar kullanılabilir hale getir
            uas = lease.uas # Kiralanan İHA'yı al
            uas.is_available = True # İHA'yı tekrar kullanılabilir hale getir
            uas.save()  # İHA durumunu kaydet

            # Kullanıcısını sipariş listesi sayfasına yönlendir
            return HttpResponseRedirect('/portal/dealer_lease_list') # Kiralama listesine yönlendir
        else:
            return HttpResponseBadRequest("Kiralama süresi bitmemiş.") # Hata mesajı döndür

@login_required
def dealer_history(request): # Dealer'a ait tamamlanmış kiralama kayıtlarını listeleme işlemini gerçekleştiren views fonksiyonu
    dealer = Dealer.objects.get(dealer=request.user) # Giriş yapan kullanıcının ilişkili olduğu dealer nesnesini al
    orders = Orders.objects.filter(dealer=dealer, is_complete=True)  # Sadece tamamlanan siparişleri getir
    total_earnings = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0  # Toplam kazanç
    return render(request, 'dealer_account_activities.html', {'wallet': dealer.wallet, 'total_earnings': total_earnings, 'order_list': orders}) # İlgili şablon dosyasına yönlendir


# Yapacağınız güncellemelere göre dealer view fonksiyonlarını ekleyebilirsiniz...
