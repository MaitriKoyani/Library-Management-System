from rest_framework import serializers
from .models import Book,Member,History,Librarian

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id','title','author','isbn','publication_date','total_copies','available_copies']

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id','name','email']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = '__all__'

class LibrarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Librarian
        fields = ['id','name','email']

