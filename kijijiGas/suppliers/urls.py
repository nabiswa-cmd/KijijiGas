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
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)