from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MaxLengthValidator

from dealer_portal.models import Dealer, Area, Vehicles

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(validators=[MinLengthValidator(10), MaxLengthValidator(13)], max_length=13)
    area = models.ForeignKey(Area, on_delete=models.PROTECT)

class Orders(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    dealer = models.ForeignKey(Dealer, on_delete=models.PROTECT)
    rent = models.CharField(max_length=8)
    vehicle = models.ForeignKey(Vehicles, on_delete=models.PROTECT)
    days = models.CharField(max_length=3)
    is_complete = models.BooleanField(default=False)
