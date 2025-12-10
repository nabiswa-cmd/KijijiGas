from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg
from django.utils.timezone import now

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

    def average_rating(self):
        return Rating.objects.filter(supplier=self).aggregate(avg=Avg('rating'))['avg'] or 0

    def todays_orders(self):
        return self.order_set.filter(created_at__date=now().date())

    def todays_total_sell(self):
        return sum(order.quantity * self.refill_price for order in self.todays_orders())

    def __str__(self):
        return f"{self.name} ({self.location})"


# ---------------- ORDER ----------------
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("On the Way", "On the Way"),
        ("Delivered", "Delivered"),
    ]
    PAYMENT_CHOICES = [
        ("unpaid", "Unpaid"),
        ("payment_pending", "Payment Pending"),
        ("paid", "Paid"),
    ]

    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)  # for unregistered customers
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=15)  # phone entered by staff
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default="unpaid")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name or (self.customer.username if self.customer else 'Guest')}"


# ---------------- RATING ----------------
class Rating(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1–5
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.username} → {self.supplier.name} ({self.rating}/5)"
