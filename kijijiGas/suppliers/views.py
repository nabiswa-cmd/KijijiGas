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

    if query:  # Filter suppliers if search query exists
        suppliers = suppliers.filter(
            Q(name__icontains=query) | Q(location__icontains=query)
        )

    # Only add pending_orders attribute if user is a supplier
    if hasattr(request.user, 'suppliers'):
        for supplier in suppliers:
            supplier.pending_orders = Order.objects.filter(
                supplier=supplier,
                status="Pending"
            ).count()

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
            form.save()
        
            messages.success(request, "Account created you can now log in.")
            return redirect("user_login") 
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

    # Unread (pending) orders count
    unread_orders = Order.objects.filter(
        supplier=supplier,
        status="Pending"
    ).count()

    # Today's orders
    today_orders_qs = Order.objects.filter(
        supplier=supplier,
        created_at__date=datetime.date.today()
    )
    today_orders = today_orders_qs.count()

    # Earnings today
    earnings = sum(o.quantity * supplier.refill_price for o in today_orders_qs)

    # Counts
    pending = Order.objects.filter(supplier=supplier, status="Pending").count()
    delivered = Order.objects.filter(supplier=supplier, status="delivered").count()

    # Latest 5 orders
    latest_orders = Order.objects.filter(supplier=supplier).order_by('-created_at')[:5]

    context = {
        "supplier": supplier,
        "today_orders": today_orders,
        "pending": pending,
        "delivered": delivered,
        "earnings": earnings,
        "latest_orders": latest_orders,
        "unread_orders": unread_orders,
    }

    return render(request, "suppliers/supplier_dashboard.html", context)


@login_required
def supplier_orders(request):

    supplier = get_object_or_404(Suppliers, user=request.user)
    
    orders = Order.objects.filter(supplier=supplier).order_by("-created_at")
    return render(request, "suppliers/supplier_orders.html", {"orders": orders , 'supplier': supplier} )
    
def payment_form(request): 
    message = None
    
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = request.POST['amount']

        # Call STK push with supplier ID
        try:
            response = send_stk_push(request, phone_number, amount)
            message = f"STK Push sent successfully: {response}"
        except Exception as e:
            message = f"Error sending STK Push: {str(e)}"

    return render(request, 'suppliers/payment_form.html', {
        'message': message,
    })
@login_required
def send_stk_push(request,phone_number,amount):
    
    supplier_phone = request.user.suppliers.Payment_number
    supplier_name = request.user.suppliers.name
    # generate timestamp, password, token etc...
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    data_to_encode = settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp
    encoded_password = base64.b64encode(data_to_encode.encode()).decode()

    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    token_req = requests.get(auth_url, auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET))
    access_token = token_req.json()['access_token']

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": encoded_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"{supplier_name} GasPayment",
        "TransactionDesc": "Payment for Gas Delivery"
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    stk_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    response = requests.post(stk_url, json=payload, headers=headers)
    return response.json()

@login_required
def edit_supplier_profile(request):
    supplier = request.user.suppliers
    if request.method == 'POST':
        supplier.name = request.POST.get('name')
        supplier.phone = request.POST.get('phone')
        supplier.email = request.POST.get('email')
        supplier.gas_brand = request.POST.get('gas_brand')
        supplier.refill_price = request.POST.get('refill_price')
        supplier.Payment_number = request.POST.get ('Payment_number')
        if 'image' in request.FILES:
            supplier.image = request.FILES['image']
        supplier.save()
        return redirect('supplier_dashboard')
    return render(request,'suppliers/edit_supplier_profile.html')
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
  
def unread_orders_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'suppliers'):
        supplier = request.user.suppliers
        unread_orders = Order.objects.filter(supplier=supplier, status="Pending").count()
        return {'unread_orders': unread_orders}
    return {'unread_orders': 0}

@login_required
def mark_on_the_way(request, order_id):
    order = get_object_or_404(Order, id=order_id, supplier=request.user.suppliers)
    order.status = "on the Way"  # Match exactly the STATUS_CHOICES
    order.save()
    return redirect("supplier_orders")


@login_required
def mark_delivered(request, order_id):
    order = get_object_or_404(Order, id=order_id, supplier=request.user.suppliers)
    order.status = "Delivered"  # Match exactly the STATUS_CHOICES
    order.save()
    return redirect("payment_form")