from rest_framework_simplejwt.authentication import JWTAuthentication

class CustomHeaderJWTAuthentication(JWTAuthentication):
    def get_header(self, request):
        header = request.META.get('HTTP_AUTHORIZE')
        return header.encode() if header else None
