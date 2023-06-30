from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy, reverse
from ..models import Book, Tag, BookTag, Category, SubCategory, Bookshelf

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

    def createModelSetup(self):
        """テスト実行前のモデル作成"""
        # カテゴリ作成
        self.categoryX = Category.objects.create(name='CategoryA')
        self.categoryY = Category.objects.create(name='CategoryB')
        # サブカテゴリ作成
        self.subcategoryA = SubCategory.objects.create(name='subcategory1', category=self.categoryX)
        self.subcategoryB = SubCategory.objects.create(name='subcategory2', category=self.categoryX)
        self.subcategoryC = SubCategory.objects.create(name='subcategory3', category=self.categoryY)
        self.subcategoryD = SubCategory.objects.create(name='subcategory4', category=self.categoryY)
        # 書籍作成
        self.book1 = Book.objects.create(title='Book1', author='Author1', description='Description1',
                                         sub_category=self.subcategoryA)
        self.book2 = Book.objects.create(title='Book2', author='Author2', description='Description2',
                                         sub_category=self.subcategoryA)
        self.book3 = Book.objects.create(title='Book3', author='Author3', description='Description3',
                                         sub_category=self.subcategoryA)
        self.book4 = Book.objects.create(title='Book4', author='Author4', description='Description4',
                                         sub_category=self.subcategoryA)
        self.book5 = Book.objects.create(title='Book5', author='Author5', description='Description5',
                                         sub_category=self.subcategoryA)
        self.book6 = Book.objects.create(title='Book6', author='Author6', description='Description6',
                                         sub_category=self.subcategoryA)
        self.book7 = Book.objects.create(title='Book7', author='Author7', description='Description7',
                                         sub_category=self.subcategoryB)
        self.book8 = Book.objects.create(title='Book8', author='Author8', description='Description8',
                                         sub_category=self.subcategoryC)
        self.book9 = Book.objects.create(title='Book9', author='Author9', description='Description9',
                                         sub_category=self.subcategoryD)

        # ユーザー作成
        self.user1 = get_user_model().objects.create_user(username='user1', email='test@gmail.com', password='user1')
        self.user2 = get_user_model().objects.create_user(username='user2', email='test@gmail.com', password='user2')
        self.user3 = get_user_model().objects.create_user(username='user3', email='test@gmail.com', password='user3')

class TestIndexView(LoggedInTestCase):
    """IndexView用のテストクラス"""
    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.url = reverse('books:index')

    def test_index_page(self):
        """インデックスページが正しく表示されることを確認する。"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('index.html')

class TestInquiryView(LoggedInTestCase):
    """InquiryView用のテストクラス"""

    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.url = reverse('books:inquiry')

    def test_index_page(self):
        """問い合わせページが正しく表示されることを確認する。"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('inquiry.html')

class TestBookListFromSearchView(LoggedInTestCase):
    """BookListFromSearchView用のテストクラス"""
    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.url = reverse('books:book_list_from_search')

    def test_book_list_from_search(self):
        """検索クエリにより書籍一覧ページが正しく表示されることを確認する。"""
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
    """BookListFromTagView用のテストクラス"""
    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.tag1 = Tag.objects.create(name='Tag1')
        self.booktag1 = BookTag.objects.create(book=self.book1, tag=self.tag1)
        self.booktag2 = BookTag.objects.create(book=self.book2, tag=self.tag1)

    def test_book_list_from_tag(self):
        """タグにより書籍一覧ページが正しく表示されることを確認する。"""
        #tag1というタグがついている書籍が正しく取得できているか。
        url = reverse('books:book_list_from_tag', kwargs={'pk': self.tag1.pk})
        response = self.client.get(url)
        self.assertTemplateUsed('book_list.html')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book2.title)
        self.assertNotContains(response, self.book3.title)

    def test_book_list_from_tag_with_invalid_id(self):
        """不適切なタグidを指定して書籍詳細ページにアクセスすると失敗することを検証する"""
        url = reverse('books:book_list_from_tag', kwargs={'pk': 999999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class TestBookDetailView(LoggedInTestCase):
    """BookDetailView用のテストクラス"""

    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.url = reverse('books:book_detail',  kwargs={'pk': self.book1.pk})

    def test_book_detail_view(self):
        "書籍詳細ページが正しく表示されることを検証する"
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail.html')
        self.assertContains(response, self.book1.title)
        self.assertContains(response, self.book1.author)
        self.assertContains(response, self.book1.description)

    def test_book_detail_view_with_invalid_id(self):
        "不適切な書籍idを指定して書籍詳細ページにアクセスすると失敗することを検証する"
        url = reverse('books:book_detail',  kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class TestTagAddView(LoggedInTestCase):
    """TagAddView用のテストクラス"""

    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()

    def test_add_tag_success(self):
        """タグ追加処理が成功することを検証する"""
        params = {'name':'テストタグ'}
        response = self.client.post(reverse_lazy('books:tag_add', kwargs={'pk':self.book1.pk}), params)
        self.assertRedirects(response, reverse_lazy('books:book_detail', kwargs={'pk':self.book1.pk}), status_code=302, target_status_code=200)
        # タグがデータベースに登録されたか確認
        self.assertEqual(Tag.objects.filter(name=params['name']).count(), 1)
        # 書籍タグがデータベースに追加されたか確認
        tag = Tag.objects.get(name=params['name'])
        self.assertEqual(BookTag.objects.filter(book=self.book1, tag=tag).count(), 1)

class TestExplorationView(LoggedInTestCase):
    """ExplorationView用のテストクラス"""
    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.url = reverse('books:exploration')

    def test_book_exploration(self):
        """ユーザーへのrecommendページが正しく取得できることを検証する"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_exploration.html')

class TestGetRelatedBooks(LoggedInTestCase):
    """get_related_booksメソッドテストクラス"""
    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.bookshelf1 = Bookshelf.objects.create(user=self.test_user, book=self.book1, status='読書中')
        self.bookshelf2 = Bookshelf.objects.create(user=self.test_user, book=self.book2, status='読書中')
        self.bookshelf3 = Bookshelf.objects.create(user=self.test_user, book=self.book7, status='読書中')
        self.url = reverse('books:get_related_books')

    def test_get_related_books(self):
        """ユーザーへのおすすめ書籍が正しく取得できることを検証する"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book3.title)
        self.assertContains(response, self.book4.title)
        self.assertContains(response, self.book5.title)
        self.assertContains(response, self.book6.title)
        # すでにmy本棚に登録済みなのでresponseには含まれないことを確認。
        self.assertNotContains(response, self.book1.title)
        self.assertNotContains(response, self.book2.title)
        # 別のサブカテゴリーなのでresponseには含まれないことを確認。
        self.assertNotContains(response, self.book7.title)
        self.assertNotContains(response, self.book8.title)
        self.assertNotContains(response, self.book9.title)

class TestGetNewBooks(LoggedInTestCase):
    """get_new_booksメソッドテストクラス"""
    def setUp(self):
        self.loginSetUp()
        self.createModelSetup()
        self.bookshelf1 = Bookshelf.objects.create(user=self.test_user, book=self.book1, status='読書中')
        self.bookshelf2 = Bookshelf.objects.create(user=self.test_user, book=self.book2, status='読書中')
        self.bookshelf3 = Bookshelf.objects.create(user=self.test_user, book=self.book7, status='読書中')
        self.url = reverse('books:get_new_books')

    def test_get_new_books(self):
        """ユーザーへのおすすめ書籍が正しく取得できることを検証する"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book8.title)
        self.assertContains(response, self.book9.title)
        # リクエストユーザーが登録しているサブカテゴリーなのでresponseには含まれないことを確認。
        self.assertNotContains(response, self.book1.title)
        self.assertNotContains(response, self.book2.title)
        self.assertNotContains(response, self.book7.title)
