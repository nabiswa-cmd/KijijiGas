from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
# ---------------- SUPPLIER ----------------
class Suppliers(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    image = models.ImageField(upload_to='supplier_images/', null=True, blank=True, default='default.jpg')
    location = models.CharField(max_length=100)
    refill_price = models.DecimalField(max_digits=10, decimal_places=2)
    gas_brand = models.CharField(max_length=50, null=True, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    Payment_number = models.CharField(max_length=20)

    def average_rating(self):
        return Rating.objects.filter(supplier=self).aggregate(avg=Avg('rating'))['avg'] or 0

    def todays_orders(self):
        return self.order_set.filter(created_at__date=now().date())

    def todays_total_sell(self):
        return sum(order.quantity * self.refill_price for order in self.todays_orders())

    def __str__(self):
        return f"{self.name} ({self.location})"
class Employee(models.Model):
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.supplier.name})"


# ---------------- ORDER ----------------
class Order(models.Model):
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_phone = models.CharField(max_length=15)
    customer_location = models.CharField(max_length=200,null=True)

    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    cash_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    mpesa_paid = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("unpaid", "Unpaid"),
            ("partial", "Partial"),
            ("paid", "Paid"),
        ],
        default="unpaid"
    )

    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_paid(self):
        return self.cash_paid + self.mpesa_paid

    @property
    def total_amount(self):
        return self.quantity * self.supplier.refill_price


# ---------------- RATING ----------------
class Rating(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} → {self.supplier.name} ({self.rating}/5)"

class SupplierWallet(models.Model):
    supplier = models.OneToOneField(Suppliers, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def credit(self, amount):
        self.balance += amount
        self.save()

    def debit(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.save()
