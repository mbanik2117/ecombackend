# config/beat_schedule.py

from datetime import timedelta
from celery import shared_task
from django.apps import apps
from celery import Celery
from store.models import CartItem
# Make sure to set the default Django settings module for the 'celery' program.
from django.conf import settings

# This line is necessary to use Django models in the Celery tasks.
settings.configure()

from accounts.task_1 import send_signup_email, send_signup_verification, send_login_verification
from store.tasks import send_order_confirmation_email, send_order_cancellation_email, send_low_quantity_email


def get_dynamic_order_id():
    Order = apps.get_model('store', 'Order')
    latest_order = Order.objects.latest('created_at')
    return latest_order.id if latest_order else None


@shared_task
def schedule_send_signup_verification(user_id, verification_code):
    send_signup_verification.apply_async(args=[user_id, verification_code], countdown=5)  # Adjust countdown as needed


@shared_task
def schedule_send_signup_email(user_id):
    send_signup_email.apply_async(args=[user_id], countdown=5)  # Adjust countdown as needed


@shared_task
def schedule_send_login_verification(user_id, verification_code):
    send_login_verification.apply_async(args=[user_id, verification_code], countdown=5)


@shared_task
def schedule_send_order_confirmation_email():
    order_id = get_dynamic_order_id()
    send_order_confirmation_email.apply_async(args=[order_id], countdown=5)  # Adjust countdown as needed


@shared_task
def schedule_send_order_cancellation_email():
    order_id = get_dynamic_order_id()
    send_order_cancellation_email.apply_async(args=[order_id], countdown=5)


@shared_task
def schedule_send_low_quantity_email():
    product_name = CartItem.product.name
    send_low_quantity_email.apply_async(args=[product_name], countdown=5)


CELERY_BEAT_SCHEDULE = {
    'schedule-send-signup-verification': {
        'task': 'config.beat_schedule.schedule_send_signup_verification',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },
    'schedule-send-signup-email': {
        'task': 'config.beat_schedule.schedule_send_signup_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },

    'schedule-send-login-verification': {
        'task': 'config.beat_schedule.schedule_send_login_verification',
        'schedule': timedelta(minutes=1),
        'options': {'expires': 60},
    },
    'schedule-send-order-confirmation-email': {
        'task': 'config.beat_schedule.schedule_send_order_confirmation_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },
    'schedule-send-order-cancellation-email': {
        'task': 'config.beat_schedule.schedule_send_order_cancellation_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },
    'schedule-send-low-quantity-email': {
        'task': 'config.beat_schedule.schedule_send_low_quantity_email',
        'schedule': timedelta(minutes=1),  # Adjust the schedule as needed
        'options': {'expires': 60},  # Adjust the expiration time as needed
    },

}
