from functools import wraps

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProductForm
from .models import Category, Product


# ---------------------------------------------------------------------------
# Access control
# ---------------------------------------------------------------------------

def staff_required(view_func):
    """
    Decorator that restricts a view to staff and superusers.
    Unauthenticated users are redirected to the login page.
    Authenticated non-staff users receive a 403 Forbidden response.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not (request.user.is_staff or request.user.is_superuser):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# Public views
# ---------------------------------------------------------------------------

def product_list(request):
    """
    Displays all active products.
    Supports filtering by category slug, sport, and a search query,
    plus sorting by price or name. All filters are combinable.
    """
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()

    # -- Active filter state (read from GET params) --
    selected_category = None
    selected_sport = None
    search_query = ''
    sort_by = request.GET.get('sort', 'name')

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    # Sport filter
    sport = request.GET.get('sport')
    if sport:
        selected_sport = sport
        products = products.filter(sport=sport)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        search_query = q
        products = products.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(short_description__icontains=q)
        )

    # Sorting
    sort_options = {
        'name':       ('name', 'Name (A–Z)'),
        'name_desc':  ('-name', 'Name (Z–A)'),
        'price_asc':  ('price', 'Price (Low–High)'),
        'price_desc': ('-price', 'Price (High–Low)'),
        'newest':     ('-created_at', 'Newest First'),
    }
    sort_field, sort_label = sort_options.get(sort_by, sort_options['name'])
    products = products.order_by(sort_field)

    context = {
        'products': products,
        'categories': categories,
        'sport_choices': Product.SPORT_CHOICES,
        'selected_category': selected_category,
        'selected_sport': selected_sport,
        'search_query': search_query,
        'sort_by': sort_by,
        'sort_label': sort_label,
        'sort_options': sort_options,
        'product_count': products.count(),
    }
    return render(request, 'products/products.html', context)


def product_detail(request, slug):
    """
    Displays a single product. Shows related products from the
    same category (excluding the current product), capped at 4.
    """
    product = get_object_or_404(Product, slug=slug, is_active=True)

    related_products = []
    if product.category:
        related_products = (
            Product.objects
            .filter(category=product.category, is_active=True)
            .exclude(pk=product.pk)[:4]
        )

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/product_detail.html', context)


# ---------------------------------------------------------------------------
# Staff-only CRUD views
# ---------------------------------------------------------------------------

@staff_required
def add_product(request):
    """Staff/superuser: add a new product via a ModelForm."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'"{product.name}" was added successfully.')
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


@staff_required
def edit_product(request, slug):
    """Staff/superuser: edit an existing product via a pre-filled ModelForm."""
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'"{product.name}" was updated successfully.')
            return redirect('products:product_detail', slug=product.slug)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {'form': form, 'product': product})


@staff_required
def delete_product(request, slug):
    """
    Staff/superuser: confirm and delete a product.
    GET  → confirmation page.
    POST → delete and redirect to product list.
    """
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'"{name}" was deleted.')
        return redirect('products:product_list')

    return render(request, 'products/confirm_delete_product.html', {'product': product})
