import json
import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from bag.contexts import bag_contents
from products.models import Product
from profiles.models import UserProfile
from .emails import send_order_confirmation
from .forms import OrderForm
from .models import Order, OrderLineItem


# ---------------------------------------------------------------------------
# Helper view — called by Stripe.js before card confirmation
# ---------------------------------------------------------------------------

@require_POST
def cache_checkout_data(request):
    """
    Stripe.js calls this endpoint before it calls stripe.confirmCardPayment().

    We attach the bag snapshot and username to the PaymentIntent's metadata
    so that the webhook handler can recreate the order even if the browser
    closes before the POST form ever reaches the server.
    """
    try:
        # The client_secret is "pi_xxx_secret_yyy" — the PID is the first part
        pid = request.POST.get('client_secret').split('_secret')[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(pid, metadata={
            'bag': json.dumps(request.session.get('bag', {})),
            'save_info': request.POST.get('save_info'),
            'username': request.user.username if request.user.is_authenticated else 'AnonymousUser',
        })
        return HttpResponse(status=200)
    except Exception as e:
        messages.error(request, 'Sorry, your payment cannot be processed right now. Please try again later.')
        return HttpResponse(content=str(e), status=400)


# ---------------------------------------------------------------------------
# Main checkout view
# ---------------------------------------------------------------------------

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. Check your environment variables.')

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, 'Your bag is empty.')
        return redirect(reverse('products:product_list'))

    current_bag = bag_contents(request)
    total = current_bag['grand_total']
    # Stripe requires the amount in the smallest currency unit (pence)
    stripe_total = round(total * 100)

    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    # Pre-fill the form from the user's saved profile if logged in
    if request.method == 'POST':
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST['street_address2'],
            'town_or_city': request.POST['town_or_city'],
            'county': request.POST['county'],
            'postcode': request.POST['postcode'],
            'country': request.POST['country'],
        }
        order_form = OrderForm(form_data)

        if order_form.is_valid():
            # commit=False so we can attach Stripe data before saving
            order = order_form.save(commit=False)
            pid = request.POST.get('client_secret').split('_secret')[0]
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            order.save()

            # Create a line item for each product in the bag
            for item_id, quantity in bag.items():
                try:
                    product = Product.objects.get(pk=item_id)
                    line_item = OrderLineItem(
                        order=order,
                        product=product,
                        quantity=quantity,
                    )
                    line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        'One of the products in your bag was not found. '
                        'Please contact us for assistance.'
                    )
                    order.delete()
                    return redirect(reverse('bag:view_bag'))

            # Attach to user profile if logged in
            if request.user.is_authenticated:
                profile = request.user.userprofile
                order.user_profile = profile
                order.save()

                # Save delivery info back to profile if requested.
                # Order fields that are null=True (street_address2, county,
                # postcode) can be None when the user left them blank.
                # UserProfile CharField columns are NOT NULL — they store ''
                # for empty. The `or ''` coercion prevents the IntegrityError
                # that would otherwise fire when None is written to a NOT NULL
                # column.
                if request.POST.get('save_info'):
                    profile.default_full_name = order.full_name
                    profile.default_phone_number = order.phone_number
                    profile.default_street_address1 = order.street_address1
                    profile.default_street_address2 = order.street_address2 or ''
                    profile.default_town_or_city = order.town_or_city
                    profile.default_county = order.county or ''
                    profile.default_postcode = order.postcode or ''
                    profile.default_country = order.country
                    profile.save()

            return redirect(
                reverse('checkout:checkout_success', args=[order.order_number])
            )
        else:
            messages.error(
                request,
                'There was an error with your form. Please check your details.'
            )

    else:
        # GET — pre-fill from profile if authenticated
        initial = {}
        if request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                initial = {
                    'full_name': profile.default_full_name,
                    'email': request.user.email,
                    'phone_number': profile.default_phone_number,
                    'street_address1': profile.default_street_address1,
                    'street_address2': profile.default_street_address2,
                    'town_or_city': profile.default_town_or_city,
                    'county': profile.default_county,
                    'postcode': profile.default_postcode,
                    'country': profile.default_country,
                }
            except UserProfile.DoesNotExist:
                pass
        order_form = OrderForm(initial=initial)

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret,
    }
    return render(request, 'checkout/checkout.html', context)


# ---------------------------------------------------------------------------
# Success view
# ---------------------------------------------------------------------------

def checkout_success(request, order_number):
    """
    Shown after a successful payment. Clears the session bag and
    attaches the order to the user's profile (handled in checkout view,
    confirmed here). Displays full order details and a confirmation message.
    """
    order = get_object_or_404(Order, order_number=order_number)

    # Clear the bag from the session
    if 'bag' in request.session:
        del request.session['bag']

    send_order_confirmation(order)

    context = {'order': order}
    return render(request, 'checkout/checkout_success.html', context)
