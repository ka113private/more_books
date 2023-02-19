from django.urls import path
from . import views

app_name = 'books'
urlpatterns = [
    # トップページ遷移用URL
    path('', views.IndexView.as_view(), name="index"),
    #問い合わせページ遷移用URL
    path('inquiry/', views.InquiryView.as_view(), name="inquiry"),
    #書籍一覧ページ遷移用URL
    path('book-list/', views.BookListView.as_view(), name="book_list"),
    path('book-list-tag/<int:pk>/', views.BookListTagView.as_view(), name="book_list_tag"),
    path('my-list/<int:status>', views.MyListView.as_view(), name="my_list"),
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
    #読了書籍の感想を記入するフォームの入力結果処理URL
    path('feedback/<int:pk>', views.FeedbackView.as_view(), name="feedback"),
    #プロフィール編集フォームの入力結果処理URL
    path('profile-edit/<int:pk>', views.ProfileEditView.as_view(), name="profile_edit"),
    #本を探すページ遷移用URL
    path('recommend', views.RecommendListView.as_view(), name="recommend"),
    #My本棚ページ遷移用URL
    path('mybooks', views.MybooksListView.as_view(), name="mybooks"),
    #書籍タグへのいいね非同期処理URL
    path('like-for-tag', views.like_for_tag, name="like_for_tag")

]