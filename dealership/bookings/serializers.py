from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from .models import TestDrive

User = get_user_model()


class TestDriveSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = TestDrive
        fields = ["id", "car", "customer", "start_at", "end_at", "status", "notes", "created_at"]
        read_only_fields = ["id", "customer", "status", "created_at", "end_at"]

    def validate_start_at(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Start time must be in the future.")
        return value

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user
        if not user.is_authenticated or getattr(user, "role", None) != User.Roles.CUSTOMER:
            raise serializers.ValidationError("Only customers can create bookings.")
        start_at = validated_data["start_at"]
        end_at = start_at + timezone.timedelta(hours=1)
        booking = TestDrive.objects.create(
            customer=user,
            end_at=end_at,
            status=TestDrive.Status.PENDING,
            **validated_data,
        )
        return booking