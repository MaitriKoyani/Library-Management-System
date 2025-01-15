from django.shortcuts import render,redirect
# from django.http import HttpResponse,JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.contrib.auth.hashers import check_password,make_password
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from .models import CustomTokenAuthentication
# from rest_framework.authtoken.models import Token
from .models import MemberToken,LibrarianToken
from rest_framework.response import Response
from rest_framework import status
from .models import Book,Member,History,Librarian
from .serializers import BookSerializer,MemberSerializer,HistorySerializer,LibrarianSerializer
from datetime import datetime

# Create your views here.

class RegisterMemberView(APIView):
    def post(self, request):
        data=request.data
        if data:
            member=Member.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = MemberSerializer(member)
            login(request, serializer.instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        name = request.data.get('name')
        passwor = request.data.get('password')
        member = Member.objects.filter(name=name).first()
        librarian = Librarian.objects.filter(name=name).first()
        if member:
            password = check_password(passwor, member.password)
            if password:
                token = MemberToken.objects.filter(member=member).first()
                if token:
                    token.delete()
                
                token = MemberToken.objects.create(member=member)
                login(request, member)
                return Response({'token':token.token},status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif librarian:
            password = check_password(password, librarian.password)
            if password:    
                token = LibrarianToken.objects.filter(librarian=librarian).first()
                if token:
                    token.delete()
                token = LibrarianToken.objects.get_or_create(librarian=librarian)
                login(request, librarian)
                return Response({'token':token.token},status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)

class LogoutView(APIView):
    def get(self, request):
        token = request.auth
        if token:
            token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)


class BookList(APIView):
    def get(self, request):
        books = Book.objects.filter(is_book=True).all()
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
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = self.get_object(pk)
        if book is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        book.delete() # There is no deletion of book just is_user=False
        return Response(status=status.HTTP_204_NO_CONTENT)

class MemberList(APIView):
    def get(self, request):
        members = Member.objects.filter(is_user=True).all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request):
        data=request.data
        if data:
            member=Member.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = MemberSerializer(member)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response({"message":"data not provided",'require':'name,email,password'}, status=status.HTTP_400_BAD_REQUEST)

class MemberDetail(APIView):
    def get_object(self, pk):
        try:
            return Member.objects.get(pk=pk,is_user=True)
        except Member.DoesNotExist:
            return None

    def get(self, request, pk):
        member = self.get_object(pk)
        if member is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self, request, pk):
        member = self.get_object(pk)
        if member is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = MemberSerializer(member, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        member = self.get_object(pk)
        if member is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        member.delete() # There is no deletion of member just is_user=False
        return Response(status=status.HTTP_204_NO_CONTENT)

class HistoryList(APIView):
    def get(self, request):
        print(request.user.id)
        if request.user.id:
            issuedbooks = History.objects.all()
            serializer = HistorySerializer(issuedbooks, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return Response({'message':'User is not logged in'},status=status.HTTP_401_UNAUTHORIZED)


class HistoryDetail(APIView):

    def post(self, request,pk):
        member=Member.objects.filter(name=request.user).first()
        if member:
            book = Book.objects.filter(id=pk).first()
            if request.data['action'] == 'issue' and book!=None:
                action='issued'
                res = book.issue_book(member)
                if res:
                    return Response({'message':'Book is issued'},status=status.HTTP_201_CREATED)
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif request.data['action'] == 'return' and book!=None:
                action='returned'
                msg,res = book.return_book(member)
                if res:
                    return Response({'message':msg},status=status.HTTP_201_CREATED)
                return Response({'message':msg},status=status.HTTP_200_OK)
            return Response({'message':'Book not found'},status=status.HTTP_404_NOT_FOUND)
        return Response({'message':'Member not found'},status=status.HTTP_401_UNAUTHORIZED)      
    def get(self, request): 
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class BookHistory(APIView):
    def get_object(self, pk):
        try:
            return History.objects.filter(book=pk).all() 
        except History.DoesNotExist as e:
            return Response({'error':e},status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        history = self.get_object(pk)
        if history is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = HistorySerializer(history,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class LibrarianList(APIView):
    def get(self, request):
        librarians = Librarian.objects.filter(is_active=True).first()
        serializer = LibrarianSerializer(librarians, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def post(self, request):
        data=request.data
        if data:
            member=Librarian.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = LibrarianSerializer(member)
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
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        librarian = self.get_object(pk)
        if librarian is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LibrarianSerializer(librarian, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        librarian = self.get_object(pk)
        if librarian is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        librarian.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)