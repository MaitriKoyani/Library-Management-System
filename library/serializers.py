from rest_framework import serializers
from .models import *

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title','author','isbn','publication_date','total_copies','available_copies']

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['name','email']

class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['member','action','book','issue_date','return_date']

class LibrarianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Librarian
        fields = ['name','email']

class MemberTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberToken
        fields = ['token']

