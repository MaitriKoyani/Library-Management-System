from django.db import models

# Create your models here.

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=13)
    publication_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=0)
    available_copies = models.PositiveIntegerField(default=0)
    is_book=models.BooleanField(default=True)
    issuebook_id=models.PositiveIntegerField(default=0)
    def delete(self, *args, **kwargs):
        self.is_user = False
        self.total_copies = 0
        self.available_copies = 0
        self.save()

    def __str__(self):
        return self.title

class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    is_user=models.BooleanField(default=True)
    issuebook_id=models.PositiveIntegerField(default=0)
    def delete(self, *args, **kwargs):
        self.is_user = False
        self.save()

    def __str__(self):
        return self.name
    
class IssuedBook(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE,)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    is_record=models.BooleanField(default=True)
    issue_date = models.DateField()
    return_date = models.DateField()

    def delete(self, *args, **kwargs):
        self.is_record = False
        self.save()

    def __str__(self):
        return f"{self.member.name} - {self.action} - {self.book.title}"