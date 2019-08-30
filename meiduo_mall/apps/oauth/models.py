from django.db import models
# Create your models here.
from meiduo_mall.utils.my_model import BaseModel


class OAuthQQUser(BaseModel):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='美多用户')
    openid = models.CharField(max_length=64, verbose_name='qq用户id',db_index=True)

    class Meta:
        db_table = 'tb_qq_users'

# 为了将qq用户和梅朵用户绑在一起

# 1 创建oauth子应用
#2 定义模型类
#注册到installed apps

class OAuthSinaUser(BaseModel):
    """
    Sina登录用户数据
    """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='美多新浪用户')
    uid = models.CharField(max_length=64, verbose_name='access_token', db_index=True)

    class Meta:
        db_table = 'tb_oauth_sina'
        verbose_name = 'sina登录用户数据'
        verbose_name_plural = verbose_name