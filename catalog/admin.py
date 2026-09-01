from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Show parent categories to make tree relationships easier to inspect.
    list_display = ("id", "name", "parent")
    search_fields = ("name",)
    list_filter = ("parent",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Surface SKU and price in the changelist for quick product lookup.
    list_display = ("id", "title", "sku", "price", "category")
    search_fields = ("title", "sku")
    list_filter = ("category",)
