from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User, CustomerProfile


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance: User, created: bool, **kwargs):
    if not created:
        return
    if instance.role == User.Roles.CUSTOMER:
        CustomerProfile.objects.get_or_create(user=instance)