from django.db import models

class BaseModel(models.Model):

    create_time = models.DateField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name="更新时间")

    class Meta:
        abstract = True #在迁移的时候不会生成表

