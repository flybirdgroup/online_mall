from fdfs_client.client import Fdfs_client
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from goods.models import SPU, GoodsCategory, Brand, SPUSpecification
from meiduo_mall.settings.dev import BASE_CONFIG, BASE_URL
from .spu_serializers import SPUSerializer, SPUCategoriesSerializer, SPUBrandSerializer, SPUSpecificationSerializer
from meiduo_mall.utils.my_pagination import ImportPaginationclass

class SPUView(ModelViewSet):
    pagination_class = ImportPaginationclass
    serializer_class = SPUSerializer
    queryset = SPU.objects.all()


class SPUCategoriesView(ListAPIView):
    queryset = GoodsCategory.objects.filter(parent__isnull=True)
    serializer_class = SPUCategoriesSerializer


class SPUSubCategories(ListAPIView):
    serializer_class = SPUCategoriesSerializer

    def get_queryset(self):
        sid = self.kwargs.get('sid')
        queryset = GoodsCategory.objects.filter(parent_id = sid).all()
        return queryset


class SPUBrand(ListAPIView):
    serializer_class = SPUBrandSerializer
    queryset = Brand.objects.all()

class SPUImageView(APIView):
    def post(self,request):
        image = request.FILES.get("image")
        if not image:
            return Response(status=400)
        client = Fdfs_client(BASE_CONFIG)
        result = client.upload_by_buffer(image.read())
        print(result)
        if result.get("Status") != "Upload successed.":
            return Response(status=400)
        image_url = result.get("Remote file_id")
        return Response({
            "img_url": "%s%s" % (BASE_URL, image_url)
        })

#SPU规格视图
class SPUspecificationView(ModelViewSet):
    pagination_class = ImportPaginationclass
    queryset = SPUSpecification.objects.all()
    serializer_class = SPUSpecificationSerializer