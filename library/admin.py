from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Librarian)
admin.site.register(Member)
admin.site.register(Book)
admin.site.register(History)
admin.site.register(MemberToken)
admin.site.register(LibrarianToken)
