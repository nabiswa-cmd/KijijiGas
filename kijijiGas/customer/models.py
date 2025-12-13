from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    county = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    exact_location = models.TextField(blank=True, null=True)

    # optional for future Google Maps
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.area}, {self.county}"


