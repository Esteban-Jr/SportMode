from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):

    def test_index_page_loads(self):
        """Homepage returns 200."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_index_uses_correct_template(self):
        """Homepage uses home/index.html."""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home/index.html')

    def test_about_page_loads(self):
        """About page returns 200."""
        response = self.client.get(reverse('about'))
        self.assertEqual(response.status_code, 200)

    def test_about_uses_correct_template(self):
        """About page uses home/about.html."""
        response = self.client.get(reverse('about'))
        self.assertTemplateUsed(response, 'home/about.html')

    def test_delivery_page_loads(self):
        """Delivery page returns 200."""
        response = self.client.get(reverse('delivery'))
        self.assertEqual(response.status_code, 200)

    def test_delivery_uses_correct_template(self):
        """Delivery page uses home/delivery.html."""
        response = self.client.get(reverse('delivery'))
        self.assertTemplateUsed(response, 'home/delivery.html')

    def test_contact_page_loads(self):
        """Contact page returns 200 on GET."""
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_uses_correct_template(self):
        """Contact page uses home/contact.html."""
        response = self.client.get(reverse('contact'))
        self.assertTemplateUsed(response, 'home/contact.html')

    def test_contact_post_valid_redirects(self):
        """Valid contact form POST redirects back to contact page."""
        response = self.client.post(reverse('contact'), {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'order',
            'message': 'This is a test message.',
        })
        self.assertRedirects(response, reverse('contact'))

    def test_contact_post_missing_fields_redirects(self):
        """Contact form POST with missing fields still redirects (with error message)."""
        response = self.client.post(reverse('contact'), {
            'name': '',
            'email': '',
            'subject': '',
            'message': '',
        })
        self.assertRedirects(response, reverse('contact'))
