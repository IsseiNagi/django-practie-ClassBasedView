from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.base import (
    View, TemplateView, RedirectView
)
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView, FormView
)
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.http import Http404

# settings.pyで定義したロガーのインスタンスを生成する
import logging
application_logger = logging.getLogger('application-logger')
error_logger = logging.getLogger('error-logger')

from datetime import datetime
from . import forms
from .models import Books, Pictures


# Create your views here.


# クラスベースビューの中で最も基本のもの。他のクラスベースビューの特定目的に一致しないようなViewを作りたい時か？
class IndexView(View):

    def get(self, request, *args, **kwargs):
        book_form = forms.BookForm()
        return render(request, 'index.html', context={
            'book_form': book_form,
        })

    def post(self, request, *args, **kwargs):
        book_form = forms.BookForm(request.POST or None)
        if book_form.is_valid():
            book_form.save()
        return render(request, 'index.html', context={
            'book_form': book_form,
        })


class HomeView(TemplateView):

    template_name = 'home.html'

    # TemplateViewのget_context_dataをオーバーライドしてカスタマイズ
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  # nameはkwargsに入ってくる
        # debugログ出力用
        application_logger.debug('Home画面を表示します')
        # エラーログ出力用
        if kwargs.get('name') == 'あああ':
            # error_logger.error('この名前は使用できません')  # Middlewareを作成し統合のためコメントアウト
            raise Http404('この名前は使用できません')
        context['name'] = kwargs.get('name')
        context['time'] = datetime.now()
        return context


class BookDetailView(DetailView):
    model = Books
    template_name = 'book.html'

    # TemplateViewと同じようにget_context_dataをオーバーライドしてカスタマイズできる
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BookListView(ListView):
    model = Books
    template_name = 'book_list.html'

    # 取得をカスタムする
    def get_queryset(self):
        qs = super(BookListView, self).get_queryset()
        qs = qs.order_by('-id')  # idの降順で並べる

        # urlsからnameで送られてきた値で始まるデータに絞り込む
        if 'name' in self.kwargs:  # urlsからnameが送られてきた場合
            qs = qs.filter(name__startswith=self.kwargs['name'])
        return qs


class BookCreateView(CreateView):
    model = Books
    fields = ['name', 'description', 'price']
    template_name = 'add_book.html'
    success_url = reverse_lazy('store:list_books')  # 成功した後の処理がないと、エラーになる

    # 上の定義だけで作成すると、Booksの親クラスで指定したフィールドがnullになるようだ。form_validをオーバーライドしてカスタムする
    def form_valid(self, form):
        form.instance.create_at = datetime.now()
        form.instance.update_at = datetime.now()
        return super(BookCreateView, self).form_valid(form)

    # フィールドにデフォルトで初期値を設定するカスタマイズ
    def get_initial(self, **kwargs):
        initial = super(BookCreateView, self).get_initial(**kwargs)
        initial['name'] = 'sample'  # nameにsampleをセットしている
        return initial


# SuccessMessageMixinを継承させてメッセージ表示機能を追加する
class BookUpdateView(SuccessMessageMixin, UpdateView):
    template_name = 'update_book.html'
    model = Books
    form_class = forms.BookUpdateForm
    # 静的メッセージを表示する場合
    success_message = '更新しました'

    def get_success_url(self):
        return reverse_lazy('store:edit_book', kwargs={'pk': self.object.id})

    # 動的にメッセージを表示する場合  cleaned_dataから名前を取って追加表示
    def get_success_message(self, cleaned_data):
        return cleaned_data.get('name') + 'を更新しました'

    # 以下、画像アップロード機能の追加
    # コンテキストでフォームを渡して、画面上でそのフォームを使って画像をアップロードする
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        picture_form = forms.PictureUploadForm()
        pictures = Pictures.objects.filter_by_book(book=self.object)
        context['pictures'] = pictures
        context['picture_form'] = picture_form
        return context

    def post(self, request, *args, **kwargs):
        # 本の内容自体のアップデートはUpdateViewに任せて、画像アップ処理を追加する
        picture_form = forms.PictureUploadForm(
            request.POST or None, request.FILES or None)
        if picture_form.is_valid() and request.FILES:
            book = self.get_object()  # 今、更新しているレコードを取得する
            picture_form.save(book=book)
        return super().post(request, *args, **kwargs)


class BookDeleteView(DeleteView):
    model = Books
    template_name = 'delete_book.html'
    success_url = reverse_lazy('store:list_books')


class BookFormView(FormView):

    template_name = 'form_book.html'
    form_class = forms.BookForm
    success_url = reverse_lazy('store:list_books')

    # フォームデータを保存する処理を実装
    def form_valid(self, form):
        if form.is_valid():
            form.save()
        return super().form_valid(form)

    # 初期値の実装
    def get_initial(self):
        initial = super().get_initial()
        initial['name'] = '本の名前を入力'
        return initial


class BookRedirectView(RedirectView):
    # 静的にリダイレクトさせる場合は、urlを指定するだけで良い
    url = 'https://yahoo.co.jp'

    # 動的にリダイレクトさせる場合は、get_redirect_urlメソッドをオーバーライドする
    def get_redirect_url(self, *args, **kwargs):
        book = Books.objects.first()
        # urlに対して引数を取って、引数をもとに遷移させるパターン
        if 'pk' in kwargs:
            return reverse_lazy('store:detail_book', kwargs={'pk': kwargs['pk']})

        return reverse_lazy('store:edit_book', kwargs={'pk': book.pk})


# 画像をクリックさせてこのviewを実行して削除する簡易的なもの
def delete_picture(request, pk):
    picture = get_object_or_404(Pictures, pk=pk)
    picture.delete()
    # osを使ってmediaの下のpictureディレクトリに保存されている画像を合わせて削除するやり方
    # import os
    # if os.path.isfile(picture.picture.path):
    #     os.remove(picture.picture.path)

    messages.success(request, '画像を削除しました')
    return redirect('store:edit_book', pk=picture.book.id)
