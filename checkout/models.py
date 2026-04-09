import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models
from django_countries.fields import CountryField

from products.models import Product
from profiles.models import UserProfile


class Order(models.Model):
    """
    A single completed (or in-progress) customer order.

    Design decisions:
    - All delivery address fields are copied from the bag/profile at the
      moment of purchase. This is a snapshot — if the user later changes
      their profile the historical order address is preserved.
    - stripe_pid stores the Stripe PaymentIntent ID. It is used by the
      webhook handler to match an incoming payment_intent.succeeded event
      to the correct order, which prevents duplicate order creation if the
      form submission and the webhook both fire.
    - original_bag stores the session bag as a JSON string for the same
      reason — so the webhook can recreate the order from scratch if the
      form submission never reached the server.
    """

    # --- Order reference ---
    order_number = models.CharField(max_length=32, null=False, editable=False)

    # --- Linked profile (optional — supports guest checkout) ---
    # SET_NULL keeps historical orders alive even if a user deletes their
    # account. null + blank = True means the field is optional.
    user_profile = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    # --- Contact ---
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)

    # --- Delivery address snapshot ---
    street_address1 = models.CharField(max_length=80, null=False, blank=False)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40, null=False, blank=False)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20, null=True, blank=True)
    country = CountryField(blank_label='Select country', null=False, blank=False)

    # --- Timestamps ---
    date = models.DateTimeField(auto_now_add=True)

    # --- Financials ---
    # Stored on the order so historical totals don't shift if settings change.
    delivery_cost = models.DecimalField(max_digits=6, decimal_places=2,
                                        null=False, default=0)
    order_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2,
                                      null=False, default=0)

    # --- Stripe / idempotency ---
    # JSON snapshot of request.session['bag'] at the moment of checkout.
    # Used by the webhook to rebuild the order if the POST never arrived.
    original_bag = models.TextField(null=False, blank=False, default='')
    # Stripe PaymentIntent ID — unique per payment attempt.
    stripe_pid = models.CharField(max_length=254, null=False, blank=False,
                                  default='')

    class Meta:
        ordering = ['-date']

    def _generate_order_number(self):
        """Return a random, unique 32-character uppercase hex string."""
        return uuid.uuid4().hex.upper()

    def update_total(self):
        """
        Recalculate order_total, delivery_cost, and grand_total from
        the current set of line items.

        Called automatically by OrderLineItem.save() and .delete() via
        signals so the order totals are always in sync.
        """
        self.order_total = (
            self.lineitems.aggregate(
                total=models.Sum('lineitem_total')
            )['total'] or Decimal('0.00')
        )
        threshold = Decimal(str(settings.FREE_DELIVERY_THRESHOLD))
        cost = Decimal(str(settings.STANDARD_DELIVERY_COST))

        self.delivery_cost = (
            Decimal('0.00') if self.order_total >= threshold else cost
        )
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        # Generate an order number on first save only.
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    """
    One line of an Order — a single Product at a given quantity.

    lineitem_total is computed and stored (not a @property) so that
    historical order values are preserved even if a product's price
    changes after the order was placed.
    """

    order = models.ForeignKey(
        Order,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        related_name='lineitems',
    )
    product = models.ForeignKey(
        Product,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    quantity = models.IntegerField(null=False, blank=False, default=0)
    # Snapshot of price × quantity at the time of purchase.
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2,
                                         null=False, blank=False,
                                         editable=False)

    def save(self, *args, **kwargs):
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'SKU {self.product.sku or self.product.pk} '
            f'on order {self.order.order_number}'
        )
