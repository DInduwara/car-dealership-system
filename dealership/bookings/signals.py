from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import TestDrive
from .tasks import send_booking_confirmation_email, send_booking_status_email

User = get_user_model()


@receiver(post_save, sender=TestDrive)
def booking_created(sender, instance: TestDrive, created: bool, **kwargs):
    if created and instance.customer and instance.customer.email:
        send_booking_confirmation_email.delay(instance.customer.email, instance.id)


@receiver(pre_save, sender=TestDrive)
def booking_status_changed(sender, instance: TestDrive, **kwargs):
    if not instance.pk:
        return
    try:
        previous = TestDrive.objects.get(pk=instance.pk)
    except TestDrive.DoesNotExist:
        return
    if previous.status != instance.status and instance.customer and instance.customer.email:
        send_booking_status_email.delay(instance.customer.email, instance.id, instance.status)