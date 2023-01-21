from django.contrib import admin
from .models import Book, Tag, FavoriteTag, BookTag, FavoriteBook, Bookshelf
# Register your models here.

admin.site.register(Book)
admin.site.register(Tag)
admin.site.register(FavoriteBook)
admin.site.register(BookTag)
admin.site.register(FavoriteTag)
admin.site.register(Bookshelf)