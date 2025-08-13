from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_booking_confirmation_email(to_email: str, booking_id: int):
    subject = "Test Drive Booking Confirmation"
    message = f"Your booking #{booking_id} has been received."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])


@shared_task
def send_booking_status_email(to_email: str, booking_id: int, status: str):
    subject = "Test Drive Booking Update"
    message = f"Your booking #{booking_id} status is now {status}."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])