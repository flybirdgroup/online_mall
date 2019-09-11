from collections import OrderedDict

from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from meiduo_admin.user.user_serializers import UserSerializer, UserAddSerializer
from meiduo_mall.utils.my_pagination import ImportPaginationclass
from users.models import User

#用户视图
class UserView(ListAPIView, CreateAPIView):
    pagination_class = ImportPaginationclass
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        if self.request.method == 'POST':
            return UserAddSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')
        if keyword is '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(username=keyword)