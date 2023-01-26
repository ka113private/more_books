import logging

from django.urls import reverse_lazy
from django.shortcuts import render
from django.views import generic
from .forms import InquiryForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Book, FavoriteBook
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
        #ログインユーザーがいいねしているかどうか
        if self.object.favoritebook_set.filter(user_id=self.request.user).exists():
            context['is_user_favorite_book'] = True
        else:
            context['is_user_favorite_book'] = False

        return context

def favorite_book(request):
    book_pk = request.BOOK.get('book_pk')
    context = {
        'user':f'{request.user.username}'
    }
    book = get_object_or_404(Book, pk=book_pk)
    favorite = FavoriteBook.objects.filter(book_id = book, user_id = user)

    if favorite.exists():
        favorite.delete()
        context['method'] = 'delete'
    else:
        favorite.create(book_id = book, user_id = user)
        context['method'] = 'create'

    context['favorite_book_count'] = book.favoritebook_set.count()

    return JsonResponse(context)