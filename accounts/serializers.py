from rest_framework import serializers
from .models import CustomUser, PaymentMethod


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'password')  # Include 'password' in fields
        extra_kwargs = {'password': {'write_only': True}}  # Specify 'password' as write-only

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ('id', 'type', 'details')
