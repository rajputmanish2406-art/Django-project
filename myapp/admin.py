from django.contrib import admin
from myapp.models import MENU1,Customer,Cart,Order,OrderItem,Review,Admin,DeliveryBoy,Reservation

# Register your models here.
admin.site.register(MENU1)
admin.site.register(Customer)
admin.site.register(Cart)
admin.site.register(OrderItem)
admin.site.register(Review)
admin.site.register(Admin)
admin.site.register(DeliveryBoy)
admin.site.register(Reservation)




class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)



