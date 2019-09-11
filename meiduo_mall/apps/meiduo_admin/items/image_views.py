from rest_framework.viewsets import ModelViewSet

from rest_framework.generics import ListAPIView

from goods.models import SKUImage, SKU
from meiduo_admin.items.image_views_serializers import SKUImageSerializer, SKUSerializer

from meiduo_mall.utils.my_pagination import ImportPaginationclass


class SKUImageView(ModelViewSet):
    queryset = SKUImage.objects.all()
    serializer_class = SKUImageSerializer
    pagination_class = ImportPaginationclass


class ImageSKUView(ListAPIView):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer