from rest_framework.viewsets import ModelViewSet
#品牌显示类视图
from goods.models import Brand
from meiduo_admin.items.goodsbrands_serializers import GoodsBrandSerializer
from meiduo_mall.utils.my_pagination import ImportPaginationclass


class GoodsBrandView(ModelViewSet):
    pagination_class = ImportPaginationclass
    queryset = Brand.objects.all()
    serializer_class = GoodsBrandSerializer

