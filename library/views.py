from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book,Member,IssuedBook
from .serializers import BookSerializer,MemberSerializer,IssuedBookSerializer

# Create your views here.

class BookList(APIView):
    def get(self, request):
        books = Book.objects.filter(is_book=True)
        
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetail(APIView):
    def get_object(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return None

    def get(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def put(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        book.delete() # There is no deletion of book just is_user=False
        return Response(status=status.HTTP_204_NO_CONTENT)


class MemberList(APIView):
    def get(self, request):
        members = Member.objects.filter(is_user=True)
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemberDetail(APIView):
    def get_object(self, pk):
        try:
            return Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return None

    def get(self, request, pk):
        member = self.get_object(pk)
        if member is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member)
        return Response(serializer.data)

    def put(self, request, pk):
        member = self.get_object(pk)
        if member is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        member = self.get_object(pk)
        if member is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        member.delete() # There is no deletion of member just is_user=False
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssuedBookList(APIView):
    def get(self, request):
        issuedbooks = IssuedBook.objects.filter(is_record=True)
        serializer = IssuedBookSerializer(issuedbooks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = IssuedBookSerializer(data=request.data) # get member id and book id and action
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssuedBookDetail(APIView):
    def get_object(self, pk):
        try:
            return IssuedBook.objects.get(pk=pk)
        except IssuedBook.DoesNotExist:
            return None

    def get(self, request, pk):
        issuedbook = self.get_object(pk)
        if issuedbook is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = IssuedBookSerializer(issuedbook)
        return Response(serializer.data)

    # def delete(self, request, pk):
    #     issuedbook = self.get_object(pk)
    #     if issuedbook is None:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #     # issuedbook.delete() # In your case, do not delete, set is_issued=False
    #     return Response(status=status.HTTP_204_NO_CONTENT)