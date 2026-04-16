from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product


class CategoryModelTests(TestCase):

    def test_slug_auto_generated_from_name(self):
        """Category slug is auto-generated from name if not provided."""
        category = Category.objects.create(name='Football')
        self.assertEqual(category.slug, 'football')

    def test_str_returns_friendly_name_when_set(self):
        """Category __str__ returns friendly_name when it exists."""
        category = Category.objects.create(
            name='football', friendly_name='Football Gear'
        )
        self.assertEqual(str(category), 'Football Gear')

    def test_str_returns_name_when_no_friendly_name(self):
        """Category __str__ falls back to name when friendly_name is blank."""
        category = Category.objects.create(name='Tennis')
        self.assertEqual(str(category), 'Tennis')


class ProductModelTests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Test Boot',
            description='A great boot.',
            price=Decimal('29.99'),
            stock_quantity=10,
        )

    def test_slug_auto_generated_from_name(self):
        """Product slug is auto-generated from name if not provided."""
        self.assertEqual(self.product.slug, 'test-boot')

    def test_str_returns_name(self):
        """Product __str__ returns product name."""
        self.assertEqual(str(self.product), 'Test Boot')

    def test_is_in_stock_true_when_quantity_above_zero(self):
        """is_in_stock returns True when stock_quantity > 0."""
        self.assertTrue(self.product.is_in_stock)

    def test_is_in_stock_false_when_quantity_zero(self):
        """is_in_stock returns False when stock_quantity is 0."""
        self.product.stock_quantity = 0
        self.assertFalse(self.product.is_in_stock)

    def test_is_on_sale_true_when_original_price_higher(self):
        """is_on_sale returns True when original_price > price."""
        self.product.original_price = Decimal('49.99')
        self.assertTrue(self.product.is_on_sale)

    def test_discount_percentage_calculated_correctly(self):
        """discount_percentage returns correct rounded integer."""
        self.product.original_price = Decimal('40.00')
        self.product.price = Decimal('30.00')
        self.assertEqual(self.product.discount_percentage, 25)


class ProductViewTests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Test Racket',
            description='Good racket.',
            price=Decimal('19.99'),
            stock_quantity=5,
            is_active=True,
        )

    def test_product_list_returns_200(self):
        """Product listing page returns 200."""
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_returns_200(self):
        """Product detail page returns 200 for a valid slug."""
        response = self.client.get(
            reverse('products:product_detail', args=[self.product.slug])
        )
        self.assertEqual(response.status_code, 200)
