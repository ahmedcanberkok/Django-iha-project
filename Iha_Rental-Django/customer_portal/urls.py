from django.urls import path
from customer_portal.views import *
from django.urls import path
urlpatterns = [
   path('index/', index),
    path('login/', login),
    path('auth/', auth_view),
    path('logout/', logout_view),
    path('register/', register),
    path('registration/', registration),
    path('search/', search),
    path('search_results/', search_results),
    path('rent/', rent_vehicle),
    path('confirmed/', confirm),
    path('manage/', manage),
    path('update/', update_order),
    path('delete/', delete_order),
]
