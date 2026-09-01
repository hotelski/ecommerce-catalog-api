from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "description", "image", "sku", "price", "category"]


class ProductSearchQuerySerializer(serializers.Serializer):
    # The search endpoint accepts optional filters and validates them before querying.
    q = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)
    sku = serializers.CharField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
    )
    max_price = serializers.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
    )
    category = serializers.IntegerField(required=False, min_value=1)

    def validate(self, attrs):
        min_price = attrs.get("min_price")
        max_price = attrs.get("max_price")

        # Reject impossible price ranges early so the view only handles valid filters.
        if min_price is not None and max_price is not None and min_price > max_price:
            raise serializers.ValidationError(
                "min_price must be less than or equal to max_price."
            )

        return attrs
