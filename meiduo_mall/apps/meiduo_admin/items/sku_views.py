from rest_framework.generics import ListAPIView

from goods.models import SPUSpecification
from .sku_serializers import SkuSpuSpecificationViewSerializer


class SkuSpuSpecificationView(ListAPIView):
    serializer_class =  SkuSpuSpecificationViewSerializer
    # queryset = SPUSpecification.objects.all()#这里显示就会出现所有SPU的规格,也就是所有不同类别的产品都会显示出来,这样很容易出现混乱,所以需要重写数据源方法

    def get_queryset(self):
        spu_id = self.kwargs.get('spu_id')
        queryset = SPUSpecification.objects.filter(spu_id= spu_id).all()
        return queryset


