from django import forms

class InquiryForm(forms.Form):
    name = forms.CharField(label='お名前', max_length=30)
    email = forms.EmailField(label='メールアドレス')
    title = forms.CharField(label='タイトル', max_length=30)
    message = forms.CharField(label='メッセージ', widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'].widget.attr['class'] = form-control
        self.fields['name'].widget.attr['placeholder'] = 'お名前をここに入力してください。'

        self.fields['email'].widget.attr['class'] = form-control
        self.fields['email'].widget.attr['placeholder'] = 'メールアドレスをここに入力してください。'

        self.fields['title'].widget.attr['class'] = form-control
        self.fields['title'].widget.attr['placeholder'] = 'タイトルをここに入力してください。'

        self.fields['message'].widget.attr['class'] = form-control
        self.fields['message'].widget.attr['placeholder'] = 'メッセージをここに入力してください。'