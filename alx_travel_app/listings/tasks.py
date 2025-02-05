from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment

@shared_task
def send_payment_confirmation_email(payment_id):
    payment = Payment.objects.get(id=payment_id)
    subject = "Payment Confirmation"
    message = f"Dear {payment.user.first_name},\n\nYour payment of {payment.amount} ETB was successful!"
    recipient_list = [payment.user.email]

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
