from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """
    Top-level grouping for products (e.g. Football, Basketball).
    Kept deliberately simple — name, slug, and an optional
    description for SEO / display purposes.
    """

    name = models.CharField(max_length=100)
    # slug: URL-safe version of name, auto-populated in save().
    # Used in product filter URLs like /products/?category=football
    slug = models.SlugField(max_length=100, unique=True)
    # friendly_name: optional display label that differs from the
    # database name, e.g. name="football", friendly_name="Football"
    friendly_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.friendly_name if self.friendly_name else self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    A single product listed for sale in the store.
    """

    SPORT_CHOICES = [
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('tennis', 'Tennis'),
        ('fitness', 'Fitness'),
        ('general', 'General / Multi-sport'),
    ]

    # --- Relationships ---
    # category: the broad group this product belongs to.
    # on_delete=SET_NULL so deleting a category doesn't destroy products;
    # null/blank so a product can exist while its category is being rebuilt.
    category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='products',
    )

    # --- Identity ---
    name = models.CharField(max_length=254)
    # slug: used in SEO-friendly product detail URLs like /products/nike-football/
    slug = models.SlugField(max_length=254, unique=True, blank=True)
    # sku: optional stock-keeping unit for internal reference
    sku = models.CharField(max_length=50, blank=True)

    # --- Sport ---
    # sport: mirrors the four store categories but lives on the product
    # so a single category could contain multi-sport items if needed.
    sport = models.CharField(
        max_length=20,
        choices=SPORT_CHOICES,
        default='general',
    )

    # --- Description ---
    description = models.TextField()
    # short_description: optional one-liner used on listing cards
    short_description = models.CharField(max_length=300, blank=True)

    # --- Pricing ---
    # price: the standard selling price. DecimalField with explicit
    # max_digits and decimal_places is required for monetary values —
    # never use FloatField for money.
    price = models.DecimalField(max_digits=8, decimal_places=2)
    # original_price: optional pre-discount price, used to show a
    # "was £X" badge. Null when there is no active discount.
    original_price = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )

    # --- Media ---
    # image: the primary product photo. Stored under MEDIA_ROOT/products/.
    # blank/null so admin can save a product before uploading an image.
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    # image_url: fallback external URL if a hosted image is used instead.
    image_url = models.URLField(max_length=1024, blank=True)

    # --- Inventory ---
    # stock_quantity: units currently available. 0 means out of stock.
    stock_quantity = models.PositiveIntegerField(default=0)

    # --- Visibility ---
    # is_active: controls whether the product appears on the site.
    # Set to False to delist a product without deleting it.
    is_active = models.BooleanField(default=True)
    # is_featured: surfaces the product in homepage or promotional sections.
    is_featured = models.BooleanField(default=False)

    # --- Timestamps ---
    # auto_now_add / auto_now are set by Django automatically;
    # never pass these values manually.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_on_sale(self):
        """True when an original_price exists and is higher than the current price."""
        return self.original_price is not None and self.original_price > self.price

    @property
    def is_in_stock(self):
        """Convenience property for templates and views."""
        return self.stock_quantity > 0

    @property
    def saving(self):
        """Absolute saving in pounds (original_price - price), or None."""
        if self.is_on_sale:
            return self.original_price - self.price
        return None

    @property
    def discount_percentage(self):
        """Returns the discount as a rounded integer percentage, or None."""
        if self.is_on_sale:
            return round((self.saving / self.original_price) * 100)
        return None
