from django.conf import settings
from django.db import models

from products.models import Product


class Wishlist(models.Model):
    """
    A single wishlist per registered user.
    Products are stored via a ManyToManyField so adding and removing
    items requires no extra through-table management.
    Created automatically on first add via get_or_create in the view.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist',
    )
    products = models.ManyToManyField(
        Product,
        blank=True,
        related_name='wishlisted_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}\'s wishlist'

    @property
    def item_count(self):
        return self.products.count()
