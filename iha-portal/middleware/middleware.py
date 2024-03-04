# middleware.py

from django_brutebuster.middleware import BruteBusterMiddleware

class CustomBruteBusterMiddleware(BruteBusterMiddleware):
    def get_username(self, request):
        # Kullanıcı adını almak için bu metodu geçersiz kılın
        return request.POST.get('username')
