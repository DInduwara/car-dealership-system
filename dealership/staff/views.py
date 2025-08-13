from django.db.models import Sum
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsAdmin, IsAdminOrSales
from sales.models import Sale

from .models import StaffProfile
from .serializers import (
    StaffCreateSerializer,
    StaffMetricsSerializer,
    StaffProfileSerializer,
)


class StaffViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.select_related("user")
    serializer_class = StaffProfileSerializer

    def get_permissions(self):
        if self.action in ["create", "list", "partial_update", "update", "destroy"]:
            return [IsAdmin()]
        if self.action in ["retrieve", "metrics"]:
            return [IsAdminOrSales()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = StaffCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        output = StaffProfileSerializer(profile).data
        return Response(output, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="metrics")
    def metrics(self, request, pk=None):
        profile = self.get_object()
        total_revenue = (
            Sale.objects.filter(salesperson=profile.user).aggregate(total=Sum("sale_price")).get("total")
            or 0
        )
        data = {
            "total_sales_count": profile.total_sales_count,
            "total_revenue": total_revenue,
        }
        return Response(data)