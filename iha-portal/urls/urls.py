from django.urls import path
from . import views
from ocrs.urls import urlpatterns as ocrs_urls

urlpatterns = [
    
    path('/', views.index, name='index'),
 # Dealer Portal URLs
    path('dealer_home_page',views.dealer_home_page, name='dealer_home_page')
    path('dealer_login/', views.dealer_index, name='dealer_index'),
    path('dealer_home_page/', views.dealer_auth_view, name='dealer_home_page'),
    path('dealer_login/', views.dealer_login, name='dealer_login'),
    path('dealer_register/', views.dealer_register, name='dealer_register'),
    path('dealer_auth_view/', views.dealer_auth_view, name='dealer_auth_view'),
    path('dealer_logout_view/', views.dealer_logout_view, name='dealer_logout_view'),
    path('dealer_registration/', views.dealer_registration, name='dealer_registration'),
    
   
    # ... diğer dealer portalı URL'leri ...

    # Customer Portal URLs
path('index/', views.customer_index, name='index'),
   from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.customer_index, name='customer_index'),
    path('login/', views.customer_login, name='customer_login'),
 
    path('customer_home_page/', views.customer_auth_view, name='customer_home_page'),
    path('customer_login_failed/',viwes.customer_auth_view, name='customer_login_failed'),
    path('logout/', views.customer_logout_view, name='customer_login'),
    path('logout/', views.customer_logout_view, name='customer_logout_view'),
    path('register/', views.customer_register, name='customer_register'),
    path('registration/', views.customer_registration, name='customer_registration'),
    path('search/', views.customer_search, name='customer_search'),
    path('search_results/', views.customer_search_results, name='customer_search_results'),
    path('rent/', views.customer_rent_vehicle, name='customer_rent_vehicle'),
    path('confirmed/', views.customer_confirm, name='customer_confirm'),
    path('manage/', views.customer_manage, name='customer_manage'),
    path('update/', views.customer_update_order, name='customer_update_order'),
    path('delete/', views.customer_delete_order, name='customer_delete_order'),
]

    # ... diğer customer portalı URL'leri ...
]

# ocrs paketinin URL patternleri ekleniyor
urlpatterns += ocrs_urls
