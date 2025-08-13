from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsAdminOrSales

from .filters import CarFilter
from .models import Car, CarPhoto
from .serializers import CarPhotoSerializer, CarSerializer


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all().prefetch_related("photos")
    serializer_class = CarSerializer
    filterset_class = CarFilter
    ordering_fields = ["year", "mileage", "base_price", "discount_price", "created_at"]
    search_fields = ["vin", "make", "model", "color"]

    def get_queryset(self):
        qs = super().get_queryset().annotate(price=Coalesce("discount_price", "base_price"))
        if self.action in ["list", "retrieve", "available_slots"] and (
            not self.request.user.is_authenticated
        ):
            return qs.exclude(status=Car.Status.REMOVED)
        return qs

    def get_permissions(self):
        if self.action in ["list", "retrieve", "available_slots"]:
            return [permissions.AllowAny()]
        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
            "photos",
            "delete_photo",
        ]:
            return [IsAdminOrSales()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="photos")
    def photos(self, request, pk=None):
        car = self.get_object()
        serializer = CarPhotoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        CarPhoto.objects.create(car=car, **serializer.validated_data)
        return Response({"detail": "Photo added"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="photos/(?P<photo_id>[^/.]+)")
    def delete_photo(self, request, pk=None, photo_id=None):
        car = self.get_object()
        try:
            photo = car.photos.get(pk=photo_id)
        except CarPhoto.DoesNotExist:
            return Response({"detail": "Photo not found"}, status=status.HTTP_404_NOT_FOUND)
        photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"], url_path="available-slots")
    def available_slots(self, request, pk=None):
        car = self.get_object()
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"detail": "date query param required (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            target_date = timezone.datetime.fromisoformat(date_str).date()
        except Exception:
            return Response({"detail": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)

        tz = timezone.get_current_timezone()
        start_hour, end_hour = 9, 16
        slots = []
        from bookings.models import TestDrive  # lazy import to avoid circular

        day_start = timezone.make_aware(
            timezone.datetime.combine(target_date, timezone.datetime.min.time()), tz
        )
        for hour in range(start_hour, end_hour + 1):
            slot_start = day_start + timezone.timedelta(hours=hour)
            slot_end = slot_start + timezone.timedelta(hours=1)
            overlapping = (
                TestDrive.objects.filter(
                    car=car,
                    status__in=[TestDrive.Status.PENDING, TestDrive.Status.APPROVED],
                )
                .filter(start_at__lt=slot_end, end_at__gt=slot_start)
                .exists()
            )
            if not overlapping and car.status not in [Car.Status.SOLD, Car.Status.REMOVED]:
                slots.append({
                    "start_at": slot_start.isoformat(),
                    "end_at": slot_end.isoformat(),
                })
        return Response(slots)