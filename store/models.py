# models.py

from accounts.models import CustomUser
from django.db import models
from django.utils import timezone


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.IntegerField()
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    seller = models.CharField(max_length=255, blank=True)
    brand_name = models.CharField(max_length=255, blank=True)
    listing_date = models.DateField(default=timezone.now)
    manufacturing_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    highlights = models.TextField(blank=True)

    # New fields
    SHIRT_SIZES = (
        ('34', '34'),
        ('36', '36'),
        ('38', '38'),
        ('40', '40'),
        ('42', '42'),
        ('44', '44'),
    )
    TROUSER_WAIST_SIZES = (
        ('28', '28'),
        ('30', '30'),
        ('32', '32'),
        ('34', '34'),
        ('36', '36'),
        ('38', '38'),
        ('40', '40'),
    )
    FOOTWEAR_SIZES = (
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10'),
    )
    shirt_sizes = models.ManyToManyField('ShirtSize', blank=True)
    trouser_sizes = models.ManyToManyField('TrouserSize', blank=True)
    footwear_sizes = models.ManyToManyField('FootwearSize', blank=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    fabric = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name


class ShirtSize(models.Model):
    size = models.CharField(max_length=2, choices=Product.SHIRT_SIZES)


class TrouserSize(models.Model):
    size = models.CharField(max_length=2, choices=Product.TROUSER_WAIST_SIZES)


class FootwearSize(models.Model):
    size = models.CharField(max_length=2, choices=Product.FOOTWEAR_SIZES)


class Cart(models.Model):
    # Define the OneToOneField with the correct User model
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='CartItem')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, null=False)


class Order(models.Model):
    SHIPPING_STATUS_CHOICES = [
        ('not_shipped', 'Not Shipped'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),  # Add the 'cancelled' status
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash_on_delivery', 'Cash on Delivery'),
        ('debit_credit_card', 'Debit/Credit Card'),
        ('upi', 'UPI'),
        # Add other payment methods as needed
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    full_name = models.CharField(max_length=255, blank=False, default='')
    email = models.EmailField(blank=False, default='')
    address = models.TextField(blank=False, default='')
    city = models.CharField(max_length=255, blank=False, default='')
    pin_code = models.CharField(max_length=6, blank=False, default='')
    state = models.CharField(max_length=255, blank=False, default='')
    mobile = models.CharField(max_length=15, blank=False, default='')
    order_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=False, default='')
    order_id = models.CharField(max_length=8, unique=True, blank=False, default='')  # Assuming order_id is unique
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_status = models.CharField(max_length=20, choices=SHIPPING_STATUS_CHOICES, default='not_shipped')

    def calculate_total(self):
        order_items = OrderItem.objects.filter(order=self)
        self.total = sum(item.total_price for item in order_items)
        self.save()  # Save the Order with updated total


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Order.PAYMENT_METHOD_CHOICES, default='')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def calculate_total_price(self):
        self.total_price = self.product.price * self.quantity

    def save(self, *args, **kwargs):
        self.calculate_total_price()  # Calculate total price before saving
        super().save(*args, **kwargs)
        self.order.calculate_total()  # Update Order total after saving OrderItem


class Payments(models.Model):
    CARD_CHOICES = [
        ('VISA', 'VISA'),
        ('MasterCard', 'MasterCard'),
        ('Rupay', 'Rupay'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('debit_credit_card', 'Debit/Credit Card'),
        ('upi', 'UPI'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, blank=True, null=True)  # Assuming 16-digit card number
    cvv_code = models.CharField(max_length=3, blank=True, null=True)  # Assuming 3-digit CVV code
    expiry_date = models.CharField(max_length=5, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    billing_city = models.CharField(max_length=255, blank=True, null=True)
    billing_pin_code = models.CharField(max_length=6, blank=True, null=True)
    billing_state = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    card_type = models.CharField(max_length=20, choices=CARD_CHOICES, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)  # Assuming QR Code as an image field

    def save(self, *args, **kwargs):
        if not self.id:  # Check if it's a new instance
            # Fetch user's billing details from the first order and store in Payments model
            first_order = Order.objects.filter(user=self.user).order_by('order_date').first()
            if first_order:
                self.address = first_order.address
                self.billing_city = first_order.city
                self.billing_pin_code = first_order.pin_code
                self.billing_state = first_order.state
                self.mobile = first_order.mobile
        super().save(*args, **kwargs)


class Shipping(models.Model):
    COURIER_CHOICES = [
        ('BLUEDART', 'bluedart'),
        ('Delhivery', 'delhivery'),
        ('INDIA POST', 'india_post'),
        ('Other', 'Other'),
    ]

    DELIVERY_STATUS_CHOICES = [
        ('in_transit', 'In Transit'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    courier_name = models.CharField(max_length=100, choices=COURIER_CHOICES, default='Other')
    tracking_id = models.CharField(max_length=100, blank=True)
    shipping_date_time = models.DateTimeField(default=timezone.now)
    expected_delivery_date = models.DateField()
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='in_transit')

    def __str__(self):
        return f"Shipping for Order {self.order.order_id}"
