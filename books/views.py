import logging

from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from .forms import InquiryForm, TagAddForm, BookshelfAddForm, ProfileEditForm, StatusChangeForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Book, FavoriteBook, BookTag, TagLike ,Tag, Bookshelf, CustomUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

logger = logging.getLogger(__name__)

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

class BookListView(LoginRequiredMixin, generic.ListView):
    """一覧ページ用View"""
    model = Book
    template_name = 'book_list.html'

    def get_queryset(self, **kwargs):
        queryset = Book.objects.order_by('-created_at')
        #検索機能
        query = self.request.GET.get('query')
        if query:
            #★タグ検索もできるようにする
            queryset = queryset.filter(
                Q(title__icontains=query)|Q(author__icontains=query)|Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        context['query'] = query

        return context

class BookListTagView(LoginRequiredMixin, generic.ListView):
    """タグボタンを押下したときに遷移する一覧ページ用View"""
    model = Book
    template_name = 'book_list.html'

    def get_queryset(self, **kwargs):
        tag_pk = self.kwargs['pk']
        tag = Tag.objects.get(pk=tag_pk)
        book_pk_list = BookTag.objects.filter(tag=tag).values_list('book', flat=True)
        book_list = Book.objects.filter(pk__in=list(book_pk_list))
        print(book_list)
        return book_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_pk = self.kwargs['pk']
        tag = Tag.objects.get(pk=tag_pk)
        context['query'] = "#" + tag.name

        return context

class MyListView(LoginRequiredMixin, generic.ListView):
    """My本棚ページ用のView"""
    model = Bookshelf
    template_name = 'my_list.html'

    def get_queryset(self, **kwargs):
        status = self.kwargs['status']
        bookshelf_list = Bookshelf.objects.filter(user=self.request.user, status=status)
        return bookshelf_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.kwargs['status']
        context['status'] = status

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

        #ログインユーザーが本棚に書籍を追加しているかどうか
        if Bookshelf.objects.filter(book=self.object, user=self.request.user).exists():
            context['is_add_bookshelf'] = True
        else:
            context['is_add_bookshelf'] = False
        #モーダル用フォーム
        context['tag_add_form'] = TagAddForm
        return context

class MyPageView(LoginRequiredMixin, generic.DetailView):
    """マイページ用View"""
    model = CustomUser
    template_name = "mypage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #プロフィール画像編集フォーム
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
        bookshelf.status = "読みたい" #読みたい状態(未読)として登録する
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
        #削除ボタンが押下された場合
        if "btn_delete" in self.request.POST:
            bookshelf = form.save(commit=False)
            target = Bookshelf.objects.get(pk=bookshelf.pk)
            target.delete()
            messages.success(self.request, '本棚から削除しました')
        else:
            bookshelf = form.save(commit=False)
            target = Bookshelf.objects.get(pk=bookshelf.pk)
            if (target.status=="読みたい"):
                bookshelf.status = "読書中"
            elif (target.status=="読書中"):
                bookshelf.status = "読了"
            bookshelf.save()
        return super().form_valid(form)

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

class RecommendListView(LoginRequiredMixin, generic.ListView):
    """ユーザーへのおすすめの書籍を一覧表示するView"""
    model = Book
    template_name = 'recommend_list.html'

    def get_queryset(self):
        #　すでに本棚に登録してある書籍以外の人気順リストを表示
        my_books = Bookshelf.objects.filter(user=self.request.user).values('book')
        popular_books = Book.objects\
            .annotate(favorite_count=Count('favoritebook'))\
            .order_by('-favorite_count')\
            .exclude(pk__in=my_books)
        return popular_books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #　新着の書籍：Bookモデルを最新順として取得
        new_books = Book.objects.order_by('-created_at')
        context['new_books'] = new_books
        #　自分がいいねした書籍タグをタグ名でまとめ、タグごとのいいね数を降順に並べる
        my_taglikes = TagLike.objects.filter(user=self.request.user)\
            .select_related()\
            .values('booktag__tag')\
            .annotate(count=Count('booktag__pk'))\
            .order_by('-count')
        recommend_dic = {}
        # いいねしたタグが付けられている書籍のlistを作成
        for taglike_dic in my_taglikes:
            tag = Tag.objects.get(pk=taglike_dic['booktag__tag'])
            booktags = BookTag.objects.filter(tag=tag).order_by('-created_at')
            related_books = []
            for booktag in booktags:
                related_books.append(booktag.book)
            recommend_dic[tag.name] = related_books
        context['recommend_dic'] = recommend_dic
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
    book_pk = request.POST.get('book_pk')#POSTメソッドのbodyに格納されているbook_pk（辞書型）を取得
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
    booktag_pk = request.POST.get('booktag_pk')#POSTメソッドのbodyに格納されているbooktag_pk（辞書型）を取得
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