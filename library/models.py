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
        history = History.objects.filter(member=member, book=self, action='returned').last()
        issue = History.objects.filter(member=member, book=self, action='issued').last()
        if not history and issue:
            self.available_copies += 1
            self.save()
            History.objects.create(member=member, book=self, action='returned', return_date=timezone.now())
            msg='Book is returned'
            return msg , True
        elif not issue:
            msg='Book is not issued'
            return msg , False
        msg='Book is already returned'
        return msg , False


    def delete(self, *args, **kwargs):
        self.is_book = False
        self.total_copies = 0
        self.available_copies = 0
        self.save()

    def __str__(self):
        return self.title
# class MemberManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email field must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
    
    
class Member(models.Model):
    name = models.CharField(max_length=100,unique=True)
    password = models.CharField(max_length=100,null=False)
    email = models.EmailField(unique=True)
    is_user=models.BooleanField(default=True)
    last_login = models.DateTimeField(blank=True, null=True)

    # objects = MemberManager()

    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = []

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
        # Get the token from the Authorization header
        token = request.headers.get('Authorization')

        if not token:
            return None  # No token is provided, proceed with normal processing

        if token.startswith('Token '):
            token = token[6:]  # Remove 'Bearer ' prefix

        try:
            # Check if the token exists in the MemberToken model
            token = MemberToken.objects.filter(token=token).first()

            return (token.member, token)
        except MemberToken.DoesNotExist:
            try:
                token = LibrarianToken.objects.filter(token=token).first()
                return (token.librarian, token)
            except LibrarianToken.DoesNotExist:
                raise AuthenticationFailed('Invalid or expired token.')