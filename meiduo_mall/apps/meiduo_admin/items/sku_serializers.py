from rest_framework import serializers
from goods.models import SPUSpecification, SpecificationOption, SKUSpecification


class SpuSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ['id','value']


class SKUSpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUSpecification
        fields = "__all__"


class SkuSpuSpecificationViewSerializer(serializers.ModelSerializer):
    options = SpuSpecificationSerializer(read_only=True, many=True)
    #要有id和value两个值,所以需要用到序列化嵌套,就是可以把似的字段可以有两个值
    class Meta:
        model = SPUSpecification
        fields = "__all__"

