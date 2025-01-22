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
from django.contrib.sessions.models import Session
from .models import Book,Member,History,Librarian
from .serializers import *
from .decorators import login_required,librarian_view_only,check_login
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime


# Create your views here.

def setcookietoken(token):
    expires = datetime.utcnow() + timedelta(days=1)
    response = Response()
    response.set_cookie(
        'token',
        token.token,
        expires=expires,
        httponly=True,
        secure=False,#make true when in production
        samesite='Lax',
        path='/'
    )
    return response

@method_decorator(check_login, name='dispatch')
class RegisterMemberView(APIView):
    def post(self, request):
        data=request.data
        if data:
            member=Member.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = MemberSerializer(member)
            token = MemberToken.objects.create(member=member)
            res = setcookietoken(token)
            res.status_code = status.HTTP_201_CREATED
            res.data = serializer.data
            return res
        return Response({"message":"data not provided",'require':'name,email,password'}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(check_login, name='dispatch')
class RegisterLibrarianView(APIView):
    def post(self, request):
        data=request.data
        if data:
            librarian=Librarian.objects.create(
                name=data['name'],
                email=data['email'],
                password=make_password(data['password']),)
            serializer = LibrarianSerializer(librarian)
            
            token = LibrarianToken.objects.create(librarian=librarian)
            res = setcookietoken(token)
            res.status_code = status.HTTP_201_CREATED
            res.data = serializer.data
            return res
        return Response({"message":"data not provided",'require':'name,email,password'}, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(check_login, name='dispatch')
class LoginView(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        try:
            print('enter token check')
            try:
                user = request.data.get('name')
            except Exception as e:
                print(e)
                return None
            muser = Member.objects.filter(name=user).first()
            luser = Librarian.objects.filter(name=user).first()
            mtoken = MemberToken.objects.filter(member=muser).first()
            ltoken = LibrarianToken.objects.filter(librarian=luser).first()
            if mtoken:
                res = Response({'message':'Already logged in other browser'},status=status.HTTP_400_BAD_REQUEST)
                return res
            elif ltoken:
                res = Response({'message':'Already logged in other browser'},status=status.HTTP_400_BAD_REQUEST)
                return res
            else:
                name = request.data.get('name')
                passwor = request.data.get('password')
                member = Member.objects.filter(name=name).first()
                librarian = Librarian.objects.filter(name=name).first()
                
                if librarian:
                    password = check_password(passwor, librarian.password)
                    if password:    
                        
                        token = LibrarianToken.objects.create(librarian=librarian)
                        res = setcookietoken(token)
                        res.status_code = status.HTTP_200_OK
                        context={'message':'Successfully logged in'}
                        res.data = context
                        return res
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                elif member:
                    
                    password = check_password(passwor, member.password)
                    if password:
                        
                        token = MemberToken.objects.create(member=member)
                        res = setcookietoken(token)
                        res.status_code = status.HTTP_200_OK
                        context={'message':'Successfully logged in'}
                        res.data = context
                        return res
                    return Response(status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_404_NOT_FOUND)
    
        except Exception as e:
            name = request.data.get('name')
            passwor = request.data.get('password')
            member = Member.objects.filter(name=name).first()
            librarian = Librarian.objects.filter(name=name).first()
            
            if librarian:
                password = check_password(passwor, librarian.password)
                if password:    
                    
                    token = LibrarianToken.objects.create(librarian=librarian)
                    res = setcookietoken(token)
                    res.status_code = status.HTTP_200_OK
                    context={'message':'Successfully logged in'}
                    res.data = context
                    return res
                return Response(status=status.HTTP_400_BAD_REQUEST)
            elif member:
                
                password = check_password(passwor, member.password)
                if password:
                    
                    token = MemberToken.objects.create(member=member)
                    res = setcookietoken(token)
                    res.status_code = status.HTTP_200_OK
                    context={'message':'Successfully logged in'}
                    res.data = context
                    return res
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_404_NOT_FOUND)
    
@method_decorator(login_required, name='dispatch')
class LogoutView(APIView):
    def get(self, request):
        try:
            print(request.user,'logout')
            res = Response({'message':'Successfully logged out'},status=status.HTTP_200_OK)
            token = request.COOKIES.get('token')
            if token:
                mtoken = MemberToken.objects.filter(token=token).first()
                if mtoken:
                    mtoken.delete()
                    
                ltoken = LibrarianToken.objects.filter(token=token).first()
                if ltoken:
                    ltoken.delete()
                    
            res.delete_cookie('token')
            return res
        except Exception as e:
            return Response({'error':e},status=status.HTTP_400_BAD_REQUEST)

listofemails = []

@method_decorator(check_login, name='dispatch')
class forgotpassword(APIView):
    def get(self, request):

        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        email = request.data.get('email')
        member = Member.objects.filter(email=email).first()
        librarian = Librarian.objects.filter(email=email).first()
        subject = 'Password Reset Request'
        message = 'You have requested to reset your password. Click the link below to set a new password:\n\n' + 'http://127.0.0.1:8000/resetpassword/'
        recipient_email = email
        if member or librarian:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL, 
                    [recipient_email], 
                    fail_silently=False 
                )
                listofemails.append(recipient_email)
                return Response({'success': 'Email sent successfully'})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else :
            return Response({'error': 'User not found of this email'}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(check_login, name='dispatch')
class resetpassword(APIView):
    def get(self, request):
        return Response(status=status.HTTP_200_OK)
    def post(self, request):
        newpassword = request.data.get('newpassword')
        confirmpassword = request.data.get('confirmpassword')
        email = listofemails[0]
        if newpassword == confirmpassword:
            print('right')
            member = Member.objects.filter(email=email).first()
            librarian = Librarian.objects.filter(email=email).first()
            if member:
                member.password = make_password(newpassword)
                member.save()
                listofemails.clear()
                print('set')
                return Response({'success': 'Password reset successfully'},status=status.HTTP_200_OK)
            elif librarian:
                librarian.password = make_password(newpassword)
                librarian.save()
                listofemails.clear()
                return Response({'success': 'Password reset successfully'},status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class BookList(APIView):
    def get(self, request):
        print(request)
        print('book',request.user)
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
    def get(self, request):
        try:
            print('history',request.user)
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
        print('history member',request.user)
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