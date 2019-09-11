from django.db import transaction
from fdfs_client.client import Fdfs_client

from rest_framework import serializers
from rest_framework.response import Response

from goods.models import Brand


from meiduo_mall.settings.dev import BASE_CONFIG


class GoodsBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'

    def create(self, validated_data):
        logo = self.context['request'].FILES.get("logo")
        if not logo:
            return Response(status=400)
        client = Fdfs_client(BASE_CONFIG)
        result = client.upload_by_buffer(logo.read())
        print(result)
        if result['Status'] != 'Upload successed.':
            return Response('上传失败',status=400)
        logo = result['Remote file_id']
        brand = Brand.objects.create(**validated_data)
        brand.logo = logo
        brand.save()
        return brand

    @transaction.atomic
    def update(self, instance, validated_data):
        sid = transaction.savepoint()
        try:
            logo = self.context['request'].FILES.get("logo")
            client = Fdfs_client(BASE_CONFIG)
            result = client.upload_by_buffer(logo.read())
            if result['Status'] != 'Upload successed.':
                return Response('上传失败', status=400)
            logo = result['Remote file_id']
            brand = Brand.objects.get(id=instance.id)
            brand.logo = logo
            brand.name = validated_data['name']
            brand.first_letter = validated_data['first_letter']
            brand.save()
        except Exception as e:
            transaction.savepoint_rollback(sid)
            raise serializers.ValidationError("图片上传失败")
        else:
            transaction.savepoint_commit(sid)
            return brand













