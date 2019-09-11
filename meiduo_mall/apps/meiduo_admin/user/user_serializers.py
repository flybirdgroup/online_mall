#用户User序列化器类
from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'mobile', 'email','password')
        extra_kwargs ={'username':{'max_length':20, 'min_length':5},
                       'password':{'max_length':20, 'min_length':8, 'write_ony':True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user