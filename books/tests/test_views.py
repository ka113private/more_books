from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy, reverse
from ..models import Book, Tag, BookTag
from ..views import BookDetailView

class LoggedInTestCase(TestCase):
    """各テストクラスで共通の事前準備処理をオーバライドした独自のTestCaseクラス"""

    def loginSetUp(self):
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

class TestBookListFromSearchView(LoggedInTestCase):
    """BookListFromSearchView用のテストクラス"""
    def setUp(self):
        self.loginSetUp()
        self.book1= Book.objects.create(title='Book1', author='Author1', description='Description1')
        self.book2 = Book.objects.create(title='Book2', author='Author2', description='Description2')
        self.url = reverse('books:book_list_from_search')

    def test_book_list_from_search(self):
        """書籍詳細ページが正しく表示されることを確認する。"""
        #書籍タイトルが検索対象に入っているか
        params = {'query': 'Book'}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('book_list.html')
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book2.title)
        #著者名が検索対象に入っているか
        params = {'query': 'Author'}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('book_list.html')
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book2.title)
        #書籍概要が検索対象に入っているか
        params = {'query': 'Description'}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('book_list.html')
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book2.title)
        #'Book1'で検索した時にBook2は結果表示されないか
        params = {'query': 'Book1'}
        response = self.client.get(self.url, params)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('book_list.html')
        self.assertContains(response, self.book1.title)
        self.assertNotContains(response, self.book2.title)

class TestBookListFromTagView(LoggedInTestCase):
    def setUp(self):
        self.loginSetUp()
        self.book1 = Book.objects.create(title='Book1', author='Author1', description='Description1')
        self.book2 = Book.objects.create(title='Book2', author='Author2', description='Description2')
        self.book3 = Book.objects.create(title='Book3', author='Author3', description='Description3')
        self.tag1 = Tag.objects.create(name='Tag1')
        self.booktag1 = BookTag.objects.create(book=self.book1, tag=self.tag1)
        self.booktag2 = BookTag.objects.create(book=self.book2, tag=self.tag1)

    def test_book_list_from_tag(self):
        #tag1というタグがついている書籍が正しく取得できているか。
        url = reverse('books:book_list_from_tag', kwargs={'pk': self.tag1.pk})
        response = self.client.get(url)
        self.assertTemplateUsed('book_list.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book2.title)
        self.assertNotContains(response, self.book3.title)

    def test_book_list_from_tag_with_invalid_id(self):
        url = reverse('books:book_list_from_tag', kwargs={'pk': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)



class TestBookDetailView(LoggedInTestCase):
    """BookDetailView用のテストクラス"""

    def setUp(self):
        self.loginSetUp()
        self.book = Book.objects.create(title='Book', author='Author', description='Description')
        self.url = reverse('books:book_detail',  kwargs={'pk': self.book.pk})

    def test_book_detail_view(self):
        "書籍詳細ページが正しく表示されることを検証する"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail.html')
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.book.author)
        self.assertContains(response, self.book.description)

    def test_book_detail_view_with_invalid_id(self):
        "不適切な書籍idを指定して書籍詳細ページにアクセスすると失敗することを検証する"
        url = reverse('books:book_detail',  kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class TestTagAddView(LoggedInTestCase):
    """TagAddView用のテストクラス"""

    def setUp(self):
        self.loginSetUp()
        self.book = Book.objects.create(title='Book', author='Author', description='Description')

    def test_add_tag_success(self):
        """タグ追加処理が成功することを検証する"""
        params = {'name':'テストタグ'}
        response = self.client.post(reverse_lazy('books:tag_add', kwargs={'pk':self.book.pk}), params)
        self.assertRedirects(response, reverse_lazy('books:book_detail', kwargs={'pk':self.book.pk}), status_code=302, target_status_code=200)
        # タグがデータベースに登録されたか確認
        self.assertEqual(Tag.objects.filter(name=params['name']).count(), 1)
        # 書籍タグがデータベースに追加されたか確認
        tag = Tag.objects.get(name=params['name'])
        self.assertEqual(BookTag.objects.filter(book=self.book, tag=tag).count(), 1)