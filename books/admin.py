from django.contrib import admin
from .models import Book, Tag, TagLike, BookTag, FavoriteBook, Bookshelf, Category, SubCategory, Inquiry
# Register your models here.


class InquiryAdmin(admin.ModelAdmin):
    fields = ('user', 'name', 'email', 'title', 'message', 'created_at', )
    readonly_fields = ('created_at', )


admin.site.register(Book)
admin.site.register(Tag)
admin.site.register(FavoriteBook)
admin.site.register(BookTag)
admin.site.register(TagLike)
admin.site.register(Bookshelf)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Inquiry, InquiryAdmin)
