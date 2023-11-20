import json
import logging

from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from .forms import InquiryForm, TagAddForm, BookshelfAddForm, ProfileEditForm, StatusChangeForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, FavoriteBook, BookTag, TagLike, Tag, Bookshelf, CustomUser, SubCategory
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

logger = logging.getLogger(__name__)
NUM_BOOKS_TO_DISPLAY = 6 # インデックスページで表示する際の書籍の数
NUM_BOOKS_TO_DISPLAY_LISTPAGE = 30 # 一覧ページで表示する際の書籍の数
NUM_BOOKS_SEARCH = 1000 # 検索する書籍の書籍の数
NUM_RELATED_BOOKS = 1000 # 提案する書籍の書籍の数

RECOMMEND_BOOKS = {}

class IndexView(generic.TemplateView):
    """インデックスページ用View"""
    template_name = "index.html"

class InquiryView(generic.FormView):
    """問い合わせページ用View"""
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('books:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request,'メッセージを送信しました')
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
            )[:NUM_BOOKS_SEARCH]
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
        book_list = Book.objects.filter(pk__in=list(book_pk_list))
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
    sub_category = None

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset()
        self.sub_category = get_object_or_404(SubCategory, pk=self.kwargs['pk'])
        queryset = queryset.filter(sub_category=self.sub_category.pk)
        self.count = queryset.count()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count'] = self.count
        context['query'] = self.sub_category.name
        return context

class BookListFromCustomView(LoginRequiredMixin, generic.ListView):
    """カスタム書籍一覧ページ用のView"""
    model = Book
    template_name = 'book_list.html'
    paginate_by = NUM_BOOKS_TO_DISPLAY_LISTPAGE

    def get_queryset(self, **kwargs):
        self.custom = self.kwargs['custom']
        book_list = Book.objects.all()
        if (self.custom == 'new_arrivals'):
            book_list = book_list.order_by('-created_at')[:NUM_BOOKS_SEARCH]
        elif (self.custom == 'popular'):
            book_list = book_list.annotate(favorite_count=Count('favoritebook'))\
                .order_by('-favorite_count')[:NUM_BOOKS_SEARCH]
        return book_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if (self.custom == 'new_arrivals'):
            context['query'] = '新着書籍'
        elif (self.custom == 'popular'):
            context['query'] = '人気書籍'
        context['count'] = NUM_BOOKS_SEARCH
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

class MyPageView(LoginRequiredMixin, generic.DetailView):
    """マイページ用View"""
    model = CustomUser
    template_name = "mypage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # プロフィール画像編集フォーム
        context['profile_edit_form']=ProfileEditForm

        return context

class TagAddView(LoginRequiredMixin, generic.CreateView):
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
        tag = form.save(commit=False)
        if not (Tag.objects.filter(name=tag.name).exists()):
            tag.save()
        target_tag = Tag.objects.get(name=tag.name)
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

class ProfileEditView(LoginRequiredMixin, generic.UpdateView):
    """プロフィール画像更新用のview"""
    model = CustomUser
    form_class = ProfileEditForm

    def get_success_url(self):
        return reverse_lazy('books:mypage', kwargs={'pk': self.request.user.pk})

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'プロフィール画像を更新しました')
        return super().form_valid(form)

class StatusChangeView(LoginRequiredMixin, generic.UpdateView):
    """MyBooksのステータス変更のview"""
    model = Bookshelf
    form_class = StatusChangeForm

    def get_success_url(self):
        return reverse_lazy('books:mybooks')

    def form_valid(self, form):
        bookshelf = form.save(commit=False)
        target = Bookshelf.objects.get(pk=bookshelf.pk)
        if (target.status=="読みたい"):
            bookshelf.status = "読書中"
        elif (target.status=="読書中"):
            bookshelf.status = "読了"
        bookshelf.save()
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

class FeedbackView(LoginRequiredMixin, generic.UpdateView):
    """読了の際にユーザーの読書の感想をタグいいねでフィードバックしてもらうView"""

    def get_success_url(self):
        return reverse_lazy('books:mybooks')

    def post(self, request, *args, **kwargs):
        checks_value = request.POST.getlist('booktags')
        taglikes = TagLike.objects.filter(user=self.request.user)
        booktags = BookTag.objects.all()
        #チェックボックスでチェックが入っている項目に関してはいいねとしてみなす。
        for value in checks_value:
            booktag = booktags.get(pk=value)
            if not taglikes.filter(booktag=booktag).exists():
                taglike = TagLike(user=self.request.user, booktag=booktag)
                taglike.save()
        #ステータスを読了にする。
        bookshelf = Bookshelf.objects.get(pk=self.kwargs['pk'])
        bookshelf.status = "読了"
        bookshelf.save()
        #★mybooksページに遷移させたい。
        return render(request, 'index.html')

class ExplorationView(LoginRequiredMixin, generic.TemplateView):
    """ユーザーへのおすすめの書籍を一覧表示するView"""
    model = Book
    template_name = 'book_exploration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        new_arrivals = Book.objects.order_by('-created_at')[:NUM_BOOKS_TO_DISPLAY]
        context['new_arrivals'] = new_arrivals
        popular = Book.objects.annotate(favorite_count=Count('favoritebook')) \
                        .order_by('-favorite_count')[:NUM_BOOKS_TO_DISPLAY]
        context['popular'] = popular

        return context

class MybooksListView(LoginRequiredMixin, generic.ListView):
    """ユーザーのmy本棚を表示するView"""
    model = Book
    template_name = 'mybooks.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Bookshelfテーブルの取得
        all = Bookshelf.objects.filter(user=self.request.user)
        mybooks_want = all.filter(status="読みたい")
        mybooks_reading = all.filter(status="読書中")
        mybooks_read = all.filter(status="読了")
        context['mybooks_want'] = mybooks_want
        context['mybooks_reading'] = mybooks_reading
        context['mybooks_read'] = mybooks_read
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
    book_list = json_data['books']
    #先頭の書籍についてBookshelfテーブルにstatus「読みたい」として登録する。登録後listから削除する
    book = get_object_or_404(Book, pk=book_list[0]["id"])
    Bookshelf.objects.create(book=book, user=request.user, status='読みたい')
    book_list.pop(0)
    if (len(book_list) != 0):
        book_list_json = JsonResponse({'books': book_list})
        context['next_books']=book_list_json.content.decode('utf-8')
        context['exists']= True
    else:
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
    # 「知見を深める」を選択した場合：ログインユーザーの興味があるサブカテゴリに属する人気の本を取得
    context = {
        'user': request.user.username
    }

    # my本棚にある書籍の一覧を取得
    library_id_list = Bookshelf.objects.filter(user=request.user).values_list('book_id')
    library_list = Book.objects.filter(id__in=library_id_list)

    # my本棚において書籍数が一番多いサブカテゴリを取得。
    favorite_category_dict = library_list.values('sub_category') \
        .annotate(count=Count('sub_category')) \
        .order_by('-count') \
        .first()

    # おすすめ書籍(該当のサブカテゴリに属する書籍でログインユーザーがmy本棚に追加していないランダムな書籍)のQuerySetを返す。
    if (len(favorite_category_dict) != 0):
        related_books = Book.objects.filter(sub_category=favorite_category_dict['sub_category']) \
                            .exclude(id__in=library_id_list)\
                            .order_by("?")[:NUM_RELATED_BOOKS]
    else:
        related_books = Book.objects.all().order_by("?")[:NUM_RELATED_BOOKS]

    # JsonResponseに格納する
    related_books_list = list(related_books.values())
    if (len(related_books_list) != 0):
        context['recommend_exists'] = True
        related_books_list_json = JsonResponse({'books': related_books_list})
        context['recommend_books'] = related_books_list_json.content.decode('utf-8')
    else:
        context['recommend_exists'] = False
    return JsonResponse(context)

def get_new_books(request):
    #「知見を広げる」を選択した場合：ログインユーザーがこれまで読んだことのないサブカテゴリに属する本を取得
    context = {
        'user': request.user.username
    }
    #  本棚にある書籍の全てのサブカテゴリを取得
    library_id_list = Bookshelf.objects.filter(user=request.user) \
        .values_list('book_id')
    library_list = Book.objects.filter(id__in=library_id_list)
    my_categories = library_list.values('sub_category') \
        .annotate(count=Count('sub_category')) \
        .order_by('-count') \
        .values_list('sub_category')

    # おすすめ書籍(ログインユーザーがmy本棚に追加していないサブカテゴリの書籍のうちランダムな書籍)のQuerySetを返す。
    new_books = Book.objects.all()\
                    .exclude(sub_category__in=my_categories) \
                    .order_by("?")[:NUM_RELATED_BOOKS]

    # 　JsonResponseに格納する
    new_books_list = list(new_books.values())
    if (len(new_books_list) != 0):
        context['recommend_exists'] = True
        new_books_list_json = JsonResponse({'books': new_books_list})
        context['recommend_books'] = new_books_list_json.content.decode('utf-8')
    else:
        context['recommend_exists'] = False
    return JsonResponse(context)