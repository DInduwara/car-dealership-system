from decimal import Decimal

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from bookings.models import TestDrive
from cars.models import Car
from staff.models import StaffProfile

from .models import Commission, Sale


@receiver(post_save, sender=Sale)
def handle_sale_created(sender, instance: Sale, created: bool, **kwargs):
    if not created:
        return
    with transaction.atomic():
        # Mark car as SOLD
        Car.objects.filter(pk=instance.car.pk).update(status=Car.Status.SOLD)
        # Cancel future bookings
        now = timezone.now()
        TestDrive.objects.filter(
            car=instance.car,
            status__in=[TestDrive.Status.PENDING, TestDrive.Status.APPROVED],
            start_at__gt=now,
        ).update(status=TestDrive.Status.CANCELLED)
        # Update staff metrics and create commission
        staff_profile = (
            StaffProfile.objects.select_for_update().filter(user=instance.salesperson).first()
        )
        if staff_profile:
            staff_profile.total_sales_count = (staff_profile.total_sales_count or 0) + 1
            staff_profile.save(update_fields=["total_sales_count"])
            rate = staff_profile.commission_rate or Decimal("0.00")
            amount = (instance.sale_price * rate) / Decimal("100.0")
            Commission.objects.create(
                sale=instance,
                salesperson=instance.salesperson,
                rate=rate,
                amount=amount.quantize(Decimal("0.01")),
            )