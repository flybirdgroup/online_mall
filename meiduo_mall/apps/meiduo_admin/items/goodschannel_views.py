from rest_framework.viewsets import ModelViewSet
from goods.models import GoodsChannel, GoodsCategory,GoodsChannelGroup
from meiduo_admin.items.goodschannel_serializers import GoodsChannelViewSerializer, ChannelCategoriesSerializer, GoodsChannelGroupSerializer
from meiduo_mall.utils.my_pagination import ImportPaginationclass
from rest_framework.generics import ListAPIView

class GoodsChannelView(ModelViewSet):
    pagination_class = ImportPaginationclass
    queryset = GoodsChannel.objects.all()
    serializer_class = GoodsChannelViewSerializer



class ChannelCategoriesView(ListAPIView):
    serializer_class = ChannelCategoriesSerializer

    def get_queryset(self):
        queryset = GoodsCategory.objects.filter(parent__isnull=True)
        return queryset

#类别的频道显示
class GoodsChannelGroupView(ListAPIView):
    serializer_class = GoodsChannelGroupSerializer
    queryset = GoodsChannelGroup.objects.all()
    pass