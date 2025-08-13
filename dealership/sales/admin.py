from django.contrib import admin

from .models import Commission, Sale


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        "car",
        "customer",
        "salesperson",
        "sale_price",
        "sale_datetime",
        "payment_method",
    )
    search_fields = ("contract_number",)


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ("sale", "salesperson", "rate", "amount", "created_at")