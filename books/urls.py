from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    path('book-list/', views.BookListView.as_view(), name="book_list"),
    path('book-detail/<int:pk>/', views.BookDetailView.as_view(), name="book_detail"),
    path('mypage/<int:pk>/', views.MyPageView.as_view(), name="mypage"),
    path('favorite-book/', views.favorite_book, name="favorite_book"),
    path('tag-add/<int:pk>', views.TagAddView.as_view(), name="tag_add"),
    path('bookshelf-add/<int:pk>', views.BookshelfAddView.as_view(), name="bookshelf_add"),
    path('bookshelf-edit/<int:pk>', views.BookshelfEditView.as_view(), name="bookshelf_edit"),
    path('profile-edit/<int:pk>', views.ProfileEditView.as_view(), name="profile_edit"),


]