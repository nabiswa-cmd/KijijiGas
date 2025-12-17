from django.shortcuts import render, get_object_or_404, redirect
from .models import Suppliers, Order, Rating,Employee,SupplierWallet,OrderMessage
from django.contrib.auth.decorators import login_required
from .form import SupplierRegistrationForm , CustomerRegisterForm ,OrderMessageForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.utils.timezone import now
import requests
import base64
from django.conf import settings
import datetime
from requests.auth import HTTPBasicAuth
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from decimal import Decimal
import json
from customer.models import CustomerProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect


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
            customer_user = request.user
            customer_name = request.user.get_full_name() or request.user.username

            try:
                profile = request.user.customerprofile
                customer_phone = getattr(profile, 'phone', '')
                customer_location = (
                    profile.exact_location
                    or f"{profile.area}, {profile.county}"
                )
            except CustomerProfile.DoesNotExist:
                customer_phone = ''
                customer_location = ''

        else:
            # Anonymous user
            customer_user = None  # no User instance
            customer_name = request.POST.get('name')
            customer_phone = request.POST.get('phone')
            customer_location = request.POST.get('location')

        if not customer_location:
            return render(
                request,
                'suppliers/order_form.html',
                {
                    'supplier': supplier,
                    'error': 'Location is required to place an order'
                }
            )

        # Create the order
        Order.objects.create(
            customer=customer_user,       # User instance for logged-in users
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_location=customer_location,
            supplier=supplier,
            quantity=quantity
        )

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
            user = form.save()

            # ✅ Create customer profile with location
            CustomerProfile.objects.create(
                user=user,
                county=form.cleaned_data["county"],
                area=form.cleaned_data["area"],
                exact_location=form.cleaned_data.get("exact_location", "")
            )
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect("user_login")
        else:
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
@login_required
def payment_form(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    amount = order.quantity * order.supplier.refill_price
    message = None

    if request.method == "POST":
        cash_paid = float(request.POST.get("cash_paid", 0))
        mpesa_paid = float(request.POST.get("mpesa_paid", 0))
        customer_phone = request.POST.get("customer_phone")

        # 🔹 CASH PAYMENT
        if cash_paid > 0:
            order.payment_method = "cash"
            order.amount_paid = cash_paid
            order.payment_status = "paid"
            order.save()

            # credit supplier wallet
            wallet, _ = SupplierWallet.objects.get_or_create(supplier=order.supplier)
            wallet.credit(cash_paid)

            return redirect("supplier_orders")

        # 🔹 MPESA PAYMENT
        elif mpesa_paid > 0:
            order.payment_method = "mpesa"
            order.amount_paid = mpesa_paid
            order.payment_status = "payment_pending"
            order.save()

            # ✅ Correct STK Push call
            send_stk_push(request,
                order=order,
                phone_number=customer_phone,
                amount=mpesa_paid
            )

            message = "STK Push sent to customer."

    return render(request, "suppliers/payment_form.html", {
        "order": order,
        "amount": amount,
        "message": message
    })

@login_required
def send_stk_push(request, order, phone_number, amount):
    supplier = order.supplier
    supplier_name = supplier.name

    phone_number = format_phone(phone_number)

    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()

    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    auth_response = requests.get(
        auth_url,
        auth=HTTPBasicAuth(
            settings.MPESA_CONSUMER_KEY,
            settings.MPESA_CONSUMER_SECRET
        )
    )

    access_token = auth_response.json().get("access_token")

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"ORDER-{order.id}",
        "TransactionDesc": f"Gas payment to {supplier_name}",
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

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
    return redirect("payment_form", order_id=order.id)

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Allowed statuses
    cancellable_status = ["Pending"]

    if order.status not in cancellable_status:
        messages.error(request, "This order can no longer be cancelled.")
        return redirect("customer_orders")

    # Cancel order
    order.status = "Cancelled"
    order.save()

    messages.success(request, "Your order has been cancelled successfully.")
    return redirect("customer_orders")

def cancel_order1 (request, order_id):
    order = get_object_or_404(Order, id=order_id)
    # Allowed statuses
    cancellable_status = ["Pending","on the Way"]

    if order.status not in cancellable_status:
        messages.error(request, "This order can no longer be cancelled.")
        return redirect("supplier_orders")

    # Cancel order
    order.status = "Cancelled"
    order.save()

    messages.success(request, "Your order has been cancelled successfully.")
    return redirect("supplier_orders")

def start_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        employee_id = request.POST.get("employee")
        if employee_id:
            order.employee = Employee.objects.get(id=employee_id)
        order.status = "On the Way"
        order.save()

    return redirect('supplier_orders')

def mark_cash_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.payment_method = "cash"
    order.payment_status = "paid"
    order.amount_paid = order.total_price()
    order.paid_at = now()
    order.save()

    return redirect('supplier_orders')

@csrf_exempt
def mpesa_callback(request):
    data = json.loads(request.body)

    try:
        callback = data['Body']['stkCallback']

        if callback['ResultCode'] == 0:
            metadata = callback['CallbackMetadata']['Item']

            amount = Decimal(next(i['Value'] for i in metadata if i['Name'] == 'Amount'))
            phone = str(next(i['Value'] for i in metadata if i['Name'] == 'PhoneNumber'))
            receipt = next(i['Value'] for i in metadata if i['Name'] == 'MpesaReceiptNumber')

            phone = format_phone(phone)

            order = Order.objects.filter(
                customer_phone=phone,
                payment_status="payment_pending"
            ).last()

            if order:
                order.payment_status = "paid"
                order.mpesa_paid = amount
                order.save()

                wallet, _ = SupplierWallet.objects.get_or_create(
                    supplier=order.supplier
                )
                wallet.credit(amount)

        return JsonResponse({"ResultCode": 0, "ResultDesc": "Accepted"})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
 
@login_required
def send_order_message(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Optional: restrict to supplier/admin
    if not request.user.is_staff:
        return redirect("home")

    if request.method == "POST":
        form = OrderMessageForm(request.POST)
        if form.is_valid():
            OrderMessage.objects.create(
                order=order,
                sender=request.user,
                receiver=order.customer.user,  # if order is linked to user
                message=form.cleaned_data["message"]
            )

    return redirect("supplier_orders")

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # mark messages as read
    order.messages.filter(
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return render(request, "suppliers/order_detail.html", {"order": order})

@login_required
def my_messages(request):
    messages = OrderMessage.objects.filter(
        receiver=request.user
    ).order_by("-created_at")

    return render(
        request,
        "suppliers/my_messages.html",
        {"messages": messages}
    )

@login_required
def send_order_message(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        message_text = request.POST.get("message")

        if request.user == order.supplier.user:
            # Supplier sending to customer
            receiver_user = order.customer  # must be a User instance
        else:
            # Customer sending to supplier
            receiver_user = order.supplier.user

        if receiver_user:  # only create if a valid User exists
            OrderMessage.objects.create(
                order=order,
                sender=request.user,
                receiver=receiver_user,
                message=message_text
            )

    return redirect("order_detail", order_id=order.id)
def format_phone(phone):
    phone = phone.strip()
    if phone.startswith("0"):
        phone = "254" + phone[1:]
    elif phone.startswith("+"):
        phone = phone[1:]
    return phone
