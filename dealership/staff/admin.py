from django.contrib import admin

from .models import StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "salary",
        "commission_rate",
        "hire_date",
        "total_sales_count",
        "is_active",
    )