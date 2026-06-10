from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from products.models import Product
from .models import Wishlist


@login_required
def wishlist_detail(request):
    """Displays all products saved to the current user's wishlist."""
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    products = wishlist.products.filter(is_active=True)
    return render(request, 'wishlist/wishlist.html', {
        'wishlist': wishlist,
        'products': products,
    })


@login_required
@require_POST
def add_to_wishlist(request, product_id):
    """
    Adds a product to the user's wishlist.
    Creates the wishlist record if it does not yet exist.
    Redirects back to the referring page (typically product detail).
    """
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)

    if wishlist.products.filter(pk=product.pk).exists():
        messages.info(request, f'"{product.name}" is already in your wishlist.')
    else:
        wishlist.products.add(product)
        messages.success(
            request,
            f'"{product.name}" has been added to your wishlist. '
            f'<a href="/wishlist/" class="alert-link">View wishlist</a>.'
        )

    redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER', '/')
    return redirect(redirect_url)


@login_required
@require_POST
def remove_from_wishlist(request, product_id):
    """
    Removes a product from the user's wishlist.
    Redirects back to the referring page.
    """
    product = get_object_or_404(Product, pk=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    wishlist.products.remove(product)
    messages.success(request, f'"{product.name}" has been removed from your wishlist.')

    redirect_url = request.POST.get('redirect_url') or request.META.get('HTTP_REFERER', '/')
    return redirect(redirect_url)
