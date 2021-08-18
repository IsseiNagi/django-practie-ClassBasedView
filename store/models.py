from django.db import models
from django.urls import reverse_lazy
from django.dispatch import receiver
import os


# Create your models here.


class BaseModel(models.Model):
    create_at = models.DateTimeField()
    update_at = models.DateTimeField()

    class Meta:
        abstract = True


class Books(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    price = models.IntegerField()

    class Meta:
        db_table = 'books'

    # CreateView絡み。作成成功した後の処理を、モデル側で定義する。pkを取って、作成したインスタンスの詳細画面に遷移する。
    # Viewsのsuccess_urlの定義が有効になっている場合、success_urlが優先される
    def get_absolute_url(self):
        return reverse_lazy('store:detail_book', kwargs={'pk': self.pk})


class PicturesManager(models.Manager):

    def filter_by_book(self, book):
        return self.filter(book=book).all()


class Pictures(BaseModel):
    picture = models.FileField(upload_to='picture/')
    book = models.ForeignKey(
        'books',
        on_delete=models.CASCADE,
        )
    objects = PicturesManager()


# Picturesの削除が行われた時のシグナルを定義し、mediaの下のpictureディレクトリにあるファイルも削除する処理
@receiver(models.signals.post_delete, sender=Pictures)
def delete_picture(sender, instance, **kwargs):  # instanceにPicturesの情報が入っている
    if instance.picture:
        if os.path.isfile(instance.picture.path):
            os.remove(instance.picture.path)
