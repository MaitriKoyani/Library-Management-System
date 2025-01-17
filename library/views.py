from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
# from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,logout
from django.contrib.auth.hashers import check_password,make_password
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
from .models import CustomTokenAuthentication
# from rest_framework.authtoken.models import Token
from .models import MemberToken,LibrarianToken
from rest_framework.response import Response
from rest_framework import status
from .models import Book,Member,History,Librarian
from .serializers import *
from .decorators import login_required,librarian_view_only
from django.utils.decorators import method_decorator
from datetime import datetime


# Create your views here.

def setsession(request):
    request.session['key1'] = 'value1'
    print(request.session['key1'],'set')
    return HttpResponse({'message':'session set'})
def getsession(request):
    print(request)
    print(request.session.items())
    print(request.session['key1'],'get')
    request.user=request.session['key1']
    print(request.user)
    return HttpResponse({'not':'1'})
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
    def post(self, request):
        data=request.data
        if data:
            member=Member.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = MemberSerializer(member)
            token = MemberToken.objects.filter(member=member).first()
            if token:
                token.delete()
            token = MemberToken.objects.create(member=member)
            login(request, member)
            return Response({'token':token.token,'member':serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message":"data not provided",'require':'name,email,password'}, status=status.HTTP_400_BAD_REQUEST)

class RegisterLibrarianView(APIView):
    def post(self, request):
        data=request.data
        if data:
            librarian=Librarian.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = LibrarianSerializer(librarian)
            token = LibrarianToken.objects.filter(librarian=librarian).first()
            if token:
                token.delete()
            token = LibrarianToken.objects.create(librarian=librarian)
            login(request, librarian)
            return Response({'token':token.token,'librarian':serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"message":"data not provided",'require':'name,email,password'}, status=status.HTTP_400_BAD_REQUEST)

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
                request.session['token'] = str(token.token)
                request.session['username'] = member.name
                request.session.set_expiry(3600)
                serializer = MemberTokenSerializer(token)
                print(serializer.data)
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif librarian:
            password = check_password(passwor, librarian.password)
            if password:    
                token = LibrarianToken.objects.filter(librarian=librarian).first()
                if token:
                    token.delete()
                token = LibrarianToken.objects.create(librarian=librarian)
                
                login(request, librarian)
                return Response({'token':token.token},status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@method_decorator(login_required, name='dispatch')
class LogoutView(APIView):
    def get(self, request):
        try:
            request.session.flush()
            logout(request)
            return Response({'message':'Successfully logged out'},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error':e},status=status.HTTP_400_BAD_REQUEST)

class BookList(APIView):
    def get(self, request):
        books = Book.objects.filter(is_book=True).all()
        serializer = BookSerializer(books,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    @method_decorator(login_required, name='dispatch')
    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(librarian_view_only, name='dispatch')
class BookDetail(APIView):
    def get_object(self, pk):
        try:
            return Book.objects.get(pk=pk,is_book=True)
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
            return Response({'message':'Book not found'},status=status.HTTP_404_NOT_FOUND)
        book.delete() # There is no deletion of book just is_active=False
        return Response({'message':'Book is deleted'},status=status.HTTP_204_NO_CONTENT)

@method_decorator(librarian_view_only, name='dispatch')
class MemberList(APIView):
    def get(self, request):
        print(request.user)
        members = Member.objects.filter(is_active=True).all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    
@method_decorator(librarian_view_only, name='dispatch')
class MemberDetail(APIView):
    def get_object(self, pk):
        try:
            return Member.objects.get(pk=pk,is_active=True)
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
            return Response({'message':'Member not found'},status=status.HTTP_404_NOT_FOUND)
        member.delete() # There is no deletion of member just is_active=False
        return Response({'message':'Member is deleted'},status=status.HTTP_204_NO_CONTENT)

@method_decorator(librarian_view_only, name='dispatch')
class HistoryList(APIView):
    def get(self, request,pk):
        try:
            issuedbooks = History.objects.all()
            serializer = HistorySerializer(issuedbooks, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message':'User is not logged in or invalid token'},status=status.HTTP_401_UNAUTHORIZED)

@method_decorator(login_required, name='dispatch')
class HistoryDetail(APIView):
    def post(self, request,pk):
        print(request.user)
        print(request.session.get('username'))
        user=request.session.get('username')
        member=Member.objects.filter(name=user).first()
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
    def get(self, request,pk): 
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
@method_decorator(login_required, name='dispatch')
class MemberHistory(APIView):
    def get_object(self,id):
        try:
            return History.objects.filter(member=id).all()
        except History.DoesNotExist as e:
            return Response({'error':e},status=status.HTTP_404_NOT_FOUND)

    def get(self, request):
        history = self.get_object(request.user.id)
        if history is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = HistorySerializer(history, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

@method_decorator(librarian_view_only, name='dispatch')
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
        if librarians is None:
            return Response({'message':'There are no librarian'},status=status.HTTP_200_OK)
        else:
            serializer = LibrarianSerializer(librarians, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
    

@method_decorator(librarian_view_only, name='dispatch')
class LibrarianDetail(APIView):
    def get_object(self, pk):
        try:
            return Librarian.objects.get(pk=pk,is_active=True)
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
            return Response({'message':'Librarian not found'},status=status.HTTP_404_NOT_FOUND)
        librarian.delete()
        return Response({'message':'Librarian is deleted'},status=status.HTTP_204_NO_CONTENT)