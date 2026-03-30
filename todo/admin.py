from django.contrib import admin
from .models import InventoryItem


@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "quantity", "category", "is_low_stock", "created_at", "updated_at")
    list_filter = ("category", "user")
    search_fields = ("name", "description")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)