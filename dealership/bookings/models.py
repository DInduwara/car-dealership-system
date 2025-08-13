from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from cars.models import Car
from users.models import User


class TestDrive(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        DECLINED = "DECLINED", "Declined"
        COMPLETED = "COMPLETED", "Completed"
        NO_SHOW = "NO_SHOW", "No-show"
        CANCELLED = "CANCELLED", "Cancelled"

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="test_drives")
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="test_drives",
        limit_choices_to={"role": User.Roles.CUSTOMER},
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["car", "start_at"], name="unique_car_start"),
        ]
        ordering = ["-start_at"]

    def clean(self):
        if self.start_at and self.end_at:
            duration = self.end_at - self.start_at
            if duration != timezone.timedelta(hours=1):
                raise ValidationError({"end_at": "Test drive must be exactly 1 hour."})
            # Only whole hours 9..16 inclusive
            start_local = timezone.localtime(self.start_at)
            if start_local.minute != 0 or start_local.second != 0 or start_local.microsecond != 0:
                raise ValidationError({"start_at": "Start time must be on the hour."})
            if not (9 <= start_local.hour <= 16):
                raise ValidationError({"start_at": "Start hour must be between 09:00 and 16:00."})
        else:
            raise ValidationError("start_at and end_at are required")

        # Car availability
        if self.car.status in [Car.Status.SOLD, Car.Status.REMOVED]:
            raise ValidationError({"car": "Car is not available for test drives."})

        # Overlap check
        overlapping = (
            TestDrive.objects.filter(
                car=self.car,
                status__in=[TestDrive.Status.PENDING, TestDrive.Status.APPROVED],
            )
            .filter(start_at__lt=self.end_at, end_at__gt=self.start_at)
        )
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)
        if overlapping.exists():
            raise ValidationError({"start_at": "This time slot is already booked for this car."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"TestDrive<{self.car_id} {self.start_at.isoformat()}>"