from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import (
    CategorySerializer,
    ProductSearchQuerySerializer,
    ProductSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    # select_related avoids an extra category query when products are serialized.
    queryset = Product.objects.select_related("category")
    serializer_class = ProductSerializer

    @action(detail=False, methods=["get"])
    def search(self, request):
        # Validate query parameters through a serializer to keep filtering predictable.
        query_serializer = ProductSearchQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        filters = query_serializer.validated_data

        queryset = self.get_queryset()

        q = filters.get("q")
        if q:
            # The general query matches either product title or SKU.
            queryset = queryset.filter(Q(title__icontains=q) | Q(sku__icontains=q))

        title = filters.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        sku = filters.get("sku")
        if sku:
            queryset = queryset.filter(sku__icontains=sku)

        min_price = filters.get("min_price")
        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)

        max_price = filters.get("max_price")
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)

        category_id = filters.get("category")
        if category_id:
            # Include products in the selected category and all nested child categories.
            queryset = queryset.filter(
                category_id__in=self._category_and_descendant_ids(category_id)
            )

        # If pagination is enabled, serialize only the current page and return DRF's
        # paginated response format with metadata such as count, next, and previous.
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def _category_and_descendant_ids(category_id):
        # Start with the selected category so its own products are included.
        category_ids = {category_id}
        # Track the current tree level whose child categories still need to be loaded.
        current_parent_ids = [category_id]

        # Walk the category tree breadth-first until there are no more descendants.
        while current_parent_ids:
            # Load all direct children for the current level in a single database query.
            child_ids = list(
                Category.objects.filter(parent_id__in=current_parent_ids).values_list(
                    "id", flat=True
                )
            )
            # Keep only new child categories to avoid processing the same category twice.
            current_parent_ids = [
                child_id for child_id in child_ids if child_id not in category_ids
            ]
            # Add the newly discovered category IDs to the final result set.
            category_ids.update(current_parent_ids)

        # The search filter uses this set with category_id__in.
        return category_ids
