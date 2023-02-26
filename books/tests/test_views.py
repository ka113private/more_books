from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy

from ..models import Book, Tag, BookTag

class LoggedInTestCase(TestCase):
    """各テストクラスで共通の事前準備処理をオーバライドした独自のTestCaseクラス"""

    def setUp(self):
        """テストメソッド実行前の事前設定"""

        # テストユーザーのパスワード
        self.password = 'test-pass'

        # 各インスタンスメソッドで使うテスト用ユーザーを作成し、インスタンス変数に格納しておく
        self.test_user = get_user_model().objects.create_user(
            username='test-user',
            email='test@gmail.com',
            password=self.password
        )

        # テスト用ユーザーでログインする
        self.client.login(email=self.test_user.email, password=self.password)

class TestTagAddView(LoggedInTestCase):
    """TagAddView用のテストクラス"""

    def test_add_tag_success(self):
        """タグ追加処理が成功することを検証する"""

        # テスト用書籍データ作成
        book = Book.objects.create(title='テスト書籍タイトル', author='テスト著者', description='テスト書籍概要')

        # Postパラメータ
        params = {'name':'テストタグ'}

        # 新規タグ追加処理実行
        response = self.client.post(reverse_lazy('books:tag_add', kwargs={'pk':book.pk}), params)

        # 書籍詳細ページへのリダイレクトを検証
        self.assertRedirects(response, reverse_lazy('books:book_detail', kwargs={'pk':book.pk}))

        # タグがデータベースに登録されたか確認
        self.assertEqual(Tag.objects.filter(name='テストタグ').count(), 1)

        # 書籍タグがデータベースに追加されたか確認
        tag = Tag.objects.get(name='テストタグ')
        self.assertEqual(BookTag.objects.filter(book=book, tag=tag).count(), 1)


