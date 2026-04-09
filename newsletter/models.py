from django.db import models
from django.utils import timezone


class Subscriber(models.Model):
    """
    A single newsletter subscriber.

    Duplicate prevention: email is unique=True so the database enforces
    one record per address at the constraint level, regardless of case.
    The form view also checks for existing subscribers before saving and
    returns a clear message rather than letting the IntegrityError bubble up.

    is_active allows soft-unsubscription — the email is retained for
    audit purposes but the subscriber receives no further mailings.
    """

    # unique=True enforces one row per address at the DB level
    email = models.EmailField(unique=True)

    # Stored so you can report "joined on X" and sort your list
    date_subscribed = models.DateTimeField(default=timezone.now)

    # Soft delete — set False to unsubscribe without losing the record
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_subscribed']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'

    def __str__(self):
        return self.email
