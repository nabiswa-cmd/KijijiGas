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

def supplier_profile(request, id):
    supplier = get_object_or_404(Suppliers, id = id)
    return render(request, 'suppliers/supplier_profile.html', {'supplier': supplier})


def place_order(request, id):
    supplier = get_object_or_404(Suppliers, id = id)
    if request.method == 'POST':
        customer = request.POST.get ('customer')
        quantity = int(request.POST.get('quantity', 1))
        Order.objects.create(customer=customer, supplier=supplier, quantity=quantity)
        return redirect('home')
    return render(request, 'suppliers/order_form.html', {'supplier': supplier})

@login_required
def rate_supplier(request, id):
    supplier = get_object_or_404(Suppliers, id=id)
    if request.method == 'POST':
        rating_val = int(request.POST.get('rating'))
        comment = request.POST.get('comment', '')
        Rating.objects.create(customer=request.user, supplier=supplier, rating=rating_val, comment=comment)
        # Update supplier average rating
        ratings = Rating.objects.filter(supplier=supplier)
        supplier.rating = sum(r.rating for r in ratings)/ratings.count()
        supplier.save()
        return redirect('supplier_profile', id = supplier.id)
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