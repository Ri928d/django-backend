from django.contrib import admin
from .models import InventoryItem, StockAdjustment


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "quantity", "category", "is_low_stock", "created_at", "updated_at")
    list_filter = ("category", "user")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ("item", "user", "old_quantity", "new_quantity", "reason", "created_at")
    list_filter = ("reason", "user")
    search_fields = ("item__name", "note")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)