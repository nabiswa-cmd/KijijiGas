from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('supplier/register/', views.supplier_register, name='supplier_register'),
    path('supplier/<int:supplier_id>/', views.supplier_profile, name='supplier_profile'),
    path('supplier/<int:supplier_id>/order/', views.place_order, name='place_order'),
    path('supplier/<int:supplier_id>/rate/', views.rate_supplier, name='rate_supplier'),
]
