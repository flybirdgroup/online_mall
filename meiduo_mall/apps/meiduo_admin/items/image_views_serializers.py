from rest_framework import serializers, status
from rest_framework.response import Response

from goods.models import SKUImage, SKU

from django.db import transaction
from fdfs_client.client import Fdfs_client

from meiduo_mall.settings.dev import BASE_CONFIG


class SKUImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = "__all__"
    @transaction.atomic()
    def create(self, validated_data):
        sid = transaction.savepoint()
        try:
            image = self.context['request'].FILES.get('image')
            if not image:
                return Response(status=status.HTTP_404_NOT_FOUND)
            client = Fdfs_client(BASE_CONFIG)
            result = client.upload_by_buffer(filebuffer=image.read())
            print(result)
            if result['Status'] != "Upload successed.":
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            image = result['Remote file_id']
            validated_data['image'] = image
            sku_image = SKUImage.objects.create(**validated_data)
        except:
            transaction.savepoint_rollback(sid)
            raise serializers.ValidationError("图片上传不成功")
        else:
            transaction.savepoint_commit(sid)
            return sku_image

    @transaction.atomic()
    def update(self,instance,validated_data):
        sid = transaction.savepoint()
        try:
            image = self.context['request'].FILES.get('image')
            if not image:
                return Response(status=status.HTTP_404_NOT_FOUND)
            client = Fdfs_client(BASE_CONFIG)
            result = client.upload_by_buffer(image.read())
            if result['Status'] != "Upload successed.":
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
            image = result['Remote file_id']
            validated_data['image'] = image
            SKUImage.objects.filter(id = instance.id).update(**validated_data)
        except Exception as E:
            transaction.savepoint_rollback(sid)
            raise serializers.ValidationError('上传图片失败')
        else:
            transaction.savepoint_commit(sid)
            return instance
class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = "__all__"