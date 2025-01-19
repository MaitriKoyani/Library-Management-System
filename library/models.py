from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import uuid
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


# Create your models here.



class Librarian(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active=models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        self.is_active = False
        self.save()

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    publication_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=0)
    available_copies = models.PositiveIntegerField(default=0)
    is_book=models.BooleanField(default=True)
    
    def issue_book(self, member):
        if self.available_copies > 0:
            self.available_copies -= 1
            self.save()
            History.objects.create(member=member, book=self, action='issued')
            return True
        return False

    def return_book(self, member):
        history = History.objects.filter(member=member, book=self).last()
        action = history.action
        if action == 'issued':
            self.available_copies += 1
            self.save()
            History.objects.create(member=member, book=self, action='returned', return_date=timezone.now())
            msg='Book is returned'
            return msg , True
        elif action == 'returned':
            msg='Book is already returned'
            return msg , False
        msg='Book is not issued'
        return msg , False


    def delete(self, *args, **kwargs):
        self.is_book = False
        self.total_copies = 0
        self.available_copies = 0
        self.save()

    def __str__(self):
        return self.title
    
    
class Member(models.Model):
    name = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=100,null=False)
    email = models.EmailField(unique=True)
    is_active=models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

    @property
    def is_authenticated(self):
        return True

    def delete(self, *args, **kwargs):
        self.is_user = False
        self.save()

    def __str__(self):
        return self.name
    
class History(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    issue_date = models.DateField(default=now)
    return_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        
        if not self.return_date:
            self.return_date = self.issue_date + timedelta(days=10)
        super(History, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.name} - {self.action} - {self.book.title}"
    
class MemberToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name="auth_token")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.member.name}"
    
class LibrarianToken(models.Model):
    id = models.AutoField(primary_key=True)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    librarian = models.OneToOneField(Librarian, on_delete=models.CASCADE, related_name="auth_token")
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Token for {self.librarian.name}"

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        print('enter auth')
        
        token = request.COOKIES.get('token')
        
        if not token:
            return None  
        if token.startswith('Token '):
            token = token[6:]  
        
        try:
            
            mtoken = MemberToken.objects.filter(token=token).first()
            if mtoken:
                return (mtoken.member, mtoken)
            else:
                ltoken = LibrarianToken.objects.filter(token=token).first()
                if ltoken:
                    return (ltoken.librarian, ltoken)
                else:
                    return None

        except Exception as e:  
            raise AuthenticationFailed('Invalid or expired token.',e)
        
# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.hashers import check_password

# class MemberAuthBackend(BaseBackend):
#     def authenticate(self, request, username=None, password=None):
#         try:
            
#             member = Member.objects.get(name=username)
#             librarian = Librarian.objects.get(name=username)
#             if member:
#                 if check_password(password, member.password):  # Use hashed passwords
#                     return member
#             elif librarian:
#                 if check_password(password, librarian.password):  # Use hashed passwords
#                     return librarian
#         except Member.DoesNotExist or Librarian.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             print('enter in back',)
#             return Member.objects.get(pk=user_id)
            
#         except Member.DoesNotExist :
#             return None

from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Check for token in the request (header, cookie, etc.)
        print('enter auth')
        
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
