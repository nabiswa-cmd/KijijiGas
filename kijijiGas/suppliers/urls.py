from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('supplier/register/', views.supplier_register, name='supplier_register'),
    path('supplier/<int:id>/', views.supplier_profile, name='supplier_profile'),
    path('supplier/<int:id>/order/', views.place_order, name='place_order'),
    path('supplier/<int:supplier_id>/rate/', views.rate_supplier, name='rate_supplier'),
    path("customer/register/", views.customer_register, name="customer_register"),
    path("supplier/register/", views.supplier_register, name="supplier_register"),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="user_logout"),
    path('dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('edit-profile/', views.edit_supplier_profile, name='edit_supplier_profile'),
    path('orders/', views.supplier_orders, name='supplier_orders'),
    path('orders/<int:order_id>/on-the-way/', views.mark_on_the_way, name='mark_on_the_way'),
    path('update-price/', views.update_refill_price, name='change_price'),
    path('orders/mark-delivered/<int:order_id>/', views.mark_delivered, name='mark_delivered'),
    path('payment/<int:order_id>/', views.payment_form, name='payment_form'),
    path("cancel_order/<int:order_id>/", views.cancel_order, name="cancel_order"),
    path("cancel_order1/<int:order_id>/", views.cancel_order1, name="cancel_order1"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)