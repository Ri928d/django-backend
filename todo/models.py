from django.db import models
from django.contrib.auth.models import User


class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ("electronics", "Electronics"),
        ("clothing", "Clothing"),
        ("food", "Food"),
        ("office", "Office"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inventory_items"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="other"
    )
    low_stock_threshold = models.PositiveIntegerField(default=5)
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.name} ({self.quantity})"


class StockAdjustment(models.Model):
    """Audit log for tracking all stock quantity changes."""

    REASON_CHOICES = [
        ("manual", "Manual Adjustment"),
        ("increase", "Stock Increase"),
        ("decrease", "Stock Decrease"),
        ("edit", "Edited via Form"),
        ("created", "Item Created"),
    ]

    item = models.ForeignKey(
        InventoryItem,
        on_delete=models.CASCADE,
        related_name="adjustments"
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_quantity = models.IntegerField()
    new_quantity = models.IntegerField()
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default="manual")
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.item.name}: {self.old_quantity} → {self.new_quantity} ({self.reason})"