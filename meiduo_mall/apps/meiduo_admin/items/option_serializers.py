from rest_framework import serializers

from goods.models import SpecificationOption, SPUSpecification


class OptionViewSerializer(serializers.ModelSerializer):
    spec = serializers.StringRelatedField(read_only=True)
    spec_id = serializers.IntegerField()
    class Meta:
        model = SpecificationOption
        fields = "__all__"


class SpecificationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPUSpecification
        fields = '__all__'
