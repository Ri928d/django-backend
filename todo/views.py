from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import InventoryItemSerializer, StockAdjustmentSerializer
from .models import InventoryItem, StockAdjustment


class InventoryItemView(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InventoryItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        item = serializer.save(user=self.request.user)
        # Log creation
        StockAdjustment.objects.create(
            item=item,
            user=self.request.user,
            old_quantity=0,
            new_quantity=item.quantity,
            reason="created",
            note=f"Item '{item.name}' created",
        )

    def perform_update(self, serializer):
        old_quantity = serializer.instance.quantity
        item = serializer.save()
        new_quantity = item.quantity

        # Only log if quantity actually changed
        if old_quantity != new_quantity:
            # Figure out the reason based on the change
            diff = new_quantity - old_quantity
            if diff == 1:
                reason = "increase"
            elif diff == -1:
                reason = "decrease"
            else:
                reason = "edit"

            StockAdjustment.objects.create(
                item=item,
                user=self.request.user,
                old_quantity=old_quantity,
                new_quantity=new_quantity,
                reason=reason,
                note=f"Quantity changed from {old_quantity} to {new_quantity}",
            )

    def perform_destroy(self, instance):
        # Log deletion before removing
        StockAdjustment.objects.filter(item=instance).delete()
        instance.delete()

    @action(detail=True, methods=["get"], url_path="history")
    def history(self, request, pk=None):
        """Get full stock adjustment history for a specific item."""
        item = self.get_object()
        adjustments = StockAdjustment.objects.filter(item=item)
        serializer = StockAdjustmentSerializer(adjustments, many=True)
        return Response(serializer.data)