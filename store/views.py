from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser

from accounts.serializers import UserSerializer
from . import serializers
from .models import Product, ProductCategory, Cart, CartItem, Order, OrderItem
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import api_view
from .tasks import send_order_confirmation_email, send_order_cancellation_email
from .serializers import (
    ProductSerializer, ProductCategorySerializer,
    CartItemSerializer, OrderSerializer, OrderItemSerializer
)


class HomeView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        products = Product.objects.distinct()
        categories = ProductCategory.objects.all()

        product_serializer = ProductSerializer(products, many=True)
        category_serializer = ProductCategorySerializer(categories, many=True)

        return Response({'products': product_serializer.data, 'categories': category_serializer.data})


class ProductCategoriesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        categories = ProductCategory.objects.all()
        serializer = ProductCategorySerializer(categories, many=True)
        return Response({'categories': serializer.data})


class CategoryProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, category_id, format=None):
        category = get_object_or_404(ProductCategory, pk=category_id)
        products = Product.objects.filter(category=category)

        category_serializer = ProductCategorySerializer(category)
        product_serializer = ProductSerializer(products, many=True)

        return Response({'category': category_serializer.data, 'products': product_serializer.data})


class ProductDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id, format=None):
        product = get_object_or_404(Product, pk=product_id)

        product_serializer = ProductSerializer(product)

        return Response({'product': product_serializer.data})


class SearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        query = request.GET.get('q', '')

        if query:
            results = Product.objects.filter(name__icontains=query)
            serializer = ProductSerializer(results, many=True)
        else:
            serializer = ProductSerializer([], many=True)

        return Response({'query': query, 'results': serializer.data})


class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        return Response({'email': request.user.email})


class MyOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user).order_by('-order_date')
        serializer = OrderSerializer(orders, many=True)

        response_data = []
        for order in serializer.data:
            items = []
            order_items = OrderItem.objects.filter(order_id=order['id'])  # Filter items for the current order
            item_serializer = OrderItemSerializer(order_items, many=True)
            items = item_serializer.data

            response_data.append({
                **order,  # Incorporate order details
                'items': items,
            })

        return Response(response_data)


class AddToCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id):
        try:
            # Check if product exists
            product = Product.objects.get(pk=product_id)

            # Get the user's cart (assuming user is authenticated)
            user = request.user  # Assuming user is authenticated in request
            cart = Cart.objects.get_or_create(user=user)[0]

            # Check if product already exists in cart (optional)
            # existing_item = CartItem.objects.filter(cart=cart, product=product).first()
            # if existing_item:
            #     raise ValidationError("Product already exists in your cart.")

            # Create or update cart item (considering quantity of 1)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=product, defaults={'quantity': 1}
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            return Response({'message': 'Product added to cart successfully!'}, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({'error': 'Product does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'An error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, product_id, format=None):
        try:
            user = request.user
            cart = Cart.objects.get(user=user)  # Get user's cart

            # Check if the requested product exists in the user's cart
            cart_item = CartItem.objects.get(product_id=product_id, cart=cart)

            cart_item.delete()
            message = 'Item removed from the cart'

            return Response({'success': True, 'message': message})

        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in your cart'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id, format=None):
        cart_item = get_object_or_404(CartItem, product_id=product_id, cart__user=request.user)
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data)


class GetUserCartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # Require authentication

    def get(self, request, format=None):
        try:
            user_cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=user_cart)

            # Optimized cart data construction using select_related and prefetch_related
            cart_data = {
                'cart_items': [
                    {
                        'product': item.product.name,  # Access product name directly
                        'price': item.product.price,
                        'image': item.product.image.url,
                        'id': item.product.id,
                        'quantity': item.quantity,
                    } for item in cart_items
                ],
                'cart_total': sum(item.product.price * item.quantity for item in cart_items),  # Calculate total
            }

            return Response(cart_data)

        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckAuthenticationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        return Response({'authenticated': True})


import os
from django.conf import settings
from django.db import transaction
from reportlab.lib.units import inch
from django.shortcuts import get_object_or_404
from .models import Order, OrderItem
from .tasks import send_order_confirmation_email, send_order_cancellation_email, send_low_quantity_email
from .serializers import (OrderSerializer, OrderItemSerializer)
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate


def generate_invoice_pdf(order):
    # Define the path for saving the PDF file
    invoice_dir = os.path.join(settings.BASE_DIR, 'invoice')
    file_path = os.path.join(invoice_dir, f'{order.order_id}_invoice.pdf')

    # Generate the PDF content
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Add supermarket logo (replace 'logo.png' with the actual path to the logo)
    elements.append(Paragraph("<img src='order/logo.png' width='100' height='100'></img>", styles['Heading1']))

    # Add invoice details
    elements.append(Paragraph("<b>Invoice Details:</b>", styles['Heading1']))
    elements.append(Paragraph(f"Order ID: {order.order_id}", styles['Normal']))
    elements.append(Paragraph(f"Customer Name: {order.full_name}", styles['Normal']))
    elements.append(Paragraph(f"Order Date: {order.order_date}", styles['Normal']))

    # Retrieve seller name from related Product object
    seller_names = []
    for order_item in order.orderitem_set.all():
        seller_names.append(order_item.product.seller)
    unique_seller_names = list(set(seller_names))  # Remove duplicates
    for seller_name in unique_seller_names:
        elements.append(Paragraph(f"Seller Name: {seller_name}", styles['Normal']))
    elements.append(Paragraph("GST Number: AA2145670981BZX", styles['Normal']))

    # Add order items to the invoice
    elements.append(Paragraph("<b>Order Items:</b>", styles['Heading2']))
    data = [["Product", "Quantity", "Price", "Total"]]
    for item in order.orderitem_set.all():
        data.append([item.product.name, item.quantity, item.price, item.total_price])
    t = Table(data)
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(t)

    # Add space between sections
    elements.append(Spacer(1, inch * 0.5))  # Adjust the height as needed

    # Add order total and payment mode
    elements.append(Paragraph(f"Order Total: {order.total}", styles['Normal']))
    elements.append(Paragraph(f"Payment Mode: {order.get_payment_method_display()}", styles['Normal']))

    # Build the PDF
    doc.build(elements)

    # Write the PDF content to a file
    with open(file_path, 'wb') as pdf_file:
        pdf_file.write(buffer.getvalue())

    # Return the file path for the saved PDF
    return file_path


class PlaceOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        try:
            serializer = OrderSerializer(data=request.data)

            if serializer.is_valid():
                validated_data = serializer.validated_data

                user_cart = request.user.cart  # Assuming a relationship between User and Cart

                # Check if products in cart are available in sufficient quantity
                cart_items = user_cart.cartitem_set.all()
                for cart_item in cart_items:
                    if cart_item.quantity > cart_item.product.quantity_available:
                        return Response({'error': f'Not enough quantity available for {cart_item.product.name}'},
                                        status=status.HTTP_400_BAD_REQUEST)

                # Create the order
                order = serializer.save(user=request.user)
                user_cart.products.clear()

                # Create order items and update product quantities
                for cart_item in cart_items:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    # Update product quantity_available
                    cart_item.product.quantity_available -= cart_item.quantity
                    cart_item.product.save()

                # Calculate order total and save order
                order.calculate_total()
                order.save()

                # Send order confirmation email
                send_order_confirmation_email.delay(order.id)

                # Check if any product quantity is low and trigger an email
                for cart_item in cart_items:
                    if cart_item.product.quantity_available < 2:
                        send_low_quantity_email.delay(cart_item.product.name)

                # Generate PDF invoice
                pdf_content = generate_invoice_pdf(order)

                # Return success response with order ID and invoice PDF content
                return Response({'success': True, 'order_id': order.order_id, 'invoice_pdf': pdf_content})

            else:
                return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        try:
            user = request.user
            orders = Order.objects.filter(user=user).order_by('-order_date')  # Order by recent first

            # Consider using pagination for large datasets
            # Use rest_framework's built-in pagination for better handling

            serializer = OrderSerializer(orders, many=True)  # Serialize all orders

            return Response({'orders': serializer.data})

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id, format=None):
        order = get_object_or_404(Order, pk=order_id, user=request.user)

        if order.shipping_status == 'not_shipped':  # Check if the order status is pending
            order.shipping_status = 'cancelled'
            order.save()

            # Add the order item quantities back to product quantity_available
            for order_item in order.orderitem_set.all():  # Access order items through the reverse relationship
                product = order_item.product
                product.quantity_available += order_item.quantity
                product.save()

            # Call the Celery task to send the order cancellation email asynchronously
            send_order_cancellation_email.delay(order.id)

            return Response({'success': True, 'message': 'Order cancelled successfully.'})
        else:
            return Response({'error': 'Order cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)


class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        return Response({'email': request.user.email})


class MyOrdersView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user).order_by('-order_date')
        serializer = OrderSerializer(orders, many=True)

        response_data = []
        for order in serializer.data:
            items = []
            order_items = OrderItem.objects.filter(order_id=order['id'])  # Filter items for the current order
            item_serializer = OrderItemSerializer(order_items, many=True)
            items = item_serializer.data

            response_data.append({
                **order,  # Incorporate order details
                'items': items,
            })

        return Response(response_data)


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from .models import Payments
from .serializers import PaymentsSerializer


@receiver(post_save, sender=Order)
def update_billing_details(sender, instance, created, **kwargs):
    if created:
        # Check if there are any existing payments for the user
        existing_payments = Payments.objects.filter(user=instance.user)
        if not existing_payments.exists():
            # Create a new Payments instance with billing details from the first order
            Payments.objects.create(
                user=instance.user,
                address=instance.address,
                billing_city=instance.city,
                billing_pin_code=instance.pin_code,
                billing_state=instance.state,
                mobile=instance.mobile
            )
        return JsonResponse({'message': 'Billing details updated successfully'}, status=200)


class PaymentCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_payments = Payments.objects.filter(user=request.user)
        serializer = PaymentsSerializer(user_payments, many=True)
        return Response(serializer.data)


from .models import Shipping
from .serializers import ShippingSerializer


class ShipProductView(generics.ListAPIView):  # Change to ListAPIView for viewing
    queryset = Shipping.objects.all()
    serializer_class = ShippingSerializer
    permission_classes = [permissions.IsAuthenticated]  # Add authentication permission


@api_view(['GET'])
def get_user_details(request):
    permission_classes = [permissions.IsAuthenticated]
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)
