from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import InventoryItem, StockAdjustment


class InventoryItemModelTest(TestCase):
    """Tests for the InventoryItem model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_create_inventory_item(self):
        """Test creating an inventory item with valid data."""
        item = InventoryItem.objects.create(
            user=self.user,
            name="Test Item",
            description="A test item",
            quantity=10,
            category="electronics",
            low_stock_threshold=5,
        )
        self.assertEqual(item.name, "Test Item")
        self.assertEqual(item.quantity, 10)
        self.assertEqual(item.user, self.user)

    def test_is_low_stock_true(self):
        """Test is_low_stock returns True when quantity is below threshold."""
        item = InventoryItem.objects.create(
            user=self.user, name="Low Item", quantity=3, low_stock_threshold=5
        )
        self.assertTrue(item.is_low_stock)

    def test_is_low_stock_false(self):
        """Test is_low_stock returns False when quantity is above threshold."""
        item = InventoryItem.objects.create(
            user=self.user, name="Stocked Item", quantity=10, low_stock_threshold=5
        )
        self.assertFalse(item.is_low_stock)

    def test_is_low_stock_at_threshold(self):
        """Test is_low_stock returns True when quantity equals threshold."""
        item = InventoryItem.objects.create(
            user=self.user, name="Edge Item", quantity=5, low_stock_threshold=5
        )
        self.assertTrue(item.is_low_stock)

    def test_string_representation(self):
        """Test the __str__ method of InventoryItem."""
        item = InventoryItem.objects.create(
            user=self.user, name="Widget", quantity=7
        )
        self.assertEqual(str(item), "Widget (7)")

    def test_default_category(self):
        """Test that default category is 'other'."""
        item = InventoryItem.objects.create(
            user=self.user, name="Default Cat", quantity=1
        )
        self.assertEqual(item.category, "other")

    def test_default_low_stock_threshold(self):
        """Test that default low stock threshold is 5."""
        item = InventoryItem.objects.create(
            user=self.user, name="Default Threshold", quantity=1
        )
        self.assertEqual(item.low_stock_threshold, 5)

    def test_timestamps_auto_set(self):
        """Test that created_at and updated_at are automatically set."""
        item = InventoryItem.objects.create(
            user=self.user, name="Timestamped", quantity=1
        )
        self.assertIsNotNone(item.created_at)
        self.assertIsNotNone(item.updated_at)


class StockAdjustmentModelTest(TestCase):
    """Tests for the StockAdjustment audit log model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="audituser", email="audit@example.com", password="auditpass123"
        )
        self.item = InventoryItem.objects.create(
            user=self.user, name="Audited Item", quantity=10
        )

    def test_create_adjustment(self):
        """Test creating a stock adjustment record."""
        adj = StockAdjustment.objects.create(
            item=self.item,
            user=self.user,
            old_quantity=10,
            new_quantity=15,
            reason="increase",
            note="Restocked",
        )
        self.assertEqual(adj.old_quantity, 10)
        self.assertEqual(adj.new_quantity, 15)
        self.assertEqual(adj.reason, "increase")

    def test_adjustment_string_representation(self):
        """Test the __str__ method of StockAdjustment."""
        adj = StockAdjustment.objects.create(
            item=self.item,
            user=self.user,
            old_quantity=10,
            new_quantity=8,
            reason="decrease",
        )
        self.assertIn("10", str(adj))
        self.assertIn("8", str(adj))

    def test_adjustments_ordered_newest_first(self):
        """Test that adjustments are ordered by newest first."""
        adj1 = StockAdjustment.objects.create(
            item=self.item, user=self.user,
            old_quantity=10, new_quantity=11, reason="increase",
        )
        adj2 = StockAdjustment.objects.create(
            item=self.item, user=self.user,
            old_quantity=11, new_quantity=12, reason="increase",
        )
        adjustments = list(StockAdjustment.objects.filter(item=self.item))
        self.assertEqual(adjustments[0].id, adj2.id)

    def test_adjustment_cascade_delete(self):
        """Test that adjustments are deleted when the item is deleted."""
        StockAdjustment.objects.create(
            item=self.item, user=self.user,
            old_quantity=10, new_quantity=5, reason="decrease",
        )
        self.assertEqual(StockAdjustment.objects.count(), 1)
        self.item.delete()
        self.assertEqual(StockAdjustment.objects.count(), 0)


class InventoryItemAPITest(TestCase):
    """Tests for the Inventory Item API endpoints."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="apiuser", email="api@example.com", password="apipass123"
        )
        self.other_user = User.objects.create_user(
            username="otheruser", email="other@example.com", password="otherpass123"
        )
        # Authenticate
        response = self.client.post(
            "/api/auth/token/",
            {"username": "apiuser", "password": "apipass123"},
            format="json",
        )
        self.token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        # Create a sample item
        self.item = InventoryItem.objects.create(
            user=self.user,
            name="Keyboard",
            description="Mechanical keyboard",
            quantity=15,
            category="electronics",
            low_stock_threshold=5,
        )

    def test_list_items(self):
        """Test listing all inventory items for authenticated user."""
        response = self.client.get("/api/items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Keyboard")

    def test_create_item(self):
        """Test creating a new inventory item via the API."""
        data = {
            "name": "Mouse",
            "description": "Wireless mouse",
            "quantity": 25,
            "category": "electronics",
            "low_stock_threshold": 10,
        }
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Mouse")
        self.assertEqual(response.data["quantity"], 25)
        self.assertEqual(InventoryItem.objects.count(), 2)

    def test_create_item_generates_audit_log(self):
        """Test that creating an item automatically generates an audit log entry."""
        data = {
            "name": "Tracked Item",
            "quantity": 20,
            "category": "office",
            "low_stock_threshold": 5,
        }
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = InventoryItem.objects.get(name="Tracked Item")
        adjustments = StockAdjustment.objects.filter(item=item)
        self.assertEqual(adjustments.count(), 1)
        self.assertEqual(adjustments.first().old_quantity, 0)
        self.assertEqual(adjustments.first().new_quantity, 20)
        self.assertEqual(adjustments.first().reason, "created")

    def test_retrieve_item(self):
        """Test retrieving a single inventory item by ID."""
        response = self.client.get(f"/api/items/{self.item.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Keyboard")
        self.assertEqual(response.data["is_low_stock"], False)

    def test_update_item(self):
        """Test fully updating an inventory item via PUT."""
        data = {
            "name": "Updated Keyboard",
            "description": "Updated description",
            "quantity": 20,
            "category": "office",
            "low_stock_threshold": 8,
        }
        response = self.client.put(
            f"/api/items/{self.item.id}/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Updated Keyboard")
        self.assertEqual(response.data["category"], "office")

    def test_partial_update_item(self):
        """Test partially updating an inventory item via PATCH."""
        response = self.client.patch(
            f"/api/items/{self.item.id}/",
            {"quantity": 3},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["quantity"], 3)
        self.assertEqual(response.data["is_low_stock"], True)

    def test_quantity_change_generates_audit_log(self):
        """Test that updating quantity creates an audit log entry."""
        self.client.patch(
            f"/api/items/{self.item.id}/",
            {"quantity": 10},
            format="json",
        )
        adjustments = StockAdjustment.objects.filter(item=self.item)
        self.assertEqual(adjustments.count(), 1)
        adj = adjustments.first()
        self.assertEqual(adj.old_quantity, 15)
        self.assertEqual(adj.new_quantity, 10)

    def test_no_audit_log_when_quantity_unchanged(self):
        """Test that no audit log is created when quantity stays the same."""
        self.client.patch(
            f"/api/items/{self.item.id}/",
            {"name": "Renamed Keyboard"},
            format="json",
        )
        adjustments = StockAdjustment.objects.filter(item=self.item)
        self.assertEqual(adjustments.count(), 0)

    def test_increase_by_one_sets_reason(self):
        """Test that increasing quantity by 1 sets reason to 'increase'."""
        self.client.patch(
            f"/api/items/{self.item.id}/",
            {"quantity": 16},
            format="json",
        )
        adj = StockAdjustment.objects.filter(item=self.item).first()
        self.assertEqual(adj.reason, "increase")

    def test_decrease_by_one_sets_reason(self):
        """Test that decreasing quantity by 1 sets reason to 'decrease'."""
        self.client.patch(
            f"/api/items/{self.item.id}/",
            {"quantity": 14},
            format="json",
        )
        adj = StockAdjustment.objects.filter(item=self.item).first()
        self.assertEqual(adj.reason, "decrease")

    def test_large_change_sets_edit_reason(self):
        """Test that changing quantity by more than 1 sets reason to 'edit'."""
        self.client.patch(
            f"/api/items/{self.item.id}/",
            {"quantity": 50},
            format="json",
        )
        adj = StockAdjustment.objects.filter(item=self.item).first()
        self.assertEqual(adj.reason, "edit")

    def test_delete_item(self):
        """Test deleting an inventory item."""
        response = self.client.delete(f"/api/items/{self.item.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(InventoryItem.objects.count(), 0)

    def test_create_item_validates_name_required(self):
        """Test that creating an item without a name fails validation."""
        data = {"quantity": 5, "category": "food"}
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_quantity_rejected(self):
        """Test that a negative quantity value is rejected."""
        data = {
            "name": "Bad Item",
            "quantity": -5,
            "category": "other",
            "low_stock_threshold": 5,
        }
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_threshold_rejected(self):
        """Test that a negative low_stock_threshold is rejected."""
        data = {
            "name": "Bad Threshold",
            "quantity": 10,
            "category": "other",
            "low_stock_threshold": -1,
        }
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_low_stock_in_response(self):
        """Test that computed is_low_stock field is in API response."""
        response = self.client.get(f"/api/items/{self.item.id}/")
        self.assertIn("is_low_stock", response.data)

    def test_timestamps_in_response(self):
        """Test that created_at and updated_at are returned."""
        response = self.client.get(f"/api/items/{self.item.id}/")
        self.assertIn("created_at", response.data)
        self.assertIn("updated_at", response.data)

    def test_recent_adjustments_in_response(self):
        """Test that recent_adjustments field is included in item response."""
        response = self.client.get(f"/api/items/{self.item.id}/")
        self.assertIn("recent_adjustments", response.data)

    def test_user_isolation(self):
        """Test that users can only see their own items."""
        InventoryItem.objects.create(
            user=self.other_user, name="Other Item", quantity=5
        )
        response = self.client.get("/api/items/")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Keyboard")

    def test_cannot_access_other_users_item(self):
        """Test that a user cannot retrieve another user's item."""
        other_item = InventoryItem.objects.create(
            user=self.other_user, name="Secret Item", quantity=5
        )
        response = self.client.get(f"/api/items/{other_item.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_delete_other_users_item(self):
        """Test that a user cannot delete another user's item."""
        other_item = InventoryItem.objects.create(
            user=self.other_user, name="Protected Item", quantity=5
        )
        response = self.client.delete(f"/api/items/{other_item.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(InventoryItem.objects.filter(id=other_item.id).exists())

    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated requests are rejected."""
        client = APIClient()
        response = client.get("/api/items/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_denied(self):
        """Test that unauthenticated users cannot create items."""
        client = APIClient()
        data = {"name": "Hacker Item", "quantity": 1}
        response = client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_item_assigned_to_authenticated_user(self):
        """Test that items are automatically assigned to the logged-in user."""
        data = {
            "name": "Auto Assign",
            "quantity": 1,
            "category": "other",
            "low_stock_threshold": 5,
        }
        response = self.client.post("/api/items/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = InventoryItem.objects.get(name="Auto Assign")
        self.assertEqual(item.user, self.user)

    def test_category_choices(self):
        """Test creating items with each valid category option."""
        categories = ["electronics", "clothing", "food", "office", "other"]
        for cat in categories:
            data = {
                "name": f"Item {cat}",
                "quantity": 1,
                "category": cat,
                "low_stock_threshold": 5,
            }
            response = self.client.post("/api/items/", data, format="json")
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                f"Failed for category '{cat}'",
            )


class StockHistoryAPITest(TestCase):
    """Tests for the /items/{id}/history/ endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="histuser", email="hist@example.com", password="histpass123"
        )
        response = self.client.post(
            "/api/auth/token/",
            {"username": "histuser", "password": "histpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_history_endpoint_returns_200(self):
        """Test that the history endpoint returns 200 for a valid item."""
        data = {"name": "History Test", "quantity": 10, "category": "other", "low_stock_threshold": 5}
        create_resp = self.client.post("/api/items/", data, format="json")
        item_id = create_resp.data["id"]
        response = self.client.get(f"/api/items/{item_id}/history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_history_includes_creation_entry(self):
        """Test that item creation is logged in history."""
        data = {"name": "Created Item", "quantity": 8, "category": "food", "low_stock_threshold": 3}
        create_resp = self.client.post("/api/items/", data, format="json")
        item_id = create_resp.data["id"]
        response = self.client.get(f"/api/items/{item_id}/history/")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reason"], "created")
        self.assertEqual(response.data[0]["old_quantity"], 0)
        self.assertEqual(response.data[0]["new_quantity"], 8)

    def test_history_tracks_multiple_changes(self):
        """Test that multiple quantity changes are all recorded."""
        data = {"name": "Multi Change", "quantity": 10, "category": "other", "low_stock_threshold": 5}
        create_resp = self.client.post("/api/items/", data, format="json")
        item_id = create_resp.data["id"]

        # make several changes
        self.client.patch(f"/api/items/{item_id}/", {"quantity": 11}, format="json")
        self.client.patch(f"/api/items/{item_id}/", {"quantity": 10}, format="json")
        self.client.patch(f"/api/items/{item_id}/", {"quantity": 5}, format="json")

        response = self.client.get(f"/api/items/{item_id}/history/")
        self.assertEqual(len(response.data), 4)  # 1 creation + 3 changes

    def test_history_not_accessible_for_other_users_items(self):
        """Test that users cannot view history of another user's items."""
        other_user = User.objects.create_user(
            username="other2", email="other2@example.com", password="other2pass123"
        )
        other_item = InventoryItem.objects.create(
            user=other_user, name="Private Item", quantity=5
        )
        response = self.client.get(f"/api/items/{other_item.id}/history/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_history_unauthenticated_denied(self):
        """Test that unauthenticated users cannot access history."""
        item = InventoryItem.objects.create(
            user=self.user, name="Auth Test", quantity=5
        )
        client = APIClient()
        response = client.get(f"/api/items/{item.id}/history/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)