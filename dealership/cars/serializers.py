from rest_framework import serializers

from .models import Car, CarPhoto


class CarPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarPhoto
        fields = ["id", "s3_key", "alt_text", "sort_order", "is_primary"]
        read_only_fields = ["id", "sort_order"]


class CarSerializer(serializers.ModelSerializer):
    photos = CarPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Car
        fields = [
            "id",
            "vin",
            "make",
            "model",
            "year",
            "mileage",
            "fuel_type",
            "transmission",
            "color",
            "body_type",
            "engine_cc",
            "doors",
            "seats",
            "drive_type",
            "base_price",
            "discount_price",
            "currency",
            "status",
            "location",
            "description",
            "created_at",
            "updated_at",
            "photos",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CarListSerializer(serializers.ModelSerializer):
    photos = CarPhotoSerializer(many=True, read_only=True)
    price = serializers.SerializerMethodField()

    class Meta:
        model = Car
        fields = [
            "id",
            "vin",
            "make",
            "model",
            "year",
            "mileage",
            "fuel_type",
            "transmission",
            "body_type",
            "base_price",
            "discount_price",
            "currency",
            "status",
            "price",
            "photos",
        ]
        read_only_fields = ["id"]

    def get_price(self, obj):
        return obj.discount_price if obj.discount_price is not None else obj.base_price