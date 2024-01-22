from accounts.models import CustomUser
from django.db import models


class Category(models.Model):
    """書籍カテゴリモデル"""
    name = models.CharField(verbose_name='カテゴリ名', max_length=50)

    class Meta:
        verbose_name_plural = 'Category'

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    """書籍サブカテゴリ"""
    name = models.CharField(verbose_name='サブカテゴリ名', max_length=50)
    category = models.ForeignKey(
        Category,
        verbose_name='カテゴリ',
        on_delete=models.CASCADE,
        related_name='category_subcategory')

    class Meta:
        verbose_name_plural = 'SubCategory'

    def __str__(self):
        return self.name


class Book(models.Model):
    """書籍モデル"""
    title = models.CharField(verbose_name='タイトル', max_length=200)
    author = models.CharField(verbose_name='著者', max_length=100)
    description = models.TextField(verbose_name='概要',
                                   blank=True,
                                   null=True)
    thumbnail_image = models.ImageField(verbose_name='サムネイル画像',
                                        blank=True,
                                        null=True)
    sub_category = models.ForeignKey(SubCategory,
                                     verbose_name='サブカテゴリ',
                                     on_delete=models.CASCADE)
    amazon_url = models.URLField(verbose_name='Amzazonリンク',
                                 blank=True,
                                 null=True)
    rakuten_url = models.URLField(verbose_name='Rakutenリンク',
                                  blank=True,
                                  null=True)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='追加日時', auto_now=True)
    registered_date = models.CharField(verbose_name='登録月', max_length=6)

    class Meta:
        verbose_name_plural = 'Book'

    def __str__(self):
        return self.title

class Tag(models.Model):
    """タグモデル"""
    name = models.CharField(verbose_name='タグ名', max_length=30)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name_plural='Tag'

    def __str__(self):
        return self.name

class FavoriteBook(models.Model):
    """お気に入り書籍"""
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, verbose_name='書籍', on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name='FavoriteBook'

    def __str__(self):
        return self.book.title


class BookTag(models.Model):
    """書籍タグ"""
    book = models.ForeignKey(Book, related_name='booktags', verbose_name='書籍', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, verbose_name='タグ', on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name='BookTag'

    def __str__(self):
        return self.tag.name

class TagLike(models.Model):
    """書籍タグいいね"""
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    booktag = models.ForeignKey(BookTag, verbose_name='書籍タグ', on_delete=models.CASCADE)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name='TagLike'

    def __str__(self):
        return self.booktag.tag.name

class Bookshelf(models.Model):
    """本棚"""
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, verbose_name='書籍', on_delete=models.CASCADE, related_name='bookshelves')
    status = models.CharField(verbose_name='ステータス', max_length=10)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='更新日時', auto_now=True)

    class Meta:
        verbose_name='Bookshelf'

    def __str__(self):
        return self.book.title

class Inquiry(models.Model):
    """問い合わせ"""
    user = models.ForeignKey(CustomUser, verbose_name='ユーザー', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='名前', max_length=30)
    email = models.EmailField(verbose_name='メールアドレス')
    title = models.CharField(verbose_name='タイトル', max_length=30)
    message = models.TextField(verbose_name='お問い合わせ内容', max_length=2000)
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)

    class Meta:
        verbose_name='Inquiry'

    def __str__(self):
        return self.name + '　：　' + self.title

class Topic(models.Model):
    """Topic"""
    title = models.CharField(verbose_name='タイトル', max_length=40)
    content = models.TextField(verbose_name='内容', max_length=2000)
    is_open = models.BooleanField(verbose_name='オープン（画面表示）する場合チェックをいれる')
    created_at = models.DateTimeField(verbose_name='作成日時', auto_now_add=True)
    update_at = models.DateTimeField(verbose_name='追加日時', auto_now=True)

    class Meta:
        verbose_name = 'Topic'

    def __str__(self):
        return self.title
