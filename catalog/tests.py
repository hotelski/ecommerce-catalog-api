from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class RootRedirectTests(SimpleTestCase):
    def test_root_redirects_to_api(self):
        # The project root should send users to the API entry point.
        response = self.client.get("/")

        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(response["Location"], "/api/")


class CategoryAPITests(APITestCase):
    def test_category_crud(self):
        # Create a category through the API and keep its ID for later requests.
        create_response = self.client.post(
            "/api/categories/",
            {"name": "Electronics"},
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        category_id = create_response.data["id"]

        # Confirm the category can be retrieved after creation.
        retrieve_response = self.client.get(f"/api/categories/{category_id}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["name"], "Electronics")

        # Update only the category name and verify the API returns the new value.
        update_response = self.client.patch(
            f"/api/categories/{category_id}/",
            {"name": "Tech"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "Tech")

        # Delete the category and confirm it is no longer stored in the database.
        delete_response = self.client.delete(f"/api/categories/{category_id}/")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Category.objects.filter(id=category_id).exists())


class ProductAPITests(APITestCase):
    def setUp(self):
        # Most product tests need a category because Product.category is required.
        self.category = Category.objects.create(name="Electronics")

    def product_payload(self, **overrides):
        # Build a valid product request body and allow each test to override fields.
        payload = {
            "title": "Phone",
            "description": "Smartphone",
            "sku": "PHONE-001",
            "price": "499.99",
            "category": self.category.id,
        }
        payload.update(overrides)
        return payload

    def test_product_crud(self):
        # Create a product through the API and keep its ID for follow-up requests.
        create_response = self.client.post(
            "/api/products/",
            self.product_payload(),
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        product_id = create_response.data["id"]

        # Retrieve the product and confirm the SKU matches the created record.
        retrieve_response = self.client.get(f"/api/products/{product_id}/")
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data["sku"], "PHONE-001")

        # Patch the price to verify partial product updates are supported.
        update_response = self.client.patch(
            f"/api/products/{product_id}/",
            {"price": "449.99"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["price"], "449.99")

        # Delete the product and confirm the database row is removed.
        delete_response = self.client.delete(f"/api/products/{product_id}/")
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=product_id).exists())

    def test_sku_must_be_unique(self):
        # Seed an existing product with the SKU that the API request will reuse.
        Product.objects.create(
            title="Phone",
            description="Smartphone",
            sku="PHONE-001",
            price="499.99",
            category=self.category,
        )

        # Submitting the same SKU should fail validation instead of creating a duplicate.
        response = self.client.post(
            "/api/products/",
            self.product_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sku", response.data)

    def test_search_by_q_matches_title_or_sku(self):
        # Create products whose title and SKU can be matched by the general query.
        Product.objects.create(
            title="Gaming Laptop",
            description="Portable computer",
            sku="LAPTOP-001",
            price="1299.00",
            category=self.category,
        )
        Product.objects.create(
            title="Wireless Headphones",
            description="Audio gear",
            sku="AUDIO-001",
            price="199.00",
            category=self.category,
        )

        # The q parameter should match title text and SKU text case-insensitively.
        title_response = self.client.get("/api/products/search/", {"q": "gaming"})
        sku_response = self.client.get("/api/products/search/", {"q": "audio"})

        # The title search should return only the laptop product.
        self.assertEqual(title_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(title_response.data), 1)
        self.assertEqual(title_response.data[0]["sku"], "LAPTOP-001")

        # The SKU search should return only the headphones product.
        self.assertEqual(sku_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(sku_response.data), 1)
        self.assertEqual(sku_response.data[0]["sku"], "AUDIO-001")

    def test_search_filters_by_price_range(self):
        # Create products below, inside, and above the requested price range.
        Product.objects.create(
            title="Budget Cable",
            description="Cable",
            sku="CABLE-001",
            price="10.00",
            category=self.category,
        )
        Product.objects.create(
            title="Keyboard",
            description="Mechanical keyboard",
            sku="KEYBOARD-001",
            price="75.00",
            category=self.category,
        )
        Product.objects.create(
            title="Monitor",
            description="Display",
            sku="MONITOR-001",
            price="250.00",
            category=self.category,
        )

        # Only products with prices between min_price and max_price should be returned.
        response = self.client.get(
            "/api/products/search/",
            {"min_price": "50.00", "max_price": "100.00"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["sku"], "KEYBOARD-001")

    def test_search_filters_by_category_with_children(self):
        # Products in child categories should be included when filtering by the parent.
        phones = Category.objects.create(name="Phones", parent=self.category)
        books = Category.objects.create(name="Books")
        Product.objects.create(
            title="Phone",
            description="Smartphone",
            sku="PHONE-001",
            price="499.99",
            category=phones,
        )
        Product.objects.create(
            title="Novel",
            description="Book",
            sku="BOOK-001",
            price="19.99",
            category=books,
        )

        # Search by the parent category ID, not the child category ID.
        response = self.client.get(
            "/api/products/search/",
            {"category": str(self.category.id)},
        )

        # The response should include the child category product and exclude unrelated ones.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["sku"], "PHONE-001")

    def test_search_returns_400_for_invalid_price_range(self):
        # min_price greater than max_price is invalid input for the search endpoint.
        response = self.client.get(
            "/api/products/search/",
            {"min_price": "100.00", "max_price": "50.00"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
