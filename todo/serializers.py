from rest_framework import serializers
from .models import InventoryItem


class InventoryItemSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = InventoryItem
        fields = (
            "id",
            "user",
            "name",
            "description",
            "quantity",
            "category",
            "low_stock_threshold",
            "image_url",
            "is_low_stock",
            "created_at",
            "updated_at",
        )

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_low_stock_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        return value