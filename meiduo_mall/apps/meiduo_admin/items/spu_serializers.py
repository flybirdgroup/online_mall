from rest_framework import serializers

from goods.models import SPU, GoodsCategory, Brand, SPUSpecification


#SPU序列化器
class SPUSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField(read_only=True)
    brand_id = serializers.IntegerField()
    category1_id = serializers.IntegerField()
    category1 = serializers.StringRelatedField(read_only=True)
    category2_id = serializers.IntegerField()
    category2 = serializers.StringRelatedField(read_only=True)
    category3_id = serializers.IntegerField()
    category3 = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SPU
        fields = "__all__"

#SPU类别序列化器
class SPUCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = '__all__'

#SPU品牌序列化器
class SPUBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"

#SPU规格序列化器
class SPUSpecificationSerializer(serializers.ModelSerializer):
    spu = serializers.StringRelatedField(read_only=True)
    spu_id = serializers.IntegerField()
    class Meta:
        model = SPUSpecification
        fields = "__all__"