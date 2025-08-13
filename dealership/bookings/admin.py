from django.contrib import admin

from .models import TestDrive


@admin.register(TestDrive)
class TestDriveAdmin(admin.ModelAdmin):
    list_display = ("car", "customer", "start_at", "end_at", "status", "created_at")
    list_filter = ("status", "start_at")
    search_fields = ("car__vin", "customer__username")