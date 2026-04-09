import json
import time
import stripe

from django.conf import settings
from django.http import HttpResponse

from products.models import Product
from profiles.models import UserProfile
from .models import Order, OrderLineItem


class StripeWH_Handler:
    """
    Handles Stripe webhooks.

    Each method corresponds to one Stripe event type. The webhook view
    dispatches to the right method based on event.type. Unhandled event
    types fall through to handle_event().

    Why webhooks matter:
    The checkout view creates the order when the POST form is submitted.
    But if the browser crashes, the network drops, or the user closes the
    tab after Stripe confirms payment but before the redirect lands, the
    form POST never reaches the server. The webhook fires directly from
    Stripe regardless — so payment_intent.succeeded is the fallback that
    guarantees the order is always recorded.
    """

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """Handle any unrecognised or unhandled webhook event."""
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200,
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle payment_intent.succeeded.

        1. Check whether the order already exists (form POST got through).
        2. If yes, optionally save delivery info to the profile and return 200.
        3. If no, create the order from the metadata attached in
           cache_checkout_data and return 200.
        """
        intent = event.data.object
        pid = intent.id
        bag = json.loads(intent.metadata.get('bag', '{}'))
        save_info = intent.metadata.get('save_info')
        username = intent.metadata.get('username', 'AnonymousUser')

        # Retrieve the charge to get billing details
        stripe.api_key = settings.STRIPE_SECRET_KEY
        charge = stripe.Charge.retrieve(intent.latest_charge)
        billing_details = charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(charge.amount / 100, 2)

        # Normalise empty strings in shipping details to None
        if shipping_details:
            for field, value in shipping_details.address.items():
                if value == '':
                    shipping_details.address[field] = None

        # --- Attach order to profile if user was logged in ---
        profile = None
        if username != 'AnonymousUser':
            try:
                profile = UserProfile.objects.get(user__username=username)
                if save_info == 'true' and shipping_details:
                    addr = shipping_details.address
                    profile.default_phone_number = shipping_details.phone
                    profile.default_street_address1 = addr.line1
                    profile.default_street_address2 = addr.line2
                    profile.default_town_or_city = addr.city
                    profile.default_county = addr.state
                    profile.default_postcode = addr.postal_code
                    profile.default_country = addr.country
                    profile.save()
            except UserProfile.DoesNotExist:
                pass

        # --- Check whether the order already exists ---
        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(stripe_pid=pid)
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | Order already in database',
                status=200,
            )

        # --- Order not found — create it from webhook metadata ---
        order = None
        try:
            addr = shipping_details.address if shipping_details else {}
            order = Order.objects.create(
                full_name=shipping_details.name if shipping_details else billing_details.name,
                user_profile=profile,
                email=billing_details.email,
                phone_number=shipping_details.phone if shipping_details else billing_details.phone,
                street_address1=addr.get('line1', ''),
                street_address2=addr.get('line2', ''),
                town_or_city=addr.get('city', ''),
                county=addr.get('state', ''),
                postcode=addr.get('postal_code', ''),
                country=addr.get('country', ''),
                original_bag=json.dumps(bag),
                stripe_pid=pid,
            )
            for item_id, quantity in bag.items():
                product = Product.objects.get(pk=item_id)
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )
        except Exception as e:
            if order:
                order.delete()
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500,
            )

        return HttpResponse(
            content=f'Webhook received: {event["type"]} | Order created by webhook',
            status=200,
        )

    def handle_payment_intent_payment_failed(self, event):
        """Handle payment_intent.payment_failed — log only, no action needed."""
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200,
        )
