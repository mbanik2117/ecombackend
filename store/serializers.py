from rest_framework import serializers
from .models import Product, ProductCategory, CartItem, Order, OrderItem, Cart, Payments
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from .models import Product, ProductCategory, ShirtSize, TrouserSize, FootwearSize


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name']


class ShirtSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShirtSize
        fields = ['id', 'size']


class TrouserSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrouserSize
        fields = ['id', 'size']


class FootwearSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FootwearSize
        fields = ['id', 'size']


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=ProductCategory.objects.all())
    shirt_sizes = ShirtSizeSerializer(many=True)
    trouser_sizes = TrouserSizeSerializer(many=True)
    footwear_sizes = FootwearSizeSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'category_id', 'name', 'description', 'price', 'quantity_available', 'image',
                  'seller', 'brand_name', 'listing_date', 'manufacturing_date', 'expiry_date', 'highlights',
                  'shirt_sizes', 'trouser_sizes', 'footwear_sizes']


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'product_id', 'quantity']
        read_only_fields = ['cart']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')

        # Get the product instance, ensuring it exists
        product = Product.objects.get(id=product_id)

        try:
            user = self.context['request'].user  # Assuming user is authenticated
            cart = Cart.objects.get_or_create(user=user)[0]
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={'quantity': 1}
            )

            # If item already existed, update the quantity (optional)
            # if not created:
            #     cart_item.quantity += 1
            #     cart_item.save()

            return cart_item

        except Product.DoesNotExist:
            raise ValidationError("Product with the specified ID does not exist.")


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'price', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'full_name', 'email', 'address', 'city', 'pin_code',
                  'state', 'mobile', 'order_date', 'payment_method', 'order_id',
                  'total', 'shipping_status', 'items']


class PaymentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'


from .models import Shipping


class ShippingSerializer(serializers.ModelSerializer):
    order_id = serializers.ReadOnlyField(source='order.order_id')
    full_name = serializers.ReadOnlyField(source='order.full_name')
    address = serializers.ReadOnlyField(source='order.address')
    items_ordered = serializers.SerializerMethodField()
    total = serializers.ReadOnlyField(source='order.total')

    def get_items_ordered(self, obj):
        order_items = obj.order.orderitem_set.all()
        items = []
        for order_item in order_items:
            items.append({
                'product_name': order_item.product.name,
                'quantity': order_item.quantity,
                'price': order_item.price,
                'total_price': order_item.total_price,
            })
        return items

    class Meta:
        model = Shipping
        fields = '__all__'