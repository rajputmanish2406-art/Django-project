from django.db import models
# add by me
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField

class MENU1(models.Model):
        Category_Choices=[
                ('veg', 'vegetable'),
                ('Chicken','Chicken'),
                ('South Indian','South Indian'),
         ]
        item_name=models.CharField(max_length=25)
        price=models.IntegerField()
        image=models.ImageField(upload_to='menu/')
        category=models.CharField(max_length=20,default="",choices=Category_Choices)
        description=models.CharField(max_length=50,default="")
        is_available=models.BooleanField(default=True)

        # Admin trker
        created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='menu_created'
        )
        updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='menu_updated'
        )
        updated_at = models.DateTimeField(auto_now=True)
# finish
#     def __str__(self):
#         return self.item_name 

        def __str__(self):
               return f"{self.item_name}"

class Customer(models.Model):
        user=models.OneToOneField(User,on_delete=models.CASCADE)
        name=models.CharField(max_length=100)
        phone = PhoneNumberField()

        def __str__(self):
                return f"{self.name}"
class Admin(models.Model):
        user=models.OneToOneField(User,on_delete=models.CASCADE)
        name=models.CharField(max_length=100)
        phone = PhoneNumberField()

        def __str__(self):
                return f"{self.name}"
class DeliveryBoy(models.Model):
        name=models.CharField(max_length=100)
        phone=PhoneNumberField(unique=True)
        password=models.CharField(max_length=100)
        is_available=models.BooleanField(default=True)

        def __str__(self):
                return f"{self.name}"

# cart function
class Cart(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        product = models.ForeignKey(MENU1, on_delete=models.CASCADE)
        quantity = models.IntegerField(default=1)

        def total_price(self):
                return self.quantity * self.product.price

# Order function 

class Order(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE)
        total_amount = models.IntegerField(default=0)
        created_at = models.DateTimeField(auto_now_add=True)
      

        delivery_boy = models.ForeignKey(
                DeliveryBoy,
                on_delete=models.SET_NULL,
                null=True,
                blank=True
    )
        STATUS_CHOICES = [
                ('Pending', 'Pending'),
                ('Accepted', 'Accepted'),
                ('Delivered', 'Delivered'),
                ('Cancelled', 'Cancelled'),
        ]
        PAYMENT_CHOICES = (
        ('online', 'Online'),
        ('cod', 'Cash on Delivery'),
         )

        status = models.CharField(
            max_length=20,
                choices=STATUS_CHOICES,
                default='Pending'
        )

        # Address fields
        full_name = models.CharField(max_length=100)
        phone = models.CharField(max_length=15)
        address = models.TextField()
        city = models.CharField(max_length=50)
        pincode = models.CharField(max_length=10)
        payment_method = models.CharField(max_length=10,default=True, choices=PAYMENT_CHOICES)
        is_paid = models.BooleanField(default=False)
        txnid = models.CharField(max_length=200, blank=True, null=True)

        transaction_note = models.CharField(max_length=200, blank=True, null=True)
        def __str__(self):
            return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('MENU1', on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.IntegerField(default=0)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product} x {self.quantity}"


#Revie page
class Review(models.Model):
    product = models.ForeignKey(MENU1, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.item_name} ({self.rating}★)"
class Reservation(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    date = models.DateField()
    time = models.TimeField()

    guests = models.IntegerField()

    special_request = models.TextField(blank=True)

    STATUS = [
        ('Pending','Pending'),
        ('Confirmed','Confirmed'),
        ('Cancelled','Cancelled')
    ]

    status = models.CharField(max_length=20, choices=STATUS, default='Pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.time}"
