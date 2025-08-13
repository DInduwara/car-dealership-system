from rest_framework import viewsets

from users.permissions import IsAdminOrSales

from .models import Sale
from .serializers import SaleSerializer


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related("car", "customer", "salesperson")
    serializer_class = SaleSerializer
    permission_classes = [IsAdminOrSales]