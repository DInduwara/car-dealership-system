from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsAdminOrSales, IsCustomer

from .models import TestDrive
from .serializers import TestDriveSerializer


class BookingViewSet(viewsets.ModelViewSet):
    queryset = TestDrive.objects.select_related("car", "customer")
    serializer_class = TestDriveSerializer

    def get_permissions(self):
        if self.action in ["create", "me"]:
            return [IsCustomer()]
        if self.action in [
            "list",
            "approve",
            "decline",
            "complete",
            "cancel",
            "no_show",
            "partial_update",
            "update",
            "destroy",
        ]:
            return [IsAdminOrSales()]
        if self.action == "retrieve":
            # Allow both staff (full access) and customers (own object)
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "me":
            return qs.filter(customer=self.request.user)
        if self.action == "retrieve" and getattr(self.request.user, "role", None) == "CUSTOMER":
            return qs.filter(customer=self.request.user)
        return qs

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        bookings = self.get_queryset()
        page = self.paginate_queryset(bookings)
        serializer = self.get_serializer(page if page is not None else bookings, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="approve")
    def approve(self, request, pk=None):
        booking = self.get_object()
        if booking.status != TestDrive.Status.PENDING:
            return Response({"detail": "Only pending bookings can be approved."}, status=400)
        booking.status = TestDrive.Status.APPROVED
        booking.save()
        return Response({"status": booking.status})

    @action(detail=True, methods=["patch"], url_path="decline")
    def decline(self, request, pk=None):
        booking = self.get_object()
        if booking.status != TestDrive.Status.PENDING:
            return Response({"detail": "Only pending bookings can be declined."}, status=400)
        booking.status = TestDrive.Status.DECLINED
        booking.save()
        return Response({"status": booking.status})

    @action(detail=True, methods=["patch"], url_path="complete")
    def complete(self, request, pk=None):
        booking = self.get_object()
        if booking.status != TestDrive.Status.APPROVED:
            return Response({"detail": "Only approved bookings can be completed."}, status=400)
        booking.status = TestDrive.Status.COMPLETED
        booking.save()
        return Response({"status": booking.status})

    @action(detail=True, methods=["patch"], url_path="cancel")
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status not in [TestDrive.Status.PENDING, TestDrive.Status.APPROVED]:
            return Response({"detail": "Only pending or approved bookings can be cancelled."}, status=400)
        booking.status = TestDrive.Status.CANCELLED
        booking.save()
        return Response({"status": booking.status})

    @action(detail=True, methods=["patch"], url_path="no-show")
    def no_show(self, request, pk=None):
        booking = self.get_object()
        if booking.status != TestDrive.Status.APPROVED:
            return Response({"detail": "Only approved bookings can be marked as no-show."}, status=400)
        booking.status = TestDrive.Status.NO_SHOW
        booking.save()
        return Response({"status": booking.status})