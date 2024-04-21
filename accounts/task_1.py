# accounts/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from accounts.models import CustomUser

@shared_task
def send_signup_email(user_id):
    user = CustomUser.objects.get(pk=user_id)
    subject = 'Welcome to InstaCommerce'
    
    # Render the email content from a template
    html_message = render_to_string('signup_email_template.html', {'user': user})
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    from_email = 'dacretail2024@gmail.com'
    to_email = [user.email]
    
    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

@shared_task
def send_signup_verification(user_id, verification_code):
    user = CustomUser.objects.get(pk=user_id)
    subject = 'InstaCommerce Signup Verification'

    # Render the verification email content from a template
    html_message = render_to_string('signup_verification_email_template.html', {'user': user, 'verification_code': verification_code})
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    from_email = 'dacretail2024@gmail.com'
    to_email = [user.email]

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)


@shared_task
def send_login_verification(user_id, verification_code):
    user = CustomUser.objects.get(pk=user_id)
    subject = 'InstaCommerce Login Verification'

    # Render the verification email content from a template
    html_message = render_to_string('login_verification_email_template.html', {'user': user, 'verification_code': verification_code})
    plain_message = strip_tags(html_message)  # Convert HTML to plain text

    from_email = 'dacretail2024@gmail.com'
    to_email = [user.email]

    send_mail(subject, plain_message, from_email, to_email, html_message=html_message)
