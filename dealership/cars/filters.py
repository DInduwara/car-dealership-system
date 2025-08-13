import django_filters
from django.db.models.functions import Coalesce

from .models import Car


class CarFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(method="filter_min_price")
    max_price = django_filters.NumberFilter(method="filter_max_price")

    class Meta:
        model = Car
        fields = ["make", "model", "year", "fuel_type", "body_type", "transmission"]

    def _annotated(self, qs):
        return qs.annotate(price=Coalesce("discount_price", "base_price"))

    def filter_min_price(self, qs, name, value):
        return self._annotated(qs).filter(price__gte=value)

    def filter_max_price(self, qs, name, value):
        return self._annotated(qs).filter(price__lte=value)