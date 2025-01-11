from django.contrib import admin
from .models import Member,Book,History,Librarian

# Register your models here.

admin.site.register(Librarian)
admin.site.register(Member)
admin.site.register(Book)
admin.site.register(History)
