from django.contrib import admin
from django.urls import path
# Customer
from myapp.views.customer import home,home1,menu,menu_detail,sign_up,login_view,logout_view,cart_page,add_to_cart,update_cart,remove_item,checkout,place_order, payu_payment,payment_success,track_order,my_track_order,order_history,table_reservation
# Admin 
from myapp.views.admin import admindash,login_view_admin,sign_up_admin,logout_view_admin,menu_list,menu_add,menu_edit,menu_delete,admin_order_list,admin_order_detail,admin_order_status, assign_order,cust_list,orders_report_pdf,menu_report_pdf,users_report_pdf,Report,delivery_boy_list
# Delivery
from myapp.views.delivery import delivery_signup,delivery_login,delivery_dashboard,delivery_logout,delivery_complete,delivery_orders
# added manually

# from myapp import views

urlpatterns = [
    # ------------Customer-----------
    path("",home,name='home'),
    path("home1",home1,name='home1'),
    path("menu",menu,name='menu'),
    path('menu/<int:id>/', menu_detail, name='menu_detail'),
    path("sign_up",sign_up,name='sign_up'),
    path("login",login_view,name='login'),
    path("logout",logout_view,name='logout'),
    path('cart/', cart_page, name='cart'),
    path('add-to-cart/', add_to_cart,name='add_to_cart'),
    path('update-cart/', update_cart,name='update_cart'),
    path('remove-item/', remove_item,name='remove_item'),
    path('checkout/', checkout, name='checkout'),
    path('place-order/',place_order, name='place_order'),
    path('track-order/<int:id>/',track_order, name='track_order'),
    path("my-track-order/",my_track_order, name="my_track_order"),
    path("order-history/",order_history, name="order_history"),
    path("table-reservation/", table_reservation, name="reservation"),
    # ------Payment
    path("payu/<int:order_id>/", payu_payment, name="payu_payment"),
    path("payment-success/<int:order_id>/", payment_success, name="payment_success"),


    # -----------admin------------
    path('admindesh/',admindash,name='admindesh'),
    path('sign_up_adm/',sign_up_admin,name='sign_up_ad'),
    path('login_view_adm/',login_view_admin,name='login_view_ad'),
    path('logout_view_ad/',logout_view_admin,name='logout_view_ad'),
    # Manage the menu
    path('dashboard/menu/', menu_list, name='menu_list'),
    path('dashboard/menu/add/', menu_add, name='menu_add'),
    path('dashboard/menu/edit/<int:id>/', menu_edit, name='menu_edit'),
    path('Delete Menu/<int:id>/',menu_delete,name='menu_delte'),
    # Manage the Oder
    path('dashboard/orders/',admin_order_list, name='admin_order_list'),
    path('dashboard/orders/<int:id>/',admin_order_detail, name='admin_order_detail'),
    path('dashboard/orders/<int:id>/',admin_order_detail, name='admin_order_detail'),
    path('dashboard/orders/status/<int:id>/',admin_order_status, name='admin_order_status'),
    path('order/assign/<int:id>/', assign_order, name='assign_order'),
    path('customerlist',cust_list,name='cust_list'),
    path('delivery-boys/', delivery_boy_list, name='delivery_boy_list'),
    #Repoert 
    path("report/orders/", orders_report_pdf, name="orders_report"),
    path("report/menu/", menu_report_pdf, name="menu_report"),
    path("report/users/", users_report_pdf, name="users_report"),
    path("report/", Report, name="Report"),

    # -----------Delivery BOY --------------
    path('delivery/signup/',delivery_signup, name='delivery_signup'),
    path('delivery/login/',delivery_login, name='delivery_login'),
    path('delivery/logout/',delivery_logout, name='delivery_logout'),

    #--------------oders delivery
    path('delivery/dashboard/', delivery_dashboard, name='delivery_dashboard'),
    path('delivery/orders/',delivery_orders, name='delivery_orders'),
    path('delivery/delivered/<int:id>/',delivery_complete, name='delivery_complete'),
    

    
   
]
    
