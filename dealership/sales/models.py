from django.conf import settings
from django.db import models
from django.utils import timezone

from cars.models import Car


class Sale(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        CARD = "CARD", "Card"
        FINANCING = "FINANCING", "Financing"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank transfer"
        OTHER = "OTHER", "Other"

    car = models.OneToOneField(Car, on_delete=models.PROTECT, related_name="sale")
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="purchases"
    )
    salesperson = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sales_made"
    )
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    sale_datetime = models.DateTimeField(default=timezone.now)
    contract_number = models.CharField(max_length=64, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sale_datetime"]

    def __str__(self):
        return f"Sale<{self.car_id} {self.sale_price} {self.currency}>"


class Commission(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="commissions")
    salesperson = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="commissions"
    )
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["sale", "salesperson"], name="unique_sale_salesperson_commission"
            ),
        ]

    def __str__(self):
        return f"Commission<{self.sale_id} {self.amount}>"