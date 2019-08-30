from django.contrib.auth.backends import ModelBackend
import re
from .models import User

#通过手机或者用户名查询用户是否存在的方法
def get_user_by_account(account):
    """

    :param account: 用户名或者手机号
    :return: user
    """
    try:
        if re.match(r'^1[3-9]\d{9}',account):
            user = User.objects.get(mobile = account)
        else:
            user = User.objects.get(username = account)

    except User.DoesNotExist:
        return None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self,request,username= None, password=None,**kwargs):
        """

        :param request: 请求队形
        :param username:用户名
        :param password:用户密码
        :param kwargs:其他参数
        :return:user
        """
        user = get_user_by_account(username)
        if user and user.check_password(password):
            return user



