# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Suppliers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='supplier_images/',default='default.svg') 

    # Supplier physical location
    location = models.CharField(max_length=100)

    # LPG Price
    refill_price = models.DecimalField(max_digits=10, decimal_places=2)

    # Added fields
    gas_brand = models.CharField(max_length=50, null=True, blank=True)
    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.location})"
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.CharField(max_length=200)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Rating(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name