from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import (
    HomeView, ProductCategoriesView, CategoryProductsView, ProductDetailView,
    SearchView, MyProfileView, MyOrdersView, AddToCartView, UpdateCartView,
    GetCartItemView, GetUserCartView, CheckAuthenticationView,
    PlaceOrderView, OrderDetailView, CancelOrderView, PaymentCheckView, ShipProductView, get_user_details
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('product_categories/', ProductCategoriesView.as_view(), name='product_categories'),
    path('category_products/<int:category_id>/', CategoryProductsView.as_view(), name='category_products'),
    path('product_detail/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('search/', SearchView.as_view(), name='search'),
    path('my_profile/', MyProfileView.as_view(), name='my_profile'),
    path('my_orders/', MyOrdersView.as_view(), name='my_orders'),
    path('add_to_cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('update_cart/<int:product_id>/', UpdateCartView.as_view(), name='update_cart'),
    path('get_cart_item/<int:product_id>/', GetCartItemView.as_view(), name='get_cart_item'),
    path('get_user_cart/', GetUserCartView.as_view(), name='get_user_cart'),
    path('check_authentication/', CheckAuthenticationView.as_view(), name='check_authentication'),
    path('place_order/', PlaceOrderView.as_view(), name='place_order'),
    path('order_detail/', OrderDetailView.as_view(), name='order_detail'),
    path('cancel-order/<int:order_id>/', CancelOrderView.as_view(), name='cancel_order'),
    path('user_payments/', PaymentCheckView.as_view(), name='user_payments'),
    path('shipments/', ShipProductView.as_view(), name='ship_product'),
    path('user-details/', get_user_details, name='get_user_details'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

