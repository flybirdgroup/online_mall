from django.db import models

# Create your models here.

class Area(models.Model):
    name = models.CharField(max_length=20, verbose_name='区域名')
    parent = models.ForeignKey('self', related_name="subs",on_delete=models.SET_NULL,null=True, blank=True,verbose_name='父级区域')
    class Meta:
        db_table = 'tb_areas'

    def __str__(self):
        return self.name