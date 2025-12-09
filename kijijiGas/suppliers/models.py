from django.db import models
from django.contrib.auth.models import User


class Suppliers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    # Supplier image with default fallback
    image = models.ImageField(
        upload_to='supplier_images/',
        null=True,
        blank=True,
        default='default.jpg'
    )

    location = models.CharField(max_length=100)
    refill_price = models.DecimalField(max_digits=10, decimal_places=2)

    gas_brand = models.CharField(max_length=50, null=True, blank=True)
    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.location})"


class Order(models.Model):
    # Relationship to User
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50, default="Pending")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"


class Rating(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)

    rating = models.IntegerField()  # 1–5
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} → {self.supplier.name} ({self.rating}/5)"
