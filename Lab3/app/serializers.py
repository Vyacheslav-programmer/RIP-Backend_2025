from rest_framework import serializers

from .models import *


class TariffsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ("id", "name", "status", "price", "ram", "cpu", "ssd", "image")


class TariffSerializer(TariffsSerializer):
    class Meta(TariffsSerializer.Meta):
        fields = "__all__"


class ForecastcloudpricesSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Forecastcloudprice
        fields = "__all__"


class ForecastcloudpriceSerializer(ForecastcloudpricesSerializer):
    tariffs = serializers.SerializerMethodField()
            
    def get_tariffs(self, forecastCloudPrice):
        items = forecastCloudPrice.tariffforecastcloudprice_set.all()
        return [TariffItemSerializer(item.tariff, context={"count": item.count}).data for item in items]


class TariffItemSerializer(TariffSerializer):
    count = serializers.SerializerMethodField()

    def get_count(self, _):
        return self.context.get("count")

    class Meta:
        model = Tariff
        fields = ("id", "name", "status", "price", "ram", "cpu", "ssd", "image", "count")


class TariffForecastcloudpriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TariffForecastcloudprice
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', "is_superuser")


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class UserUpdateProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        instance = super().update(instance, validated_data)

        if password and password.strip() and not self.instance.check_password(password):
            instance.set_password(password)
            instance.save()

        return instance