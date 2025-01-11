from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.contrib.auth.hashers import check_password
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book,Member,History,Librarian
from .serializers import BookSerializer,MemberSerializer,HistorySerializer,LibrarianSerializer
from datetime import datetime

# Create your views here.

class RegisterMemberView(APIView):
    def post(self, request):
        serializer = MemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            login(request, serializer.instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def get(self, request):
        return Response({"status": "success"})
    def post(self, request):
        name = request.data.get('name')
        password = request.data.get('password')
        member = Member.objects.filter(name=name).first()
        librarian = Librarian.objects.filter(name=name).first()
        if member:
            password = check_password(password, member.password)
            login(request, member)
            return Response({"status": "success"})
        elif librarian:
            password = check_password(password, librarian.password)
            login(request, librarian)
            return Response({"status": "success"})
        return Response({"status": "failed"})

class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return Response({"status": "success"})


class BookList(APIView):
    def get(self, request):
        books = Book.objects.filter(is_book=True).all()
        print(books)
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
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
@login_required
class MemberList(APIView):
    def get(self, request):
        members = Member.objects.filter(is_user=True).all()
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

class HistoryList(APIView):
    def get(self, request):
        issuedbooks = History.objects.all()
        serializer = HistorySerializer(issuedbooks, many=True)
        return Response(serializer.data)

class HistoryDetail(APIView):
    def post(self, request,pk):
        if request.user.is_authenticated:
            member = request.user.id
            member = Member.objects.get(id=member)
            book = Book.objects.get(id=pk)
            if request.data['action'] == 'issue':
                action='issued'
                res = book.issue_book(member)
                if res:
                    return Response(status=status.HTTP_201_CREATED)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif request.data['action'] == 'return':
                action='returned'
                res = book.return_book(member)
                if res:
                    return Response(status=status.HTTP_201_CREATED)
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return redirect('login')        

class MemberHistory(APIView):
    def get_object(self, pk):
        try:
            return History.objects.filter(member=pk).all()
        except History.DoesNotExist:
            return None

    def get(self, request, pk):
        history = self.get_object(pk)
        if history is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = HistorySerializer(history)
        return Response(serializer.data)

class BookHistory(APIView):
    def get_object(self, pk):
        try:
            return History.objects.filter(book=pk).all() 
        except History.DoesNotExist:
            return None

    def get(self, request, pk):
        history = self.get_object(pk)
        if history is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = HistorySerializer(history)# many=True
        return Response(serializer.data)

class LibrarianList(APIView):
    def get(self, request):
        librarians = Member.objects.filter(is_active=True).first()
        serializer = LibrarianSerializer(librarians, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LibrarianSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LibrarianDetail(APIView):
    def get_object(self, pk):
        try:
            return Librarian.objects.get(pk=pk)
        except Librarian.DoesNotExist:
            return None

    def get(self, request, pk):
        librarian = self.get_object(pk)
        if librarian is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LibrarianSerializer(librarian)
        return Response(serializer.data)
    
    def put(self, request, pk):
        librarian = self.get_object(pk)
        if librarian is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LibrarianSerializer(librarian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        librarian = self.get_object(pk)
        if librarian is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        librarian.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)