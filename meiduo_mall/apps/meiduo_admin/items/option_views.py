from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from goods.models import SpecificationOption, SPUSpecification
from meiduo_admin.items.option_serializers import OptionViewSerializer, SpecificationOptionSerializer
from meiduo_mall.utils.my_pagination import ImportPaginationclass

#规格选项视图
class OptionView(ModelViewSet):
    pagination_class = ImportPaginationclass
    queryset = SpecificationOption.objects.all()
    serializer_class = OptionViewSerializer


class SpecificationOptionView(ListAPIView):
    serializer_class = SpecificationOptionSerializer
    def get_queryset(self):
        queryset = SPUSpecification.objects.all()
        for spec in queryset:
            spec.name = '%s, %s'%(spec.spu.name,spec.name)
        return queryset
