from django.contrib import admin
from .models import Suppliers
from .models import Order
from .models import Rating
# Register your models here.
admin.site.register(Suppliers)
admin.site.register(Order)
admin.site.register(Rating)
