from .models import Wishlist


def wishlist_product_ids(request):
    """
    Exposes the authenticated user's wishlisted product IDs as a set
    so templates can check membership without extra DB queries.
    Returns an empty set for guests.
    """
    if not request.user.is_authenticated:
        return {'wishlist_product_ids': set()}
    try:
        ids = set(
            request.user.wishlist.products.values_list('id', flat=True)
        )
    except Wishlist.DoesNotExist:
        ids = set()
    return {'wishlist_product_ids': ids}
