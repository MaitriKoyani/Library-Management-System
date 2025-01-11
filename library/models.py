from django.db import models
from datetime import timedelta
from django.contrib.auth.hashers import make_password

# Create your models here.

class Librarian(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active=models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(Librarian, self).save(*args, **kwargs)

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
        history = History.objects.filter(member=member, book=self, action='issued').last()
        if history:
            self.available_copies += 1
            self.save()
            History.objects.create(member=member, book=self, action='returned')
            return True
        return False


    def delete(self, *args, **kwargs):
        self.is_user = False
        self.total_copies = 0
        self.available_copies = 0
        self.save()

    def __str__(self):
        return self.title

class Member(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100, blank=True)
    email = models.EmailField(unique=True)
    is_user=models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super(Member, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_user = False
        self.save()

    def __str__(self):
        return self.name
    
class History(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    issue_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        
        if not self.return_date:
            self.return_date = self.issue_date + timedelta(days=10)
        super(History, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.name} - {self.action} - {self.book.title}"