from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
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

    for item_id, quantity in bag.items():
        product = get_object_or_404(Product, pk=item_id)
        subtotal = product.price * quantity
        total += subtotal
        product_count += quantity
        bag_items.append({
            'item_id': item_id,
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

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
