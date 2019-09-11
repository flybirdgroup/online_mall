from django.db import transaction
from rest_framework import serializers

from goods.models import GoodsCategory, SKU, SPU, SKUSpecification
from meiduo_admin.items.sku_serializers import SkuSpuSpecificationViewSerializer, SKUSpecificationSerializer


class SKUSerializer(serializers.ModelSerializer):
    specs = SKUSpecificationSerializer(read_only=True, many=True)
    category_id = serializers.IntegerField()
    # 关联嵌套返回
    category = serializers.StringRelatedField(read_only=True)
    # 指定所关联的spu表信息
    spu_id = serializers.IntegerField()
    # 关联嵌套返回
    spu = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SKU
        fields = "__all__"

    # 因为创建sku的同时,sku的规格也应该创建,但是序列化器只针对sku,
    # 所以,需要在sku序列化器的create方法进行重写
    #录入到sku specification表需要的数据是spu,sku,optionid
    @transaction.atomic
    def create(self, validated_data):
        try:
            sid = transaction.savepoint()
            sku = SKU.objects.create(**validated_data)
            specs_list = self.context['request'].data['specs']
            for spec in specs_list:
                SKUSpecification.objects.create(
                    option_id=spec['option_id'], spec_id=spec['spec_id'], sku_id=sku.id
                )
        except Exception as e:
            transaction.savepoint_rollback(sid)  # TODO 回滚
            raise serializers.ValidationError('数据录入有误')
        else:
            transaction.savepoint_commit(sid)
            return sku




class GoodsCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"

class SPUSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    category = serializers.StringRelatedField()
    class Meta:
        model = SPU
        fields = "__all__"