from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from library.models import MemberToken,LibrarianToken

class CustomTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check for token in the request (header, cookie, etc.)
        print('enter auth middle')
        
        token = request.COOKIES.get('token')
        
        if not token:
            return None  
        if token.startswith('Token '):
            token = token[6:]  
        
        try:
            
            mtoken = MemberToken.objects.filter(token=token).first()
            if mtoken:
                request.user = mtoken.member
            else:
                ltoken = LibrarianToken.objects.filter(token=token).first()
                if ltoken:
                    request.user = ltoken.librarian
                else:
                    return None

        except Exception as e:  
            raise AuthenticationFailed('Invalid or expired token.',e)
