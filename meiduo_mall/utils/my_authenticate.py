from django.contrib.auth.backends import ModelBackend
import re
from users.models import  User
class MymodelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
                try:
                    user = User.objects.get(username=username, is_staff=True, is_superuser=True)
                except:
                    return None
                else:
                    if user.check_password(password):
                        return user
                    return None
        else:
            try:
                if re.match(r'^1[3-9]\d{9}$',username):
                    user = User.objects.get(mobile= username)
                #查询用户
                else:
                    user = User.objects.get(username = username)
            except Exception as e:
                return None
            if user and user.check_password(password):
                return user
            else:
                return None

        #2 校验密码,返回用户
