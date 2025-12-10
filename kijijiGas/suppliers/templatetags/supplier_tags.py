from django import template
from suppliers.models import Suppliers

register = template.Library()

@register.filter
def has_supplier(user):
    return Suppliers.objects.filter(user=user).exists()
