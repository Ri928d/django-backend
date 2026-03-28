from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import InventoryItemSerializer
from .models import InventoryItem


class InventoryItemView(viewsets.ModelViewSet):
    serializer_class = InventoryItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return InventoryItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)