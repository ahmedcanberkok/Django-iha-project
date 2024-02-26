from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator

from django.contrib.auth.models import User


class Area(models.Model):
    pincode = models.CharField(validators=[MinLengthValidator(6), MaxLengthValidator(6)], max_length=6, unique=True)
    city = models.CharField(max_length=20)

class Dealer(models.Model):
    dealer = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(validators=[MinLengthValidator(10), MaxLengthValidator(13)], max_length=13)
    area = models.OneToOneField(Area, on_delete=models.PROTECT)
    wallet = models.IntegerField(default=0)

class Vehicles(models.Model):
    iha_name = models.CharField(max_length=20)
    brand = models.CharField(max_length=50)  # Değişiklik burada: brand alanı eklendi
    model = models.CharField(max_length=50)  # Değişiklik burada: model alanı eklendi
    weight = models.CharField(max_length=50)  # Değişiklik burada: weight alanı eklendi
    category = models.CharField(max_length=10)  # Değişiklik burada: category alanı eklendi
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    is_available = models.BooleanField(default=True)
    description = models.CharField(max_length=100)
