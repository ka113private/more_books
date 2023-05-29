from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    # トップページ遷移用URL
    path('', views.IndexView.as_view(), name="index"),
    #問い合わせページ遷移用URL
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    #書籍一覧ページ遷移用URL
    path('book-list-from-search/', views.BookListFromSearchView.as_view(), name="book_list_from_search"),
    path('book-list-from-tag/<int:pk>/', views.BookListFromTagView.as_view(), name="book_list_from_tag"),
    path('book-list-from-custom/<slug:custom>', views.BookListFromCustomView.as_view(), name="book_list_from_custom"),
    #書籍詳細ページ遷移用URL
    path('book-detail/<int:pk>/', views.BookDetailView.as_view(), name="book_detail"),
    #マイページ遷移用URL
    path('mypage/<int:pk>/', views.MyPageView.as_view(), name="mypage"),
    #タグを追加するフォームの入力結果処理URL
    path('tag-add/<int:pk>', views.TagAddView.as_view(), name="tag_add"),
    #My本棚へ書籍を追加するフォームの入力結果処理URL
    path('mybooks-add/<int:pk>', views.MybooksAddView.as_view(), name="mybooks_add"),
    #My本棚の書籍のステータスを変更するフォームの入力結果処理URL
    path('status-change/<int:pk>', views.StatusChangeView.as_view(), name="status_change"),
    #My本棚の書籍削除するフォームの入力結果処理URL
    path('status-delete/<int:pk>', views.StatusDeleteView.as_view(), name="status_delete"),
    #読了書籍の感想を記入するフォームの入力結果処理URL
    path('feedback/<int:pk>', views.FeedbackView.as_view(), name="feedback"),
    #プロフィール編集フォームの入力結果処理URL
    path('profile-edit/<int:pk>', views.ProfileEditView.as_view(), name="profile_edit"),
    #本を探すページ遷移用URL
    path('exploration', views.ExplorationView.as_view(), name="exploration"),
    #My本棚ページ遷移用URL
    path('mybooks', views.MybooksListView.as_view(), name="mybooks"),
    #書籍へのお気に入り非同期処理URL
    path('favorite-for-book', views.favorite_for_book, name="favorite_for_book"),
    #書籍タグへのいいね非同期処理URL
    path('like-for-tag', views.like_for_tag, name="like_for_tag"),
    #おすすめ書籍をmy本棚に追加する際に非同期処理URL
    path('add-mybooks', views.add_mybooks, name="add_mybooks"),
    #おすすめ書籍をmy本棚に追加しない際に非同期処理URL
    path('not-add-mybooks', views.not_add_mybooks, name="not_add_mybooks"),
    #おすすめ書籍(知見を深める)の取得（非同期処理）URL
    path('get-related-books', views.get_related_books, name="get_related_books"),
    #おすすめ書籍(知見を広げる)の取得（非同期処理）URL
    path('get-new-books', views.get_new_books, name="get_new_books")


]