# store/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.apps import apps  # Import necessary modules, no need for login_required here
from django.core.exceptions import ObjectDoesNotExist

from ecom import settings
from ecom.celery import app
from .models import Order


@shared_task
def send_order_confirmation_email(order_id):
    order = Order.objects.get(pk=order_id)

    subject = 'Order Confirmation'

    # Construct the email message using a template
    html_message = render_to_string('order_confirmation_email.html', {'order': order})

    # Use the strip_tags function to convert HTML to plain text for the email body
    plain_message = strip_tags(html_message)

    from_email = 'dacretail2024@gmail.com'  # Replace with your email address
    to_email = [order.email]
    print(f"Sending order confirmation email for order ID: {order_id}")
    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)


@shared_task
def send_order_cancellation_email(order_id):
    try:
        order = Order.objects.get(pk=order_id)
    except ObjectDoesNotExist:
        print(f"Order with ID {order_id} does not exist.")
        return

    subject = 'Order Cancellation'

    # Construct the email message using a template
    html_message = render_to_string('order_cancellation_email.html', {'order': order})

    # Use the strip_tags function to convert HTML to plain text for the email body
    plain_message = strip_tags(html_message)

    from_email = 'dacretail2024@gmail.com'  # Replace with your email address
    to_email = [order.email]
    print(f"Sending order cancellation email for order ID: {order_id}")
    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)


@shared_task
def send_low_quantity_email(product_name):
    subject = 'Low Quantity Alert'

    # Construct the email message using a template
    html_message = render_to_string('low_quantity_email.html', {'product_name': product_name})

    # Use the strip_tags function to convert HTML to plain text for the email body
    plain_message = strip_tags(html_message)

    from_email = 'dacretail2024@gmail.com' # Replace with your email address
    admin_email = settings.ADMIN_EMAIL  # Replace with your admin or superuser email
    to_email = [admin_email]
    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

    print(f"Sending low quantity alert email for product: {product_name}")