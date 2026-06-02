from django.test import TestCase
from rest_framework.test import APIClient

from store.models import Cart, CartItem, Collection, Customer, Order, Product


class StoreApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.collection = Collection.objects.create(title="Essentials")
        self.product = Product.objects.create(
            title="Desk Lamp",
            slug="desk-lamp",
            description="Warm desk lighting",
            unit_price="49.00",
            inventory=10,
            collection=self.collection,
        )

    def test_product_list_returns_catalog(self):
        response = self.client.get("/api/store/products/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"][0]["title"], "Desk Lamp")
        self.assertTrue(response.data["results"][0]["is_available"])

    def test_cart_item_can_be_added(self):
        cart_response = self.client.post("/api/store/carts/", {})
        cart_id = cart_response.data["id"]

        response = self.client.post(
            f"/api/store/carts/{cart_id}/items/",
            {"product_id": self.product.id, "quantity": 2},
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(CartItem.objects.get(cart_id=cart_id).quantity, 2)

    def test_checkout_creates_order_and_reduces_inventory(self):
        cart = Cart.objects.create()
        CartItem.objects.create(cart=cart, product=self.product, quantity=3)

        response = self.client.post(
            "/api/store/carts/checkout/",
            {
                "cart_id": str(cart.id),
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "phone": "555-0100",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Customer.objects.get(email="ada@example.com").first_name, "Ada")
        self.product.refresh_from_db()
        self.assertEqual(self.product.inventory, 7)
        self.assertFalse(Cart.objects.filter(pk=cart.id).exists())
