from django.contrib import admin
from .models import Books, Tags, FavoriteTags, BookTags, FavoriteBooks, Bookshelf
# Register your models here.

admin.site.register(Books)
admin.site.register(Tags)
admin.site.register(FavoriteBooks)
admin.site.register(BookTags)
admin.site.register(FavoriteTags)
admin.site.register(Bookshelf)