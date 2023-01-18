from accounts.models import CustomUser
from django.db import models

class Books(models.Model):
    """書籍モデル"""
    user = models.ForeignKey(CustomUser, verbose_name='ユーザーID', on_delete=models.PROTECT)
    title = models.CharField(verbose_name='タイトル', max_length=50)
    author = models.CharField(verbose_name='著者', max_length=30)
    description = models.TextField(verbose_name='概要', blank=True, null=True)
    thumbnail_image = models.ImageField(verbose_name='サムネイル画像', blank=True, null=True)
    amazon_url = models.URLField(verbose_name='Amzazonリンク', blank=True, null=True)
    rakuten_url = models.URLField(verbose_name='Rakutenリンク', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='追加日時', auto_now=True)

    class Meta:
        verbose_name_plural='Books'

    def __str__(self):
        return self.title

class Tags(models.Model):
    """タグモデル"""
    name = models.CharField(verbose_name='タグ名', max_length=30)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural='Tags'

    def __str__(self):
        return self.name

class FavoriteBooks(models.Model):
    """お気に入り書籍"""
    user_id = models.ForeignKey(CustomUser, verbose_name='ユーザーID', on_delete=models.PROTECT)
    book_id = models.ForeignKey(Books, verbose_name='書籍ID', on_delete=models.PROTECT)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name='FavoriteBooks'

class BookTags(models.Model):
    """書籍タグ"""
    book_id = models.ForeignKey(Books, verbose_name='書籍ID', on_delete=models.PROTECT)
    tag_id = models.ForeignKey(Tags, verbose_name='タグID', on_delete=models.PROTECT)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name='BookTags'

class FavoriteTags(models.Model):
    """お気に入りタグ"""
    user_id = models.ForeignKey(CustomUser, verbose_name='ユーザーID', on_delete=models.PROTECT)
    booktag_id = models.ForeignKey(BookTags, verbose_name='書籍タグID', on_delete=models.PROTECT)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name='FavoriteTags'

class Bookshelf(models.Model):
    """本棚"""
    user_id = models.ForeignKey(CustomUser, verbose_name='ユーザーID', on_delete=models.PROTECT)
    book_id = models.ForeignKey(Books, verbose_name='書籍ID', on_delete=models.PROTECT)
    status = models.IntegerField(verbose_name='ステータス')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name='Booksshelf'