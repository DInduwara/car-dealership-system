from django.contrib import admin

from .models import Car, CarPhoto


class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    extra = 0


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("vin", "make", "model", "year", "status", "location", "base_price", "discount_price")
    list_filter = ("status", "location", "make", "model", "year")
    search_fields = ("vin", "make", "model")
    inlines = [CarPhotoInline]


@admin.register(CarPhoto)
class CarPhotoAdmin(admin.ModelAdmin):
    list_display = ("car", "s3_key", "sort_order", "is_primary")