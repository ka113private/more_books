import os
from django import forms
from django.core.mail import EmailMessage
from .models import Tag, Bookshelf, Inquiry


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ('name', 'email', 'title', 'message', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control-inquiry'
        self.fields['name'].widget.attrs['placeholder'] = 'お名前'
        self.fields['email'].widget.attrs['placeholder'] = 'メールアドレス'
        self.fields['title'].widget.attrs['placeholder'] = 'タイトル'
        self.fields['message'].widget.attrs['placeholder'] = 'お問い合わせ内容'

    def send_email(self):
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        title = self.cleaned_data['title']
        message = self.cleaned_data['message']

        subject = '[MoreBooks!]お問い合わせ確認メール {}'.format(title)
        message = '{0}様\n\n'.format(name)\
                  +'この度はお問い合わせいただき、誠にありがとうございます。\n'\
                  +'以下の内容でお問い合わせを承りました。\n'\
                  +'担当者より順次ご返信させていただきますので、それまでお待ちください。\n\n' \
                  +'■お問い合わせ内容\n' \
                  +'氏名：{0}\nメールアドレス：{1}\nタイトル：{2}\nお問い合わせ内容：\n{3}'.format(name, email, title, message)
        from_email = os.environ.get('FROM_EMAIL')
        to_list = [
            email
        ]
        cc_list = [
        ]

        emailMessage = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=to_list,
            cc=cc_list)
        emailMessage.send()


class TagAddForm(forms.ModelForm):
    """タグ追加フォーム"""
    class Meta:
        model = Tag
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = '自由にタグをつけてみましょう'


class BookshelfAddForm(forms.ModelForm):
    """書籍をマイページの本棚に追加するフォーム"""
    class Meta:
        model = Bookshelf
        fields = ()