from django.urls import path
from library import views

urlpatterns = [
    path('books/', views.BookList().as_view(), name='book-list'),
    path('books/<int:pk>/', views.BookDetail().as_view(), name='book-detail'),
    path('members/', views.MemberList, name='member-list'),
    path('members/<int:pk>/', views.MemberDetail().as_view(), name='member-detail'),
    path('history/', views.HistoryList().as_view(), name='history-list'),
    path('history/<int:pk>/', views.HistoryDetail().as_view(), name='history-detail'),# for issue or return book
    path('member/<int:pk>/', views.MemberHistory().as_view(), name='member-history'),
    path('book/<int:pk>/', views.BookHistory().as_view(), name='book-history'),
    path('librarian/', views.LibrarianList().as_view(), name='librarian-list'),
    path('librarian/<int:pk>/', views.LibrarianDetail().as_view(), name='librarian-detail'),
    path('login/', views.LoginView().as_view(), name='login'),
    path('logout/', views.LogoutView().as_view(), name='logout'),
]