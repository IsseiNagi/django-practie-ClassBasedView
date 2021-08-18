from django import forms
from .models import Books
from datetime import datetime


class BookForm(forms.ModelForm):

    class Meta:
        model = Books
        fields = ['name', 'description', 'price']

    # BookFormのsaveメソッドをオーバーライドする
    def save(self, *args, **kwargs):
        # Booksの親クラスのcreate_atとupdate_atに入る値を定義する
        obj = super(BookForm, self).save(commit=False)
        obj.create_at = datetime.now()
        obj.update_at = datetime.now()
        obj.save()
        return obj


class BookUpdateForm(forms.ModelForm):

    class Meta:
        model = Books
        fields = ['name', 'description', 'price']

    def save(self, *args, **kwargs):
        obj = super().save(commit=False)
        # アップデートは、create_atを新たに更新するのはおかしい。値は既に入っているのでエラーにはならない。
        obj.update_at = datetime.now()
        obj.save()
        return obj
