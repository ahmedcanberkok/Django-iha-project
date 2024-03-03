from django.urls import path, include
from . import views
from ocrs.urls import urlpatterns as ocrs_urls

urlpatterns = [
 # Dealer Portal URLs
    path('dealer_index/', views.dealer_index, name='dealer_index'),
    path('dealer_login/', views.dealer_login, name='dealer_login'),
    path('dealer_register/', views.dealer_register, name='dealer_register'),
    path('dealer_auth_view/', views.dealer_auth_view, name='dealer_auth_view'),
    path('dealer_logout_view/', views.dealer_logout_view, name='dealer_logout_view'),
    path('dealer_registration/', views.dealer_registration, name='dealer_registration'),
    path('add_vehicle/', views.add_vehicle, name='add_vehicle'),    
    path('manage_vehicles/', views.manage_vehicles, name='manage_vehicles'),
    # ... diğer dealer portalı URL'leri ...

    # Customer Portal URLs
    path('customer_index/', views.customer_index, name='customer_index'),
    path('customer_login/', views.customer_login, name='customer_login'),
    path('customer_register/', views.customer_register, name='customer_register'),
    path('customer_auth_view/', views.customer_auth_view, name='customer_auth_view'),
    path('customer_logout_view/', views.customer_logout_view, name='customer_logout_view'),
    path('customer_registration/', views.customer_registration, name='customer_registration'),
    # ... diğer customer portalı URL'leri ...
]

# ocrs paketinin URL patternleri ekleniyor
urlpatterns += ocrs_urls
