# MoreBooks README
## 開発ログ
### 〇2023/1/19
個人開発の進め方や技術的な内容を記すために開発ログを記し始める。\
＜時間＞\
7:00～7:30, 20:00～20:30\
＜実績＞
- Books\Model.pyを定義し、マイグレーションまで実行。
- NativeCamp30分受講\

＜所感＞
- Modelで定義したものをマイグレーションするだけでDB構築できるのがDjangoの良いところだが、実際にマイグレーション処理でどのようにSQLを発行しているのかは知っておく必要がある。
- この個人開発以外にも毎日英会話30分（復習要）、週に一回はLeetCode1問を解くことを習慣づけたい。

### 〇2023/1/20
＜時間＞\
5:30～7:00　17:00～19:00（新幹線移動中）\
＜実績＞
- book-listページのurlとViewの定義まで完了
- book-listページの表示まで完了
- NativeCamp30分受講

＜所感＞
- ListViewやBootstrapを自分で調べながら実装していくのは楽しい。これを仕事に出来たらいいなと思う。
- フリーランサーは当たり前に複数のポートフォリオを作成している。
- 開発を始める前には必ずローカルの作業ブランチを確認。
- Django adminサイトからデータを追加するとローカルのDBも正しく更新される。
- Djangoのモデルはなるべく単数形がよさそう（adminサイト上だとなぜかsがついているものとついていないものが存在している）
- book_list.htmlはviewよりbook_listを受け取り、そのhtmlファイル上でfor分によりlist表示するところまで理解できた。ただし、bookモデルのurlを正しく使用する方法がわからなかったので調査が必要。
- Djangoの主な遷移としてはhtmlのボタン要素などに{% url 'book:book_list '%}のように逆引きのURLを設定し、そのボタンを押下するとurl.pyからそれぞれのViewに処理が渡される。各viewではmodelを取得し、再度template_nameで設定したhtmlにmodelの情報を付加し、ブラウザに表示する流れ。

### 〇2023/1/21
＜時間＞\
8:30～9:00\
＜実績＞
- book-listページに画像を表示できるようにした。

＜所感＞
- 画像が入ると一気に見栄えが良くなる。

### 〇2023/1/22
＜時間＞\
21:00～23:15（新幹線移動中）\
＜実績＞
- book-detailページのurlとView、htmlの作成まで完了

＜所感＞
- htmlにおいて画像のパス（mediaまでのパス）の定義がよくわからない。book_list.htmlでは../media、book_detailでは../../mediaというようになり、違いがわからない。
- <i class="bi-cart me-1"></i>のようにBootstrapのアイコンを利用できるが、それらはプロジェクトのどこに保存されているのだろう。
- detailViewにおいて副問い合わせをするためにはmodels.pyでrelated_nameというものを設定する。
- Booktagのお気に入り数の表示の仕方とタグを押下したときに検索画面への遷移とお気に入り登録の両方ができるようにしたい。どのようにやるか調査及び検討が必要。


### 〇2023/1/25
＜時間＞\
6:30～7:30、20:30～21:30\
＜実績＞
- book-detailページにイイね機能の実装（ハートマークを表示するところまで）

＜所感＞
- viewのqueryset（特に副問い合わせ）の仕方は良く調べる必要がありそう。
- related_nameはなるべくmodelに定義したほうがよさそう。Book.favoritebook_set.allでもできるが、外部キーが二つ以上ある場合にエラーになるので定義したほうが安全。

### 〇2023/1/26
＜時間＞\
6:15～7:30
＜実績＞
- book-detailページに書籍お気に入り機能の実装（表示するところまで）

＜所感＞
- Ajaxとはクライアントとサーバー間の非同期通信を実現する技術。ページの再読み込みなしでページの一部を書き換えることができる。 非同期通信とは同期通信とは異なり、Webブラウザからサーバにリクエストしてから別の処理をすることができる。
  - ①AjaxはAsynchronous JavaScript And XMLの略。クライアントからサーバへのリクエストにはJavaScriptの組み込みオブジェクトであるXMLHttpRequestを使用。
  - ②Ajaxにおいてサーバからのレスポンス形式はXMLやJSONが多い。（近年はJSONメイン ）
  - ③DOM（書き換える場所を指定するAPI）を用いて、サーバからのレスポンスをもとにページの再読み込みなしでページの一部を書き換えることができる。
- related_nameはなるべくmodelに定義したほうがよさそう。Book.favoritebook_set.allでもできるが、外部キーが二つ以上ある場合にエラーになるので定義したほうが安全。
- 明日は書籍タグいいね機能とマイページ、検索機能を実装したい。

### 〇2023/1/27
  ＜時間＞\
  6:15～7:30
  ＜実績＞
- book-detailページにタグいいね機能の実装

＜所感＞
- 「AttributeError at /book-detail/2/ 'Book' object has no attribute 'booktag_set'」が出るときはviewにただしくmodelがimportされているかをチェックする。
- {% ～ %}タグ内で変数を使う方法で少し戸惑った。Qiitaの「【Django】{% static %}タグ内で変数を使う方法」を参考にした。→withタグとaddタグを使えばよいことを発見。
- withタグ、addタグの使い方のために「Djangoのテンプレートで文字列を連結する方法」を参照。とくにtemplate内で文字と数値(pk)を加算するためにはbooktag.pk|slugifyとASCIIに変換する必要があるので注意

### 〇2023/1/29
  ＜時間＞\
  21:00～23:30
  ＜実績＞
- book-detailページにタグいいね機能の実装（表示するところまで）
- mypageに自分のプロフィール画像を表示するところまで

＜所感＞
- 結局、書籍タグいいねを表示させるのに2日かかった。解決法としてはcontentにdic形式で値を持たせたが、そのときのKeyをBooktagモデル、valueをいいね状態（bool）で管理した。うまくいったのはよかったが、タグ名表示のために{{booktag.tag_id.name}}としたが、booktagモデルからnameまでを表示できるのが よくわからない。

### 〇2023/1/29
  ＜時間＞\
  21:00～23:30
  ＜実績＞
- mypageに本棚テーブルからのデータを表示するところまで。お気に入り表示も

＜所感＞
- viewからtemplateにデータを渡す方法がだんだん理解出来てきた。辞書型はmodelもvalue,keyのどちらにもすることができるのでかなり便利。これからも多用していきたい。
- DjangoやBootstrapの公式リファレンスはなるべく見るくせを付ける。役立つ情報が結構書いてある。
- Djangoのmodel設計において、外部キーのカラムはその外部キーが紐づくテーブル名の小文字にすると良いらしい。
