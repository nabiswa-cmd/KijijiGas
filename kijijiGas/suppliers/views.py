from django.shortcuts import render, get_object_or_404, redirect
from .models import Suppliers, Order, Rating
from django.contrib.auth.decorators import login_required
from .form import SupplierRegistrationForm , CustomerRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect
from django.utils.timezone import now
import requests
import base64
from django.conf import settings
import datetime
from requests.auth import HTTPBasicAuth

def home(request):
    query = request.GET.get('q', '').strip()

    suppliers = Suppliers.objects.all()

    if query:  # Now only runs if query is NOT empty
        suppliers = suppliers.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    # AJAX request
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'suppliers/supplier_cards.html', {'suppliers': suppliers})

    # Normal request
    return render(request, 'suppliers/home.html', {'suppliers': suppliers, 'query': query})

def supplier_profile(request, id):
    supplier = get_object_or_404(Suppliers, id = id)
    return render(request, 'suppliers/supplier_profile.html', {'supplier': supplier})


def place_order(request, id):
    supplier = get_object_or_404(Suppliers, id=id)

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))

        if request.user.is_authenticated:
            # Logged-in user
            customer = request.user
        else:
            # Anonymous user - get name/email/phone from form
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')

            # Option 1: Save anonymous users in User table as "guest"
            customer, created = User.objects.get_or_create(
                username=email,  # using email as username
                defaults={'first_name': name, 'email': email}
            )
            # Optionally, you can store phone somewhere (like in a profile or another table)

        Order.objects.create(customer=customer, supplier=supplier, quantity=quantity)
        return redirect('home')

    return render(request, 'suppliers/order_form.html', {'supplier': supplier})

@login_required
def rate_supplier(request, supplier_id):
    supplier = get_object_or_404(Suppliers, id=supplier_id)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment", "")

        Rating.objects.create(
            customer=request.user,
            supplier=supplier,
            rating=rating,
            comment=comment
        )

        return redirect('supplier_profile', supplier_id)

    return render(request, "suppliers/rate_supplier.html", {"supplier": supplier})

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
            # Username and password are already handled by UserCreationForm
            user.email = form.cleaned_data["email"]
            user.save()
            messages.success(request, "Account created — you can now log in.")
            return redirect("user_login")  # change to your login url name
        else:
            # form invalid — fall through to re-render with errors shown
            messages.error(request, "Please fix the errors below.")
    else:
        form = CustomerRegisterForm()

    return render(request, "suppliers/customer_register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # --- CHECK IF USER IS A SUPPLIER ---
            if hasattr(user, "suppliers"):
                return redirect("supplier_dashboard")   # supplier-only page

            # --- NORMAL CUSTOMER ---
            return redirect("home")

        # Invalid login
        messages.error(request, "Invalid login details")
        return redirect("user_login")

    return render(request, "suppliers/login.html")

def user_logout(request):
    logout(request)
    request.session.flush()
    return redirect("home")
@login_required
def supplier_dashboard(request):
    supplier = get_object_or_404(Suppliers, user=request.user)

    today_orders = Order.objects.filter(
        supplier=supplier,
        created_at__date=datetime.date.today()
    )

    # Calculate earnings safely
    earnings = sum(o.quantity * supplier.refill_price for o in today_orders)

    context = {
        "supplier": supplier,
        "today_orders": today_orders.count(),
        "pending": Order.objects.filter(supplier=supplier, status="Pending").count(),
        "delivered": Order.objects.filter(supplier=supplier, status="Delivered").count(),
        "earnings": earnings,
        # Pass latest orders if you want to show them in template
        "latest_orders": Order.objects.filter(supplier=supplier).order_by('-created_at')[:5],
    }
    return render(request, "suppliers/supplier_dashboard.html", context)

@login_required
def supplier_orders(request):
    supplier = get_object_or_404(Suppliers, user=request.user)
    orders = Order.objects.filter(supplier=supplier).order_by("-created_at")
    return render(request, "suppliers/supplier_orders.html", {"orders": orders})
@login_required
def mark_on_the_way(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = "On the Way"
    order.save()

    
    return redirect("supplier_orders")



def payment_form(request):
    message = None
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = request.POST['amount']

        # Call your MPESA STK push function
        try:
            response = send_stk_push(phone_number, amount)
            message = f"STK Push sent successfully: {response}"
        except Exception as e:
            message = f"Error sending STK Push: {str(e)}"

    return render(request, 'suppliers/payment_form.html', {'message': message})


def send_stk_push(phone_number, amount):
    """
    Function to trigger STK push using MPESA API.
    Replace with actual logic.
    """
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    shortcode = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY
    callback_url = settings.MPESA_CALLBACK_URL

    # Get OAuth token
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    token = response.json()['access_token']

    # Prepare STK push payload
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    payload = {
        "BusinessShortCode": shortcode,
        "Password": passkey,  # usually base64 encoded
        "Timestamp": "20251210120000",  # generate dynamically
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": "Gas Payment",
        "TransactionDesc": "Payment for Gas Delivery"
    }

    headers = {"Authorization": f"Bearer {token}"}
    stk_response = requests.post(stk_url, json=payload, headers=headers)
    return stk_response.json()

@login_required
def edit_supplier_profile(request):
    supplier = request.user.suppliers
    if request.method == 'POST':
        supplier.name = request.POST.get('name')
        supplier.phone = request.POST.get('phone')
        supplier.email = request.POST.get('email')
        supplier.gas_brand = request.POST.get('gas_brand')
        supplier.refill_price = request.POST.get('refill_price')
        if 'image' in request.FILES:
            supplier.image = request.FILES['image']
        supplier.save()
        return redirect('supplier_dashboard')
    return render(request,'')
@login_required
def update_refill_price(request):
    supplier = get_object_or_404(Suppliers, user=request.user)

    if request.method == "POST":
        new_price = request.POST.get("refill_price")
        if new_price:
            try:
                supplier.refill_price = float(new_price)
                supplier.save()
                messages.success(request, "Refill price updated successfully.")
            except ValueError:
                messages.error(request, "Invalid price entered.")
        return redirect("supplier_dashboard")

    # Optional: render a simple form if you want GET to show a page
    return render(request, "suppliers/update_refill_price.html", {"supplier": supplier})

def mark_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order.status = 'delivered'  # or however you track delivery
    order.save()

    return render(request, 'suppliers/payment_form')
    # replace with the name of your orders page URL