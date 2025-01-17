from functools import wraps
from django.http import JsonResponse
from rest_framework import status
from .models import CustomTokenAuthentication

def login_required(view_func):
    @wraps(view_func) 
    def wrapper(request, *args, **kwargs):
        if not request.user.id:
            try:
                print('enter')
                authentication = CustomTokenAuthentication()
                if authentication.authenticate(request):
                    user,auth = authentication.authenticate(request)
                else:
                    return JsonResponse({'error':'Login required '},status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                return JsonResponse({'error':'Login required ','error':str(e)},status=status.HTTP_401_UNAUTHORIZED) 
            request.user=user
            if not request.user:
                return JsonResponse({'error': 'Login required'}, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(request, *args, **kwargs)
    return wrapper
def librarian_view_only(view_func):
    @wraps(view_func) 
    def wrapper(request, *args, **kwargs):
        print(request.session.get('username'))
        try:
            authentication = CustomTokenAuthentication()
            if authentication.authenticate(request):
                user,auth = authentication.authenticate(request)
            else:
                return JsonResponse({'error':'Librarian Login required and only librarian can access'},status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return JsonResponse({'error':'Librarian Login required and only librarian can access','error':str(e)},status=status.HTTP_401_UNAUTHORIZED) 
        request.user=user
        if not request.user and not request.user.is_active:
            return JsonResponse({'error': 'Librarian Login required and only librarian can access'}, status=status.HTTP_401_UNAUTHORIZED)
        return view_func(request, *args, **kwargs)
    return wrapper
