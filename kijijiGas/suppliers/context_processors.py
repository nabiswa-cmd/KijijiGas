from .models import Order

def unread_orders_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'suppliers'):
        supplier = request.user.suppliers
        unread_orders = Order.objects.filter(supplier=supplier, status="Pending").count()
        return {'unread_orders': unread_orders}
    return {'unread_orders': 0}

def supplier_info(request):
    """
    Makes logged-in supplier info globally available in templates.
    """
    if request.user.is_authenticated and hasattr(request.user, 'suppliers'):
        supplier = request.user.suppliers
        return {
            'supplier_phone': supplier.Payment_number,
            'supplier_name': supplier.name,
            'supplier_id': supplier.id,
        }
    return {
        'supplier_phone': None,
        'supplier_name': None,
        'supplier_id': None,
    }
