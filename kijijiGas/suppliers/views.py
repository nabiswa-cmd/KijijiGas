from django.shortcuts import render, get_object_or_404, redirect
from .models import Suppliers, Order, Rating
from django.contrib.auth.decorators import login_required
from .form import SupplierRegistrationForm , CustomerRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

# Create your views here.
def home(request):
    query = request.GET.get('q', '')

    suppliers = Suppliers.objects.all()
    if query:
        suppliers = suppliers.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'suppliers/supplier_cards.html', {'suppliers': suppliers})
    
    return render(request, 'suppliers/home.html', {'suppliers': suppliers, 'query': query})


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
    if request.method == "POST":
        form = SupplierRegistrationForm(request.POST,request.FILES)

        if form.is_valid():
            # Create user
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = User.objects.create_user(username=username, password=password)
            user.save()

            # Create supplier and link user
            supplier = form.save(commit=False)
            supplier.user = user
            supplier.save()

            login(request, user)
            return redirect("home")

    else:
        form = SupplierRegistrationForm()

    return render(request, "suppliers/supplier_register.html", {"form": form})

def customer_register(request):
    if request.method == "POST":
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            messages.success(request, "Account created. You can now login.")
            return redirect("user_login")
    else:
        form = CustomerRegisterForm()
    return render(request, "suppliers/customer_register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        # Customer login
        if user is not None:
            login(request, user)
            return redirect("home")

        # Supplier login
        try:
            supplier = Suppliers.objects.get(supplier_name=username)
            if supplier.check_password(password):
                request.session["supplier_id"] = supplier.id
                return redirect("home")
        except Suppliers.DoesNotExist:
            pass

        messages.error(request, "Invalid login details")
        return redirect("user_login")

    return render(request, "suppliers/login.html")

def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect("home")
