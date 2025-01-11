from django.urls import path
from library import views

urlpatterns = [
    path('books/', views.BookList.as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetail.as_view(), name='book-detail'),
    path('members/', views.MemberList.as_view(), name='member-list'),
    path('members/<int:pk>/', views.MemberDetail.as_view(), name='member-detail'),
    path('issued-books/', views.IssuedBookList.as_view(), name='issued-book-list'),
    path('issued-books/<int:pk>/', views.IssuedBookDetail.as_view(), name='issued-book-detail'),
]