from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import StaffProfile

User = get_user_model()


class StaffProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            "id",
            "user",
            "salary",
            "commission_rate",
            "hire_date",
            "total_sales_count",
            "is_active",
        ]
        read_only_fields = ["id", "user", "total_sales_count"]


class StaffCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    role = serializers.ChoiceField(
        choices=[(User.Roles.SALES, "SALES"), (User.Roles.ADMIN, "ADMIN")],
        default=User.Roles.SALES,
    )
    salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    commission_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    hire_date = serializers.DateField(required=False)

    def create(self, validated_data):
        role = validated_data.pop("role")
        password = validated_data.pop("password")
        salary = validated_data.pop("salary")
        commission_rate = validated_data.pop("commission_rate")
        hire_date = validated_data.pop("hire_date", None)

        user = User.objects.create_user(role=role, **validated_data)
        user.set_password(password)
        user.save()

        profile = StaffProfile.objects.create(
            user=user,
            salary=salary,
            commission_rate=commission_rate,
            hire_date=hire_date if hire_date else None,
        )
        return profile


class StaffMetricsSerializer(serializers.Serializer):
    total_sales_count = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=14, decimal_places=2)