from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product
from profiles.models import UserProfile
from .models import Order, OrderLineItem


class OrderModelTests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Checkout Test Product',
            description='Test.',
            price=Decimal('20.00'),
            stock_quantity=10,
        )
        self.order = Order.objects.create(
            full_name='Test User',
            email='test@example.com',
            phone_number='07700000000',
            street_address1='1 Test Street',
            town_or_city='London',
            country='GB',
        )

    def test_order_number_auto_generated(self):
        """Order number is generated on first save."""
        self.assertTrue(len(self.order.order_number) == 32)

    def test_order_str_returns_order_number(self):
        """Order __str__ returns the order number."""
        self.assertEqual(str(self.order), self.order.order_number)

    def test_lineitem_total_calculated_on_save(self):
        """LineItem total is price × quantity on save."""
        item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=3,
        )
        self.assertEqual(item.lineitem_total, Decimal('60.00'))

    def test_update_total_sets_order_total(self):
        """update_total correctly sets order_total from line items."""
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_total, Decimal('40.00'))

    def test_update_total_sets_grand_total(self):
        """grand_total equals order_total plus delivery cost."""
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
        )
        self.order.refresh_from_db()
        self.assertEqual(
            self.order.grand_total,
            self.order.order_total + self.order.delivery_cost
        )

    def test_free_delivery_applied_above_threshold(self):
        """Delivery cost is zero when order total meets the free delivery threshold."""
        expensive = Product.objects.create(
            name='Expensive Product',
            description='Pricey.',
            price=Decimal('60.00'),
            stock_quantity=5,
        )
        OrderLineItem.objects.create(
            order=self.order,
            product=expensive,
            quantity=1,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.delivery_cost, Decimal('0.00'))

    def test_delivery_charged_below_threshold(self):
        """Delivery cost is non-zero when order total is below threshold."""
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
        )
        self.order.refresh_from_db()
        self.assertGreater(self.order.delivery_cost, Decimal('0.00'))

    def test_signal_recalculates_on_lineitem_save(self):
        """Signal triggers update_total automatically when line item is saved."""
        OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=4,
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_total, Decimal('80.00'))

    def test_signal_recalculates_on_lineitem_delete(self):
        """Signal triggers update_total when a line item is deleted."""
        item = OrderLineItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
        )
        item.delete()
        self.order.refresh_from_db()
        self.assertEqual(self.order.order_total, Decimal('0.00'))

    def test_order_number_not_regenerated_on_resave(self):
        """Order number remains the same after a subsequent save."""
        original_number = self.order.order_number
        self.order.save()
        self.assertEqual(self.order.order_number, original_number)
