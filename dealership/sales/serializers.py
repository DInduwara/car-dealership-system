from rest_framework import serializers

from cars.models import Car
from staff.models import StaffProfile

from .models import Commission, Sale


class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = ["id", "sale", "salesperson", "rate", "amount", "created_at"]
        read_only_fields = ["id", "created_at"]


class SaleSerializer(serializers.ModelSerializer):
    commissions = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Sale
        fields = [
            "id",
            "car",
            "customer",
            "salesperson",
            "sale_price",
            "currency",
            "payment_method",
            "sale_datetime",
            "contract_number",
            "remarks",
            "created_at",
            "commissions",
        ]
        read_only_fields = ["id", "created_at", "commissions"]

    def validate(self, attrs):
        car = attrs["car"]
        if car.status == Car.Status.SOLD:
            raise serializers.ValidationError({"car": "Car already sold."})
        if car.status == Car.Status.REMOVED:
            raise serializers.ValidationError({"car": "Car removed from inventory."})
        # Ensure salesperson has a StaffProfile for commission and metrics
        salesperson = attrs.get("salesperson")
        if not StaffProfile.objects.filter(user=salesperson).exists():
            raise serializers.ValidationError({"salesperson": "Salesperson must have a StaffProfile."})
        return attrs