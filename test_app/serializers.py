from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class AccountSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = Account
        fields = ['id', 'user', 'city', 'country', 'is_verified', 'balance']

class UserRegistrationSerializer(serializers.ModelSerializer):
    city = serializers.CharField(write_only=True)
    country = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'city', 'country']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        city = validated_data.pop('city')
        country = validated_data.pop('country')
        user = User.objects.create_user(**validated_data)
        Account.objects.create(user=user, city=city, country=country)
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        account = Account.objects.get(user=instance)
        representation['city'] = account.city
        representation['country'] = account.country
        return representation
