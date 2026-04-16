from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from products.models import Product


class BagViewTests(TestCase):

    def setUp(self):
        self.product = Product.objects.create(
            name='Bag Test Product',
            description='Test.',
            price=Decimal('10.00'),
            stock_quantity=20,
            is_active=True,
        )

    def test_view_bag_returns_200(self):
        """Empty bag page returns 200."""
        response = self.client.get(reverse('bag:view_bag'))
        self.assertEqual(response.status_code, 200)

    def test_view_bag_uses_correct_template(self):
        """Bag page uses bag/bag.html."""
        response = self.client.get(reverse('bag:view_bag'))
        self.assertTemplateUsed(response, 'bag/bag.html')

    def test_add_to_bag_adds_item_to_session(self):
        """Adding a product stores it in the session bag."""
        self.client.post(reverse('bag:add_to_bag', args=[self.product.pk]), {
            'quantity': 2,
            'redirect_url': '/',
        })
        bag = self.client.session.get('bag', {})
        self.assertIn(str(self.product.pk), bag)
        self.assertEqual(bag[str(self.product.pk)], 2)

    def test_add_to_bag_increments_existing_quantity(self):
        """Adding same product twice increments the quantity."""
        self.client.post(reverse('bag:add_to_bag', args=[self.product.pk]), {
            'quantity': 1,
            'redirect_url': '/',
        })
        self.client.post(reverse('bag:add_to_bag', args=[self.product.pk]), {
            'quantity': 3,
            'redirect_url': '/',
        })
        bag = self.client.session.get('bag', {})
        self.assertEqual(bag[str(self.product.pk)], 4)

    def test_update_bag_changes_quantity(self):
        """Updating bag changes the stored quantity."""
        session = self.client.session
        session['bag'] = {str(self.product.pk): 2}
        session.save()
        self.client.post(reverse('bag:update_bag', args=[self.product.pk]), {
            'quantity': 5,
        })
        bag = self.client.session.get('bag', {})
        self.assertEqual(bag[str(self.product.pk)], 5)

    def test_update_bag_with_zero_removes_item(self):
        """Updating quantity to 0 removes the item from the bag."""
        session = self.client.session
        session['bag'] = {str(self.product.pk): 3}
        session.save()
        self.client.post(reverse('bag:update_bag', args=[self.product.pk]), {
            'quantity': 0,
        })
        bag = self.client.session.get('bag', {})
        self.assertNotIn(str(self.product.pk), bag)

    def test_remove_from_bag_removes_item(self):
        """Remove view deletes item from session bag entirely."""
        session = self.client.session
        session['bag'] = {str(self.product.pk): 2}
        session.save()
        self.client.post(reverse('bag:remove_from_bag', args=[self.product.pk]))
        bag = self.client.session.get('bag', {})
        self.assertNotIn(str(self.product.pk), bag)

    def test_free_delivery_applied_above_threshold(self):
        """grand_total equals order_total when bag exceeds free delivery threshold."""
        expensive_product = Product.objects.create(
            name='Expensive Item',
            description='Pricey.',
            price=Decimal('60.00'),
            stock_quantity=5,
            is_active=True,
        )
        self.client.post(reverse('bag:add_to_bag', args=[expensive_product.pk]), {
            'quantity': 1,
            'redirect_url': '/',
        })
        response = self.client.get(reverse('bag:view_bag'))
        self.assertEqual(response.context['delivery'], Decimal('0.00'))

    def test_delivery_charge_applied_below_threshold(self):
        """Delivery charge applied when bag total is below free delivery threshold."""
        self.client.post(reverse('bag:add_to_bag', args=[self.product.pk]), {
            'quantity': 1,
            'redirect_url': '/',
        })
        response = self.client.get(reverse('bag:view_bag'))
        self.assertGreater(response.context['delivery'], Decimal('0.00'))

    def test_bag_context_product_count(self):
        """product_count in context matches total quantity added."""
        self.client.post(reverse('bag:add_to_bag', args=[self.product.pk]), {
            'quantity': 3,
            'redirect_url': '/',
        })
        response = self.client.get(reverse('bag:view_bag'))
        self.assertEqual(response.context['product_count'], 3)
