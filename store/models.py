from django.db import models
from django.urls import reverse_lazy

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
