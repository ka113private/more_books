from accounts.models import CustomUser
from django.db import models

class Books(models.Model):
    """書籍モデル"""
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.PROTECT)
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