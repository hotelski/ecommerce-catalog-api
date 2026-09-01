from django.db import models


class Category(models.Model):
    # A category can point to another category, which creates a simple tree.
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    # SKU is unique so products can be reliably identified outside the database.
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="products/", blank=True)
    sku = models.CharField(max_length=64, unique=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.sku})"
