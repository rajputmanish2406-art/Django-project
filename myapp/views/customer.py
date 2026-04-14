from django.shortcuts import render, HttpResponse, redirect,get_object_or_404
# added manually
from myapp.models import MENU1,Customer,Cart,OrderItem,Order,Review,Reservation
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.db.models import Avg,Sum
from django import template
# For Paymant
import hashlib
import random
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
                                                                           

# Create your views here.
def home1(request):
    items = MENU1.objects.all()[:10]   # max 10 items
    return render(request, 'home.html', {'items': items})
def home(request):
    items = MENU1.objects.all()[:10]   # max 10 items
    return render(request, 'home.html', {'items': items})
# Menu viwe her
@login_required(login_url='login')
def menu(request):
    category = request.GET.get('category')  # veg / chicken
  
    if category:
        items = MENU1.objects.filter(category=category, is_available=True)
    else:
        items = MENU1.objects.filter(is_available=True)

    return render(request, 'menu.html', {
        'items': items,
        'selected_category': category
    })
    items  = MENU1.objects.filter(is_available=True)
    return render(request,'menu.html',{'items':items })


#review  or menu_detail
@login_required(login_url='login')
def menu_detail(request, id):
    item = get_object_or_404(MENU1, id=id)
    reviews = item.reviews.all().order_by('-created_at')
    
    # Calculate Average
    avg_query = reviews.aggregate(Avg('rating'))['rating__avg']
    average_rating = avg_query if avg_query is not None else 0
    
    # Calculate Percentage for CSS stars 
    star_percentage = (average_rating / 5) * 100

    if request.method == "POST" and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        Review.objects.create(
            product=item,
            user=request.user,
            rating=int(rating),
            comment=comment
        )
        return redirect('menu_detail', id=id)

    context = {
        'menu': item, 
        'reviews': reviews,
        'average_rating': average_rating,
        'star_percentage': star_percentage,
    }
    return render(request, 'menu_detail.html', context)

# Signup viwe here
def sign_up(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # PHONE VALIDATION
        if not phone.isdigit() or len(phone) != 10 or phone[0] not in "6789":
            return render(request, 'signup.html', {
                'error': 'Please enter a valid  phone number.'
            })        
        #  1. EMPTY CHECK
        if not name:
            return render(request, 'signup.html', {
                'error': 'Name is required'
            })

        #  2. DUPLICATE CHECK (IMPORTANT)
        if User.objects.filter(username=name).exists():
            return render(request, 'signup.html', {
                'error': 'Name already exists. Please choose a different name.'
            })

        try:
            #  3. CREATE USER
            user = User.objects.create_user(
                username=name,
                email=email,
                password=password,
                first_name=name
            )
            user.save()

            Customer.objects.create(
                user=user,
                name=name,
                phone=phone
            )

            return redirect('login')

        except IntegrityError:
            # 🔥 DB safety net
            return render(request, 'signup.html', {
                'error': 'Name already exists. Please choose a different name.'
            })

    return render(request, 'signup.html')
#login viwe here
def login_view(request):
    # Check if user is already logged in; if so, send them home immediately
    if request.user.is_authenticated:
        return redirect('home1')

    if request.method == "POST":
        name = request.POST.get('name')
        password = request.POST.get('password')
        
        user = authenticate(request, username=name, password=password)
        
        # if user is not None:
        if user and not user.is_staff:
            login(request, user)
            # After login, redirect to the 'menu' URL name
            print("login success")
            return redirect('menu') 
            print("login success")
        else:
            # Add an error message here if you want
            return render(request, 'login.html', {'alert1': 'Wrong Email Name or Password plase Try again '})
            
    return render(request,'login.html')
    
# logout viwe here
def logout_view(request):
            logout(request)
            return redirect('home1')

# Cart viwe here :
@login_required(login_url='login')  # Redirects to 'login' page if not logged in
def cart_page(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required(login_url='login')
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")

        product = MENU1.objects.get(id=product_id)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return JsonResponse({
            "success": True,
            "message": "Item added to cart"
        })

    return JsonResponse({"success": False})


def update_cart(request):
    if request.method == "POST":
        cart_id = request.POST.get('cart_id')
        action = request.POST.get('action')

        cart = Cart.objects.get(id=cart_id)

        if action == "plus":
            cart.quantity += 1
        elif action == "minus" and cart.quantity > 1:
            cart.quantity -= 1

        cart.save()
        return JsonResponse({'success': True})

def remove_item(request):
    if request.method == "POST":
        cart_id = request.POST.get('cart_id')
        Cart.objects.get(id=cart_id).delete()
        return JsonResponse({'success': True})



# oder plase
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect("cart")

    total = sum(item.total_price() for item in cart_items)

    # Optional: Customer data auto-fill
    customer = Customer.objects.filter(user=request.user).first()

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "total": total,
        "customer": customer
    })


#  PLACE ORDER (Create order + order items + clear cart)
@login_required
def place_order(request):
    if request.method == "POST":
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return redirect("cart")

        full_name = request.POST.get("full_name")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")
        payment_method = request.POST.get("payment")

        # total calculate
        total = sum(item.total_price() for item in cart_items)

        # create order
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            pincode=pincode,
            payment_method=payment_method
        )

        # LOOP — sab items save karo
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # cart clear
        cart_items.delete()

        #  redirect LOOP ke baad
        if payment_method == "online":
            return redirect("payu_payment", order.id)

        return redirect("track_order", order.id)

    return redirect("checkout")
# Upi page ----
def payu_payment(request, order_id):
    order = Order.objects.get(id=order_id)

    txnid = f"TXN{random.randint(10000,99999)}"
    order.txnid = txnid
    order.save()

    hashh = generate_hash(order, txnid)

    context = {
        "action": settings.PAYU_BASE_URL,
        "hash": hashh,
        "txnid": txnid,
        "amount": "{:.2f}".format(order.total_amount),
        "productinfo": "Order Payment",
        "firstname": order.user.username,
        "email":  order.user.email if order.user.email else"test@test.com",
        "phone": order.phone ,
        "key": settings.PAYU_MERCHANT_KEY,
        "surl": f"http://127.0.0.1:8000/payment-success/{order.id}/",
        "furl": f"http://127.0.0.1:8000/payment-fail/{order.id}/",
    }

    return render(request, "payu_payment.html", context)

    return render(request, "payu_payment.html", context)
@csrf_exempt
def payment_success(request, order_id):
    order = Order.objects.get(id=order_id)
    order.is_paid = True
        
    order.save()
    Cart.objects.filter(user=order.user).delete()
        
    return redirect("menu")
def generate_hash(order, txnid):

    amount = "{:.2f}".format(order.total_amount)
    firstname = order.user.username
    email =  order.user.email if order.user.email else"test@test.com"
    productinfo = "Order Payment"

    hash_string = (
        f"{settings.PAYU_MERCHANT_KEY}|{txnid}|{amount}|{productinfo}|"
        f"{firstname}|{email}|||||||||||{settings.PAYU_SALT}"
    )

    return hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
def track_order(request, id):
    order = get_object_or_404(Order, id=id, user=request.user)

    order_items = order.items.all()   #  IMPORTANT

    return render(request, 'track_order.html', {
        'order': order,
        'order_items': order_items
    })
def my_track_order(request):
    if not request.user.is_authenticated:
        return redirect("login")

    # Latest active order
    order = Order.objects.filter(
        user=request.user
    ).exclude(status__in=["Delivered", "Cancelled"]).order_by("-created_at").first()

    if order:
        return redirect("track_order", order.id)

    # Agar koi active order nahi
    return redirect("home") 
# order history
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "order_history.html", {
        "orders": orders
    })
# Table booking

MAX_CAPACITY = 500

def table_reservation(request):

    if request.method == "POST":

        date = request.POST['date']
        time = request.POST['time']
        guests = int(request.POST['guests'])

        # calculate already booked seats
        booked = Reservation.objects.filter(
            date=date,
            time=time
        ).aggregate(total=Sum('guests'))['total'] or 0

        if booked + guests > MAX_CAPACITY:
            return render(request,'reservation.html',{
                'error': 'Sorry! Restaurant is full for this time slot.'
            })

        Reservation.objects.create(
            user=request.user,
            name=request.POST['name'],
            phone=request.POST['phone'],
            date=date,
            time=time,
            guests=guests,
            special_request=request.POST['request']
        )

        return redirect("home")

    return render(request,'reservation.html')