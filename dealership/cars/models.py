import uuid
from django.db import models


class Car(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        RESERVED = "RESERVED", "Reserved"
        SOLD = "SOLD", "Sold"
        REMOVED = "REMOVED", "Removed"

    class Location(models.TextChoices):
        SHOWROOM = "SHOWROOM", "Showroom"
        WAREHOUSE = "WAREHOUSE", "Warehouse"

    class FuelType(models.TextChoices):
        PETROL = "PETROL", "Petrol"
        DIESEL = "DIESEL", "Diesel"
        HYBRID = "HYBRID", "Hybrid"
        ELECTRIC = "ELECTRIC", "Electric"
        CNG = "CNG", "CNG"
        LPG = "LPG", "LPG"

    class Transmission(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        AUTOMATIC = "AUTOMATIC", "Automatic"
        CVT = "CVT", "CVT"
        DUAL_CLUTCH = "DUAL_CLUTCH", "Dual-clutch"

    class BodyType(models.TextChoices):
        SEDAN = "SEDAN", "Sedan"
        HATCHBACK = "HATCHBACK", "Hatchback"
        SUV = "SUV", "SUV"
        COUPE = "COUPE", "Coupe"
        CONVERTIBLE = "CONVERTIBLE", "Convertible"
        WAGON = "WAGON", "Wagon"
        VAN = "VAN", "Van"
        PICKUP = "PICKUP", "Pickup"
        OTHER = "OTHER", "Other"

    class DriveType(models.TextChoices):
        FWD = "FWD", "FWD"
        RWD = "RWD", "RWD"
        AWD = "AWD", "AWD"
        FOUR_WD = "4WD", "4WD"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vin = models.CharField(max_length=32, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    mileage = models.PositiveIntegerField(default=0)
    fuel_type = models.CharField(max_length=16, choices=FuelType.choices)
    transmission = models.CharField(max_length=16, choices=Transmission.choices)
    color = models.CharField(max_length=30, blank=True)
    body_type = models.CharField(max_length=16, choices=BodyType.choices)
    engine_cc = models.PositiveIntegerField(null=True, blank=True)
    doors = models.PositiveSmallIntegerField(null=True, blank=True)
    seats = models.PositiveSmallIntegerField(null=True, blank=True)
    drive_type = models.CharField(max_length=8, choices=DriveType.choices, blank=True)
    base_price = models.DecimalField(max_digits=12, decimal_places=2)
    discount_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.AVAILABLE)
    location = models.CharField(max_length=12, choices=Location.choices, default=Location.SHOWROOM)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["vin"]),
            models.Index(fields=["make", "model", "year"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.make} {self.model} {self.year} ({self.vin})"


class CarPhoto(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="photos")
    s3_key = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "id"]

    def save(self, *args, **kwargs):
        if not self.sort_order:
            last = CarPhoto.objects.filter(car=self.car).order_by("-sort_order").first()
            self.sort_order = (last.sort_order if last else 0) + 1
        super().save(*args, **kwargs)
        if self.is_primary:
            CarPhoto.objects.filter(car=self.car).exclude(pk=self.pk).update(is_primary=False)
        else:
            if not CarPhoto.objects.filter(car=self.car, is_primary=True).exists():
                CarPhoto.objects.filter(pk=self.pk).update(is_primary=True)

    def __str__(self) -> str:
        return f"Photo<{self.car_id}:{self.s3_key}>"