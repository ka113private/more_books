import json
import logging

from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from .forms import InquiryForm, TagAddForm, BookshelfAddForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, FavoriteBook, BookTag, TagLike, Tag, Bookshelf, CustomUser, Category, Inquiry
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

logger = logging.getLogger(__name__)
NUM_BOOKS_TO_DISPLAY = 6 # インデックスページで表示する際の書籍の数
NUM_BOOKS_TO_DISPLAY_LISTPAGE = 30 # 一覧ページで表示する際の書籍の数
NUM_BOOKS_SEARCH = 1000 # 検索する書籍の書籍の数
NUM_RECOMMEND_BOOKS = 1000 # 提案する書籍の書籍の数
PER_FIRST = 0.5
PER_SECOND = 0.3
PER_THIRD = 0.1
PER_FORTH = 0.1



RECOMMEND_BOOKS = {}

class IndexView(generic.TemplateView):
    """インデックスページ用View"""
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = NUM_RECOMMEND_BOOKS
        return context

class AboutUsView(generic.TemplateView):
    """MoreBooks紹介用ページ用View"""
    template_name = "about_us.html"

class InquiryView(generic.CreateView):
    """問い合わせページ用View"""
    model = Inquiry
    template_name = "inquiry.html"
    form_class = InquiryForm

    def get_success_url(self):
        return reverse_lazy('books:inquiry')

    def form_valid(self, form):
        inquiry = form.save(commit=False)
        inquiry.user = self.request.user
        form.save()
        form.send_email()
        messages.success(self.request,'お問い合わせありがとうございます。お問い合わせ確認メールを送信致しました。')
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)

class BookListFromSearchView(LoginRequiredMixin, generic.ListView):
    """一覧ページ用View"""
    model = Book
    template_name = 'book_list.html'
    paginate_by = NUM_BOOKS_TO_DISPLAY_LISTPAGE
    count = 0

    def get_queryset(self, **kwargs):
        queryset = Book.objects.order_by('-created_at')
        self.count = queryset.count()
        #検索機能
        query = self.request.GET.get('query')
        if query:
            #★タグ検索もできるようにする
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(author__icontains=query) | Q(description__icontains=query)
            ).order_by("?")[:NUM_BOOKS_SEARCH]
            self.count = queryset.count()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        context['query'] = query
        # 検索結果の表示や選択したタグに紐づく書籍の表示をする際にhtml表示を少し変えるためにどのビューから生成されたのか判定するために以下を設定
        context['view_from'] = 'BookListFromSearchView'
        context['count'] = self.count

        return context

class BookListFromTagView(LoginRequiredMixin, generic.ListView):
    """タグボタンを押下したときに遷移する一覧ページ用View"""
    model = Book
    template_name = 'book_list.html'
    paginate_by = NUM_BOOKS_TO_DISPLAY_LISTPAGE
    count = 0

    def get_queryset(self, **kwargs):
        tag_pk = self.kwargs['pk']
        tag = get_object_or_404(Tag, pk=tag_pk)
        book_pk_list = BookTag.objects.filter(tag=tag).values_list('book', flat=True)
        book_list = Book.objects.filter(pk__in=list(book_pk_list)).order_by("?")
        self.count = book_list.count()
        return book_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_pk = self.kwargs['pk']
        tag = Tag.objects.get(pk=tag_pk)
        context['query'] = "#" + tag.name
        context['view_from']='BookListFromTagView'
        context['count'] = self.count
        return context

class BookListFromCategoryView(LoginRequiredMixin, generic.ListView):
    """Categoryを押下したときに遷移する一覧ページ用View"""
    model = Book
    template_name = 'book_list.html'
    paginate_by = NUM_BOOKS_TO_DISPLAY_LISTPAGE
    count = 0
    category = None
    sub_category = None

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        self.category = get_object_or_404(Category, pk=self.kwargs['pk'])
        queryset = queryset.filter(sub_category__category=self.category.pk).order_by("?")
        self.count = queryset.count()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.count
        context['query'] = self.category.name
        return context

class BookDetailView(LoginRequiredMixin, generic.DetailView):
    """書籍詳細ページ用View"""
    model = Book
    template_name = 'book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #ログインユーザーの書籍お気に入り状態を取得
        if self.object.favoritebook_set.filter(user=self.request.user).exists():
            context['is_user_favorite_book'] = True
        else:
            context['is_user_favorite_book'] = False
        #ログインユーザーのタグいいね状態を取得
        tag_list = self.object.booktags.all()
        tag_islike_dic = {}
        for booktag in tag_list:
            like_count = TagLike.objects.filter(booktag=booktag).count()
            if booktag.taglike_set.filter(user=self.request.user).exists():
                #tag_islike_dicのformat：{'booktag':(is_like, count)}
                tag_islike_dic[booktag] = (True, like_count)
            else:
                tag_islike_dic[booktag] = (False, like_count)
        context['tag_islike_dic'] = tag_islike_dic

        # ログインユーザーが本棚に書籍を追加しているかどうか
        if Bookshelf.objects.filter(book=self.object, user=self.request.user).exists():
            context['is_add_bookshelf'] = True
        else:
            context['is_add_bookshelf'] = False
        # モーダル用フォーム
        context['tag_add_form'] = TagAddForm
        return context

class TagAddView(LoginRequiredMixin, generic.FormView):
    """
    タグ追加処理用ビュー
    書籍詳細ページのフォームからpkを受け取り、モデル保存処理をする。
    すでにDBに保存済みのタグかどうかを判定し、未保存の場合はタグモデルへの保存及び書籍タグへの追加を行う。
    保存済みの場合は書籍タグのみ追加を行う。
    """
    model = Book
    form_class = TagAddForm

    def get_success_url(self):
        return reverse_lazy('books:book_detail',  kwargs={'pk': self.kwargs['pk']})

    def form_valid(self, form):
        # 既にtagモデルに同名のタグが保存されているか確認する。されていない場合はタグを保存
        pk = self.kwargs['pk']
        tag_name = form.cleaned_data.get('name')
        if (Tag.objects.filter(name=tag_name).exists()):
            target_tag = Tag.objects.get(name=tag_name)
        else:
            target_tag = form.save()
        book = Book.objects.get(pk=pk)
        if not (BookTag.objects.filter(book=book, tag=target_tag).exists()):
            booktag = BookTag(book=book, tag=target_tag)
            booktag.save()
            messages.success(self.request, 'タグを追加しました。')
        else:
            messages.success(self.request, 'すでにタグは登録済みです。')

        return super().form_valid(form)

class MybooksAddView(LoginRequiredMixin, generic.CreateView):
    """
    書籍をMy本棚に追加するビュー
    該当の書籍とログインユーザーをBookShelfモデルとしてDBに登録する。
    """
    model = Bookshelf
    form_class = BookshelfAddForm

    def get_success_url(self):
        return reverse_lazy('books:mybooks')

    def form_valid(self, form):
        bookshelf = form.save(commit=False)
        pk = self.kwargs['pk']
        bookshelf.user = self.request.user
        bookshelf.book = Book.objects.get(pk=pk)
        bookshelf.status = "読みたい" # 読みたい状態(未読)として登録する
        bookshelf.save()
        messages.success(self.request, '本棚に書籍を追加しました。')

        return super().form_valid(form)

class StatusDeleteView(LoginRequiredMixin, generic.DeleteView):
    """MyBooksの削除view"""
    model = Bookshelf
    template_name = 'mybooks_delete.html'

    def get_success_url(self):
        return reverse_lazy('books:mybooks')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, '本棚から書籍を削除しました。')
        return super().delete(request, *args, **kwargs)

class MybooksListView(LoginRequiredMixin, generic.ListView):
    """ユーザーのmy本棚を表示するView"""
    model = Book
    template_name = 'mybooks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Bookshelfテーブルの取得
        mybooks = Bookshelf.objects.select_related('book').filter(user=self.request.user).filter(status="読みたい")
        context['mybooks'] = mybooks
        #お気に入り書籍の取得
        favorite_books = FavoriteBook.objects.filter(user=self.request.user)
        context['favorite_books'] = favorite_books
        #bookタグの一覧を取得
        booktags = BookTag.objects.all()
        context['booktags'] = booktags
        return context

def favorite_for_book(request):
    """書籍へのお気に入り処理"""
    book_pk = request.POST.get('book_pk')# POSTメソッドのbodyに格納されているbook_pk（辞書型）を取得
    context = {
        'user': request.user.username
    }
    book = get_object_or_404(Book, pk=book_pk)
    favoriteBook= FavoriteBook.objects.filter(book=book, user=request.user)

    if favoriteBook.exists():
        favoriteBook.delete()
        context['method'] = 'delete'
    else:
        favoriteBook.create(book=book, user=request.user)
        context['method'] = 'create'

    return JsonResponse(context)

def like_for_tag(request):
    """書籍タグへのいいね処理"""
    booktag_pk = request.POST.get('booktag_pk')# POSTメソッドのbodyに格納されているbooktag_pk（辞書型）を取得
    context = {
        'user':request.user.username
    }
    booktag = get_object_or_404(BookTag, pk=booktag_pk)
    taglike= TagLike.objects.filter(booktag=booktag, user=request.user)

    if taglike.exists():
        taglike.delete()
        context['method'] = 'delete'
    else:
        taglike.create(booktag=booktag, user=request.user)
        context['method'] = 'create'

    context['like_for_tag_count'] = TagLike.objects.filter(booktag=booktag).count()

    return JsonResponse(context)

def add_mybooks(request):
    context = {
        'user': request.user.username
    }
    #postメソッドのbodyに格納されているのはjsonなので、変換をかける
    json_data = json.loads(request.body)
    book = json_data['book']
    is_like = json_data['is_like']
    is_last = json_data['is_last']
    if (is_like):
        book = get_object_or_404(Book, pk=book["id"])
        Bookshelf.objects.create(book=book, user=request.user, status='読みたい')
    if (is_last):
        context['exists'] = False
    return JsonResponse(context)

def not_add_mybooks(request):
    context = {
        'user': request.user.username
    }
    # postメソッドのbodyに格納されているのはjsonなので、変換をかける
    json_data = json.loads(request.body)
    book_list = json_data['books']
    # データベースに登録せずに先頭の書籍をlistから削除する
    book_list.pop(0)
    if (len(book_list) != 0):
        book_list_json = JsonResponse({'books': book_list})
        context['next_books'] = book_list_json.content.decode('utf-8')
        context['exists'] = True
    else:
        context['exists'] = False
    return JsonResponse(context)

def get_related_books(request):
    # ログインユーザーの好みに応じた提案書籍をDBから取得
    context = {
        'user': request.user.username
    }

    # my本棚にある書籍の一覧を取得
    library_id_list = Bookshelf.objects.filter(user=request.user).values_list('book_id')
    library_list = Book.objects.filter(id__in=library_id_list)

    # my本棚において書籍数が一番多いサブカテゴリを取得。
    my_categories = library_list.values('sub_category') \
        .annotate(count=Count('sub_category')) \
        .order_by('-count')

    if (len(my_categories) >= 3):
        first_cat = my_categories[0]['sub_category']
        second_cat = my_categories[1]['sub_category']
        third_cat = my_categories[2]['sub_category']
        # おすすめ書籍(該当のサブカテゴリに属する書籍でログインユーザーがmy本棚に追加していないランダムな書籍)のQuerySetを返す。
        qs1 = Book.objects.filter(sub_category=first_cat) \
                  .exclude(id__in=library_id_list) \
                  .order_by("?")[:(NUM_RECOMMEND_BOOKS * PER_FIRST)]
        qs2 = Book.objects.filter(sub_category=second_cat) \
                  .exclude(id__in=library_id_list) \
                  .order_by("?")[:(NUM_RECOMMEND_BOOKS * PER_SECOND)]
        qs3 = Book.objects.filter(sub_category=third_cat) \
                  .exclude(id__in=library_id_list) \
                  .order_by("?")[:(NUM_RECOMMEND_BOOKS * PER_THIRD)]
        qs4 = Book.objects.all().order_by("?")[:(NUM_RECOMMEND_BOOKS * PER_FORTH)]
        related_books = qs1.union(qs2, qs3, qs4, all=True).order_by("?")
    else:
        related_books = Book.objects.all().order_by("?")[:NUM_RECOMMEND_BOOKS]

    # JsonResponseに格納する
    related_books_list = list(related_books.values())
    if (len(related_books_list) != 0):
        context['recommend_exists'] = True
        related_books_list_json = JsonResponse({'books': related_books_list})
        context['recommend_books'] = related_books_list_json.content.decode('utf-8')
    else:
        context['recommend_exists'] = False
    return JsonResponse(context)