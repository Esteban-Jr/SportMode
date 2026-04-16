from decimal import Decimal
from django.conf import settings
from products.models import Product


def bag_contents(request):
    """
    A context processor that makes bag data available across every template.

    The session bag is stored as:
        request.session['bag'] = { '<product_id>': <quantity>, ... }

    This function reads that dict, fetches the matching Product objects,
    computes per-line subtotals, and returns totals and delivery cost.
    The returned dict is merged into every template context automatically
    once this processor is registered in settings.TEMPLATES.
    """

    bag_items = []
    total = Decimal('0.00')
    product_count = 0

    bag = request.session.get('bag', {})
    stale_ids = []

    for item_id, quantity in bag.items():
        try:
            product = Product.objects.get(pk=item_id)
        except Product.DoesNotExist:
            stale_ids.append(item_id)
            continue
        subtotal = product.price * quantity
        total += subtotal
        product_count += quantity
        bag_items.append({
            'item_id': item_id,
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    # Remove any stale product IDs from the session
    if stale_ids:
        for sid in stale_ids:
            bag.pop(sid, None)
        request.session['bag'] = bag

    # Delivery logic — mirrors what is shown in templates and the delivery page
    free_delivery_threshold = Decimal(str(settings.FREE_DELIVERY_THRESHOLD))
    standard_delivery_cost = Decimal(str(settings.STANDARD_DELIVERY_COST))

    if total >= free_delivery_threshold:
        delivery = Decimal('0.00')
        free_delivery_delta = Decimal('0.00')
    else:
        delivery = standard_delivery_cost
        free_delivery_delta = free_delivery_threshold - total

    grand_total = total + delivery

    return {
        'bag_items': bag_items,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'free_delivery_delta': free_delivery_delta,
        'free_delivery_threshold': free_delivery_threshold,
        'grand_total': grand_total,
    }
