from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product


def view_bag(request):
    """Render the shopping bag page."""
    return render(request, 'bag/bag.html')


def add_to_bag(request, item_id):
    """
    Add a product to the bag, or increment its quantity if already present.
    Reads `quantity` from POST and `redirect_url` to know where to send
    the user after adding (defaults to the product detail page).
    """
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity', 1))
    redirect_url = request.POST.get('redirect_url', '/')

    bag = request.session.get('bag', {})

    # Session keys are always strings after JSON serialisation
    str_id = str(item_id)

    if str_id in bag:
        bag[str_id] += quantity
        messages.success(
            request,
            f'Updated <strong>{product.name}</strong> quantity to {bag[str_id]}.'
        )
    else:
        bag[str_id] = quantity
        messages.success(
            request,
            f'Added <strong>{product.name}</strong> to your bag.'
        )

    request.session['bag'] = bag
    return redirect(redirect_url)


def update_bag(request, item_id):
    """
    Set a product's quantity to the value submitted.
    Posting quantity=0 (or less) removes the item entirely.
    """
    product = get_object_or_404(Product, pk=item_id)
    quantity = int(request.POST.get('quantity', 0))

    bag = request.session.get('bag', {})
    str_id = str(item_id)

    if quantity > 0:
        bag[str_id] = quantity
        messages.success(
            request,
            f'Updated <strong>{product.name}</strong> quantity to {quantity}.'
        )
    else:
        bag.pop(str_id, None)
        messages.success(
            request,
            f'Removed <strong>{product.name}</strong> from your bag.'
        )

    request.session['bag'] = bag
    return redirect('bag:view_bag')


def remove_from_bag(request, item_id):
    """
    Remove a product from the bag entirely, regardless of quantity.
    Uses POST for safety (avoids accidental removal via a stale GET link).
    """
    product = get_object_or_404(Product, pk=item_id)

    bag = request.session.get('bag', {})
    str_id = str(item_id)

    bag.pop(str_id, None)
    request.session['bag'] = bag

    messages.success(
        request,
        f'Removed <strong>{product.name}</strong> from your bag.'
    )
    return redirect('bag:view_bag')
