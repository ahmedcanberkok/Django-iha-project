from django.db import models

# Kullanıcılar için model
class Users(models.Model):
    user_id = models.AutoField(primary_key=True)  # Otomatik artan kullanıcı kimliği
    firstname = models.CharField(max_length=100)  # Kullanıcının adı
    lastname = models.CharField(max_length=100)  # Kullanıcının soyadı
    username = models.CharField(max_length=100)  # Kullanıcı adı
    password = models.CharField(max_length=100)  # Kullanıcı şifresi
    email = models.EmailField(max_length=254)  # Kullanıcının e-posta adresi
    phone = models.CharField(max_length=13)  # Kullanıcının telefon numarası
    city = models.CharField(max_length=100)  # Kullanıcının şehri

# Müşteriler için model
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)  # Otomatik artan müşteri kimliği
    user = models.ForeignKey(Users, on_delete=models.CASCADE)  # Kullanıcıya referans ve silme kuralı (CASCADE)


    # Diğer özel alanlar buraya eklenebilir

# Least yapanlar için model
class Dealer(models.Model):
    dealer_id = models.AutoField(primary_key=True)  # Dealer kimliği otomatik artan
    user = models.ForeignKey(Users, on_delete=models.CASCADE)  # Kullanıcıya referans ve silme kuralı (CASCADE)

    # Diğer özel alanlar buraya eklenebilir

# İHA'lar için model
class Uas(models.Model):
    uas_id = models.AutoField(primary_key=True)  # İHA kimliği otomatik artan
    brand = models.CharField(max_length=100)  # İHA markası
    model = models.CharField(max_length=100)  # İHA modeli
    range = models.CharField(max_length=100)  # İHA menzili
    wingspan = models.CharField(max_length=100)  # İHA kanat açıklığı
    length = models.CharField(max_length=100)  # İHA uzunluğu
    max_speed = models.CharField(max_length=100)  # İHA maksimum hızı
    category = models.CharField(max_length=100)  # İHA kategorisi

# Kiralamalar için model
class Lease(models.Model):
    lease_id = models.AutoField(primary_key=True)  # Kiralama kimliği
    leased_uas = models.ForeignKey(Uas, on_delete=models.CASCADE)  # Kiralanan İHA'ya referans
    lease_start_date = models.DateTimeField()  # Kiralama başlangıç tarihi
    lease_end_date = models.DateTimeField()  # Kiralama bitiş tarihi
    lease_customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # Kiralayan müşteriye referans
    dealer = models.ForeignKey(Dealer, on_delete=models.CASCADE)  # Satıcıya referans
    is_complete = models.BooleanField(default=False)  # Kiralama tamamlandı mı?
    lease_fee = models.DecimalField(max_digits=10, decimal_places=2)  # Kiralama ücreti
