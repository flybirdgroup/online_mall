from rest_framework import serializers

from goods.models import CategoryVisitCount


class CategoryVisitCountSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryVisitCount
        fields = "__all__"