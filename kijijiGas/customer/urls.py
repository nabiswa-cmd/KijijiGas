from django.urls import path
from . import views

urlpatterns = [
    path('customer_orders/', views.customer_orders, name='customer_orders'),
    path('rate-supplier/<int:order_id>/', views.rate_supplier, name='rate_supplier'),
]
