from rest_framework import serializers
from .models import InventoryItem, StockAdjustment


class StockAdjustmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = StockAdjustment
        fields = (
            "id",
            "user",
            "old_quantity",
            "new_quantity",
            "reason",
            "note",
            "created_at",
        )


class InventoryItemSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    recent_adjustments = serializers.SerializerMethodField()

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
            "recent_adjustments",
        )

    def get_recent_adjustments(self, obj):
        # Return last 5 adjustments for each item
        adjustments = obj.adjustments.all()[:5]
        return StockAdjustmentSerializer(adjustments, many=True).data

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_low_stock_threshold(self, value):
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        return value