from functools import wraps
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import status
from .models import CustomTokenAuthentication,Librarian
from rest_framework.decorators import authentication_classes

@authentication_classes([CustomTokenAuthentication])
def check_login(view_func):
    @wraps(view_func) 
    def wrapper(request, *args, **kwargs):
        
        print(request)
        print(request.user)
        if not request.user.id:
            try:  
                print('enter check login')
                authentication = CustomTokenAuthentication()
                if authentication.authenticate(request):
                    return redirect('/')
                else:
                    return view_func(request, *args, **kwargs)
            except Exception as e:
                print(e)
                return view_func(request, *args, **kwargs)
            
            return view_func(request, *args, **kwargs)
        
        return redirect('/')
    return wrapper

def login_required(view_func):
    @wraps(view_func) 
    def wrapper(request, *args, **kwargs):
        print(request.user,'login')
        if not request.user.id:
            try:
                print('enter login')
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
        if request.user :
            print('enter for librarian')
            lib = Librarian.objects.filter(name=request.user,is_active=True).first()
            print(lib)
            if not lib :
                try:
                    print('enter login librarian')
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
