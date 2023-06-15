from django.contrib import admin
from .models import (
    Book,
    Tag,
    TagLike,
    BookTag,
    FavoriteBook,
    Bookshelf,
    Category,
    SubCategory)
# Register your models here.

admin.site.register(Book)
admin.site.register(Tag)
admin.site.register(FavoriteBook)
admin.site.register(BookTag)
admin.site.register(TagLike)
admin.site.register(Bookshelf)
admin.site.register(Category)
admin.site.register(SubCategory)
