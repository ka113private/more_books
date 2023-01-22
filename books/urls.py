from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('book-list/', views.BookListView.as_view(), name="book_list"),
    path('book-detail/<int:pk>/', views.BookDetailView.as_view(), name="book_detail"),
]