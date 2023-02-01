import logging

from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from .forms import InquiryForm, TagAddForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, FavoriteBook, BookTag, TagLike ,Tag, Bookshelf, CustomUser
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

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

    def get_queryset(self):
        #　☆検索機能はそのうち実装する。
        book_list = Book.objects.order_by('-created_at')
        return book_list

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
        #モーダル用のフォーム
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

        # ログインユーザーの読了書籍F
        read_list = Bookshelf.objects.filter(user=self.request.user, status=3)
        read_dic = {}
        for read in read_list:
            if FavoriteBook.objects.filter(user=self.request.user, book=read.book).exists():
                read_dic[read] = True
            else:
                read_dic[read] = False
        context['read_dic'] = read_dic


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