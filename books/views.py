import logging

from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from .forms import InquiryForm, TagAddForm, BookshelfAddForm, ProfileEditForm, BookshelfEditForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, FavoriteBook, BookTag, TagLike ,Tag, Bookshelf, CustomUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count


logger = logging.getLogger(__name__)

class IndexView(generic.TemplateView):
    template_name = "index.html"

class InquiryView(generic.FormView):
    template_name = "inquiry.html"
    form_class = InquiryForm
    success_url = reverse_lazy('books:inquiry')

    def form_valid(self, form):
        form.send_email()
        messages.success(self.request,'メッセージを送信しました')
        logger.info('Inquiry sent by {}'.format(form.cleaned_data['name']))
        return super().form_valid(form)

class BookListView(LoginRequiredMixin, generic.ListView):
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
            if booktag.taglike_set.filter(user=self.request.user).exists():
                tag_islike_dic[booktag] = True
            else:
                tag_islike_dic[booktag] = False
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
    model = CustomUser
    template_name = "mypage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #ログインユーザーのほしい書籍
        want_list = Bookshelf.objects.filter(user=self.request.user, status=1)
        want_dic = {}
        for want in want_list:
            if FavoriteBook.objects.filter(user=self.request.user, book=want.book).exists():
                want_dic[want] = True
            else:
                want_dic[want] = False
        context['want_dic'] = want_dic

        # ログインユーザーの読書中書籍
        reading_list = Bookshelf.objects.filter(user=self.request.user, status=2)
        reading_dic = {}
        for reading in reading_list:
            if FavoriteBook.objects.filter(user=self.request.user, book=reading.book).exists():
                reading_dic[reading] = True
            else:
                reading_dic[reading] = False
        context['reading_dic'] = reading_dic

        # ログインユーザーの読了書籍
        read_list = Bookshelf.objects.filter(user=self.request.user, status=3)
        read_dic = {}
        for read in read_list:
            if FavoriteBook.objects.filter(user=self.request.user, book=read.book).exists():
                read_dic[read] = True
            else:
                read_dic[read] = False
        context['read_dic'] = read_dic
        #プロフィール画像編集フォーム
        context['profile_edit_form']=ProfileEditForm
        #本棚の書籍のステータス編集フォーム
        context['bookshelf_edit_form'] = BookshelfEditForm
        return context

class TagAddView(LoginRequiredMixin, generic.CreateView):
    """
    タグ追加ビュー
    書籍詳細ページのフォームからpkを受け取り、モデル保存処理をする。
    すでにDBに保存済みのタグかどうかを判定し、未保存の場合はタグモデルへの保存及び書籍タグへの追加を行う。
    保存済みの場合は書籍タグのみ追加を行う。
    """
    model = Book
    form_class = TagAddForm
    """★詳細ページに遷移できるように修正"""
    success_url = reverse_lazy('books:book_list')

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

class BookshelfAddView(LoginRequiredMixin, generic.CreateView):
    """
    書籍をMy本棚に追加するビュー
    該当の書籍とログインユーザーをBookShelfモデルとしてDBに登録する。
    """
    model = Bookshelf
    form_class = BookshelfAddForm

    def get_success_url(self):
        return reverse_lazy('books:mypage', kwargs={'pk':self.request.user.pk})

    def form_valid(self, form):
        bookshelf = form.save(commit=False)
        pk = self.kwargs['pk']
        bookshelf.user = self.request.user
        bookshelf.book = Book.objects.get(pk=pk)
        bookshelf.status = 1 #読みたい状態(未読)として登録する
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

class BookshelfEditView(LoginRequiredMixin, generic.UpdateView):
    """本棚更新用のview"""
    model = Bookshelf
    form_class = BookshelfEditForm

    def get_success_url(self):
        if 'book_detail_button' in self.request.POST:
            print('test2')
            bookshelf = Bookshelf.objects.get(pk=self.kwargs['pk'])
            return reverse_lazy('books:book_detail', kwargs={'pk': bookshelf.book.pk})
        else:
            bookshelf = Bookshelf.objects.get(pk=self.kwargs['pk'])
            return reverse_lazy('books:mypage', kwargs={'pk': self.request.user.pk})


    def form_valid(self, form):
        if 'move_to_reading_button' in self.request.POST:
            bookshelf = form.save(commit=False)
            bookshelf.status = 2
            bookshelf.save()
            return super().form_valid(form)
        elif 'move_to_read_button' in self.request.POST:
            bookshelf = form.save(commit=False)
            bookshelf.status = 3
            bookshelf.save()
            return super().form_valid(form)
        else:
            print('test')
            return super().form_valid(form)

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

def favorite_book(request):
    book_pk = request.BOOK.get('book_pk')
    context = {
        'user':f'{request.user.username}'
    }
    book = get_object_or_404(Book, pk=book_pk)
    favorite = FavoriteBook.objects.filter(book = book, user = user)

    if favorite.exists():
        favorite.delete()
        context['method'] = 'delete'
    else:
        favorite.create(book = book, user = user)
        context['method'] = 'create'

    context['favorite_book_count'] = book.favoritebook_set.count()

    return JsonResponse(context)