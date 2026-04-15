from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import OrderLineItem


@receiver(post_save, sender=OrderLineItem)
def recalculate_order_on_save(sender, instance, **kwargs):
    """Recalculate the parent order totals whenever a line item is saved."""
    instance.order.update_total()


@receiver(post_delete, sender=OrderLineItem)
def recalculate_order_on_delete(sender, instance, **kwargs):
    """Recalculate the parent order totals whenever a line item is deleted."""
    instance.order.update_total()
