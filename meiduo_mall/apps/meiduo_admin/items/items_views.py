from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from meiduo_admin.items.items_serializers import SKUSerializer, GoodsCategorySerializer, SPUSerializer
from meiduo_admin.user.user_views import ImportPaginationclass
from goods.models import SKU, GoodsCategory, SPU


#商品视图
class SKUView(ModelViewSet):
    pagination_class = ImportPaginationclass
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer

#商品创建的类别
class SkuCategoriesView(APIView):
    # queryset = GoodsCategory.objects.filter(subs__isnull=True).all()
    # serializers = GoodsCategorySerializer
    def get(self,request):
        category = GoodsCategory.objects.filter(subs__isnull=True).all()
        serializer = GoodsCategorySerializer(instance=category, many=True)
        return Response(serializer.data)


class SpuSimpleView(ListAPIView):
    queryset = SPU.objects.all()
    serializer_class = SPUSerializer