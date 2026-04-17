from django.shortcuts import render, HttpResponse, redirect,get_object_or_404
# added manually
from myapp.models import MENU1,Customer,Cart,OrderItem,Order,Review,Admin,DeliveryBoy
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db import IntegrityError
from django.utils import timezone
from django.db.models import Sum
from datetime import date,timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

def admindash(request):
    one_hour_ago = timezone.now() - timedelta(hours=1)

    orders = Order.objects.filter(
        created_at__gte=one_hour_ago
    ).order_by('-created_at')

    today = date.today()

    total_customers = Customer.objects.count()
    total_orders = Order.objects.count()

    today_orders = Order.objects.filter(created_at__date=today).count()

    total_revenue = Order.objects.filter(status="Delivered").aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    pending_orders = Order.objects.filter(status="Pending").count()
    delivered_orders = Order.objects.filter(status="Delivered").count()

    active_delivery = DeliveryBoy.objects.filter(is_available=False).count()

    context = {
        'orders': orders,  
        'total_customers': total_customers,
        'total_orders': total_orders,
        'today_orders': today_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'delivered_orders': delivered_orders,
        'active_delivery': active_delivery
    }
    return render(request,'admin/Admindashboard.html',context)
# customer show list here
def cust_list(request):
    customer =Customer.objects.all()
    return render(request, 'admin/customer_list.html', {'customer': customer})
# delivery boy show list here
def delivery_boy_list(request):
    delivery_boys = DeliveryBoy.objects.all()
    return render(request, 'admin/deliveryboylist.html', {'delivery_boys': delivery_boys})
# Signup view here Admin
def sign_up_admin(request):
    if request.method == "POST":
        name=request.POST.get('name')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        password=request.POST.get('password')

        admin_user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )
        admin_user.is_staff = True
        admin_user.save()
        Admin.objects.create(
            user=admin_user,
            name=name,
            phone=phone
        )
        return redirect('login_view_ad')
 
    return render(request,'admin/signup_adm.html')

#login viwe here
def login_view_admin(request):
    # Check if user is already logged in; if so, send them home immediately
    if request.user.is_authenticated:
        return redirect('admindesh')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
         # logic for staff users
        if user and user.is_staff:
            login(request, user)
            # After login, redirect to the 'menu' URL name
            print("login success")
            return redirect('admindesh') 
            print("login success")
        else:
            # Add an error message here if you want
            return render(request, 'admin/login_adm.html', {'alert1': 'Wrong Email Name or Password plase Try again '})
            
    return render(request,'admin/login_adm.html')
    
# logout viwe here
def logout_view_admin(request):
        logout(request)
        return redirect('home1')



# ADD item
@staff_member_required(login_url='login_view_ad')
def menu_add(request):
    if request.method == "POST":
        MENU1.objects.create(
            item_name=request.POST['item_name'],
            price=request.POST['price'],
            category=request.POST['category'],
            description=request.POST['description'],
            image=request.FILES['image'],
            created_by=request.user,   #  ADMIN NAME
            updated_by=request.user
        )
        return redirect('menu_list')

    return render(request, 'admin/menu_add.html')
# Edit menu
@staff_member_required(login_url='login_view_ad')
def menu_edit(request, id):
    menu = get_object_or_404(MENU1, id=id)

    if request.method == "POST":
        menu.item_name = request.POST['item_nam']
        menu.price = request.POST['price']
        menu.category = request.POST['category']
        menu.is_available = bool(request.POST.get('available'))
        menu.description = request.POST['description']
        menu.updated_by = request.user   #  EDIT KARNE WALA ADMIN

        if 'image' in request.FILES:
            menu.image = request.FILES['image']

        menu.save()
        return redirect('menu_list')

    return render(request, 'admin/menu_edit.html', {'menu': menu})
#List of Menu
@staff_member_required(login_url='login_view_ad')
def menu_list(request):
    menus = MENU1.objects.all()
    return render(request, 'admin/menulist.html', {'menus': menus})

# Delete Menu
@staff_member_required
def menu_delete(request, id):
    menu = get_object_or_404(MENU1, id=id)
    menu.delete()
    return redirect('menu_list')

# ORDER manage 
@staff_member_required
def admin_order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'admin/order_list.html', {'orders': orders})
# Order Detail
@staff_member_required
def admin_order_detail(request, id):
    order = get_object_or_404(Order, id=id)
    items = order.items.all()   # OrderItem related_name="items"

    return render(request, 'admin/order_detail.html', {
        'order': order,
        'items': items
    })
#  change status
@staff_member_required
def admin_order_status(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        order.status = request.POST['status']
        order.save()

    return redirect('admin_order_detail', id=id)


#- Assign Order
def assign_order(request,id):
    order = Order.objects.get(id=id)
    boys = DeliveryBoy.objects.filter(is_available=True)

    if request.method=="POST":
        boy = DeliveryBoy.objects.get(id=request.POST.get('delivery_boy'))
        order.delivery_boy = boy
        order.status = "Out for Delivery"
        order.save()

        boy.is_available=False
        boy.save()

        # return redirect('admin_order_detail',id=id)
        return redirect('admin_order_list')


    return render(request,'admin/assign_order.html',{
        'order':order,
        'boys':boys
    })
# Repoert Order
def orders_report_pdf(request):
    width=30
    filter_type = request.GET.get("filter", "day")

    now = timezone.now()

    if filter_type == "month":
        start = now - timedelta(days=30)
    elif filter_type == "year":
        start = now - timedelta(days=365)
    else:
        start = now - timedelta(days=1)

    orders = Order.objects.filter(created_at__gte=start)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="orders_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)

    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph("Restaurant Orders Report",styles['Title']))
    elements.append(Spacer(1,20))

    # Table Header
    data = [
        ["Order ID","Customer","Total","Status","Date"]
    ]

    total_revenue = 0

    for o in orders:
        data.append([
            f"#{o.id}",
            o.full_name,
            f"₹{o.total_amount}",
            o.status,
            o.created_at.strftime("%d-%m-%Y")
        ])
        total_revenue += o.total_amount

    table = Table(data, colWidths=[70,150,80,100,100])

    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.red),
        ("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
        ("GRID",(0,0),(-1,-1),1,colors.black),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("ALIGN",(2,1),(2,-1),"RIGHT"),
    ]))

    elements.append(table)

    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"Total Revenue: ₹{total_revenue}", styles['Heading2']))

    doc.build(elements)

    return response
# Menu Repoert
def menu_report_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="menu_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Menu Report", styles['Title']))
    elements.append(Spacer(1,20))

    menus = MENU1.objects.all()

    data = [["ID","Item Name","Category","Price"]]

    for m in menus:
        data.append([
            m.id,
            m.item_name,
            m.category,
            f"₹{m.price}"
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.green),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')
    ]))

    elements.append(table)

    doc.build(elements)

    return response
# Repoert User
def users_report_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="users_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Users Report", styles['Title']))
    elements.append(Spacer(1,20))

    users = User.objects.all()

    data = [["ID","Username","Email","Date Joined"]]

    for u in users:
        data.append([
            u.id,
            u.username,
            u.email,
            str(u.date_joined.date())
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold')
    ]))

    elements.append(table)

    doc.build(elements)

    return response
def Report(request):
    return render(request,'admin/analytics.html')
