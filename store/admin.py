from django.contrib import admin
from .models import ProductCategory, Product, Cart, CartItem, Order, OrderItem

from django.contrib import admin
from .models import ProductCategory, Product, ShirtSize, TrouserSize, FootwearSize


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'category', 'price', 'quantity_available', 'created_at', 'seller', 'brand_name', 'listing_date',
        'manufacturing_date', 'expiry_date', 'highlights', 'color', 'fabric'
    )
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'category__name', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def get_form(self, request, obj=None, **kwargs):
        form = super(ProductAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['shirt_sizes'].widget.can_add_related = False
        form.base_fields['trouser_sizes'].widget.can_add_related = False
        form.base_fields['footwear_sizes'].widget.can_add_related = False
        return form


admin.site.register(ProductCategory)
admin.site.register(ShirtSize)
admin.site.register(TrouserSize)
admin.site.register(FootwearSize)
admin.site.register(Product, ProductAdmin)


class CartItemInline(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    list_display = ['user']
    search_fields = ['user__username']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ['product_name', 'quantity', 'price', 'total_price']
    readonly_fields = ['product_name', 'quantity', 'price', 'total_price']

    def product_name(self, instance):
        return instance.product.name

    product_name.short_description = 'Product Name'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'order_date', 'payment_method', 'total', 'shipping_status']
    search_fields = ['order_id', 'user__username']
    list_filter = ['order_date', 'payment_method', 'shipping_status']
    inlines = [OrderItemInline]


admin.site.register(Cart, CartAdmin)
admin.site.register(Order, OrderAdmin)

from django.contrib import admin
from .models import Payments


class PaymentsAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'card_number', 'cvv_code', 'expiry_date',
        'billing_city', 'billing_pin_code', 'billing_state',
        'mobile', 'card_type', 'payment_method'
    )
    list_filter = ('payment_method',)
    search_fields = ('user__username', 'order__order_id')


admin.site.register(Payments, PaymentsAdmin)

from django.contrib import admin
from .models import Shipping


class ShippingAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'customer_name', 'address', 'total_value', 'order_date', 'courier_name', 'tracking_id',
        'shipping_date_time', 'expected_delivery_date', 'delivery_status')
    list_filter = ('delivery_status',)
    search_fields = ('order__order_id', 'order__full_name', 'order__address', 'order__total', 'order__order_date')

    def order_id(self, obj):
        return obj.order.order_id

    def customer_name(self, obj):
        return obj.order.full_name

    def address(self, obj):
        return obj.order.address

    def total_value(self, obj):
        return obj.order.total

    def order_date(self, obj):
        return obj.order.order_date

    order_id.short_description = 'Order ID'
    customer_name.short_description = 'Customer Name'
    address.short_description = 'Address'
    total_value.short_description = 'Total Value'
    order_date.short_description = 'Order Date'


admin.site.register(Shipping, ShippingAdmin)
