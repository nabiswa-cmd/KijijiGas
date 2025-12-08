from django.shortcuts import render, get_object_or_404, redirect
from .models import Suppliers, Order, Rating
from django.contrib.auth.decorators import login_required
from .form import SupplierRegistrationForm

# Create your views here.
def home(request):
    suppliers = Suppliers.objects.all()
    # Get search query and filter parameters from GET
    query = request.GET.get('q', '')
    location = request.GET.get('location', '')

    if query:
        suppliers = suppliers.filter(name__icontains=query)
    if location:
        suppliers = suppliers.filter(location__icontains=location)

    context = {
        'suppliers': suppliers,
        'query': query,
        'location': location,
    }
    return render(request, 'suppliers/home.html', context)

def supplier_profile(request, supplier_id):
    supplier = get_object_or_404(Suppliers, id=supplier_id)
    return render(request, 'supplier_profile.html', {'suppliers': supplier})

@login_required
def place_order(request, supplier_id):
    supplier = get_object_or_404(Suppliers, id=supplier_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        Order.objects.create(customer=request.user, supplier=supplier, quantity=quantity)
        return redirect('home')
    return render(request, 'suppliers/order_form.html', {'supplier': supplier})

@login_required
def rate_supplier(request, supplier_id):
    supplier = get_object_or_404(Suppliers, id=supplier_id)
    if request.method == 'POST':
        rating_val = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        Rating.objects.create(customer=request.user, supplier=supplier, rating=rating_val, comment=comment)
        # Update supplier average rating
        ratings = Rating.objects.filter(supplier=supplier)
        supplier.rating = sum(r.rating for r in ratings)/ratings.count()
        supplier.save()
        return redirect('supplier_profile', supplier_id=supplier.id)
    return render(request, 'suppliers/rate_supplier.html', {'supplier': supplier})

def supplier_register(request):
    if request.method == 'POST':
        form = SupplierRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # back to homepage
    else:
        form = SupplierRegistrationForm()
    return render(request, 'suppliers/supplier_register.html', {'form': form})