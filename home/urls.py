from django.urls import path
from django.urls import path
from home.views import *
from dealer_portal import *
from customer_portal import *

urlpatterns = [
    path('',home_page),

]
