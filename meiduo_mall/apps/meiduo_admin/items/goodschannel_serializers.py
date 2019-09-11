from rest_framework import serializers
from goods.models import GoodsChannel, GoodsCategory, GoodsChannelGroup


class GoodsChannelViewSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only=True)
    group_id = serializers.IntegerField()
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField()
    class Meta:
        model = GoodsChannel
        fields = "__all__"


class ChannelCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"

#类别的频道组序列化器
class GoodsChannelGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsChannelGroup
        fields = "__all__"