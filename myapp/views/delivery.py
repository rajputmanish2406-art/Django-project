from django.shortcuts import render, redirect,get_object_or_404
from myapp.models import DeliveryBoy
from myapp.models import MENU1,Customer,Cart,OrderItem,Order,Review


def delivery_signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        #  check duplicate phone
        if DeliveryBoy.objects.filter(phone=phone).exists():
            return render(request, 'delivery/signup_delivery.html', {
                'error': 'Phone number already exists'
            })

        DeliveryBoy.objects.create(
            name=name,
            phone=phone,
            password=password
        )
        return redirect('delivery_login')

    return render(request, 'delivery/signup_delivery.html')

def delivery_login(request):
    if request.method == "POST":
        phone = request.POST['phone']
        password = request.POST['password']

        try:
            boy = DeliveryBoy.objects.get(phone=phone, password=password)
            request.session['delivery_id'] = boy.id   #  session create
            return redirect('delivery_dashboard')
        except DeliveryBoy.DoesNotExist:
            return render(request, 'delivery/login_delivery.html', {'error': 'Invalid credentials'})

    return render(request, 'delivery/login_delivery.html')
def delivery_dashboard(request):
    if 'delivery_id' not in request.session:
        return redirect('delivery_login')

    boy = DeliveryBoy.objects.get(id=request.session['delivery_id'])

    orders_count = Order.objects.filter(
        delivery_boy=boy,
        status="Out for Delivery"
    ).count()

    return render(request, 'delivery/dashboard.html', {
        'boy': boy,
        'orders_count': orders_count
    })
def delivery_orders(request):
    if 'delivery_id' not in request.session:
        return redirect('delivery_login')

    boy = DeliveryBoy.objects.get(id=request.session['delivery_id'])

    orders = Order.objects.filter(
        delivery_boy=boy,
        status="Out for Delivery"
    ).order_by('-created_at')

    return render(request, 'delivery/orders.html', {'orders': orders})


def delivery_complete(request, id):
    # Logic remains the same, just redirects back to the main dashboard
    if 'delivery_id' not in request.session:
        return redirect('delivery_login')

    boy = get_object_or_404(DeliveryBoy, id=request.session['delivery_id'])
    order = get_object_or_404(Order, id=id, delivery_boy=boy)

    order.status = "Delivered"
    order.save()

    boy.is_available = True
    boy.save()

    return redirect('delivery_dashboard')
def delivery_logout(request):
    request.session.flush()
    return redirect('home1')


