from django.test import TestCase
from django.urls import reverse
from .models import Subscriber


class SubscriberModelTests(TestCase):

    def test_str_returns_email(self):
        """Subscriber __str__ returns the email address."""
        subscriber = Subscriber.objects.create(email='hello@example.com')
        self.assertEqual(str(subscriber), 'hello@example.com')

    def test_subscriber_is_active_by_default(self):
        """New subscribers are active by default."""
        subscriber = Subscriber.objects.create(email='active@example.com')
        self.assertTrue(subscriber.is_active)

    def test_email_is_unique(self):
        """Database enforces unique email constraint."""
        Subscriber.objects.create(email='unique@example.com')
        with self.assertRaises(Exception):
            Subscriber.objects.create(email='unique@example.com')


class SubscribeViewTests(TestCase):

    def test_subscribe_new_email_creates_subscriber(self):
        """Posting a new email creates a Subscriber record."""
        self.client.post(
            reverse('newsletter:subscribe'),
            {'email': 'new@example.com'},
            HTTP_REFERER='/',
        )
        self.assertTrue(Subscriber.objects.filter(email='new@example.com').exists())

    def test_subscribe_duplicate_active_does_not_create_duplicate(self):
        """Subscribing with an already-active email does not create a second record."""
        Subscriber.objects.create(email='existing@example.com', is_active=True)
        self.client.post(
            reverse('newsletter:subscribe'),
            {'email': 'existing@example.com'},
            HTTP_REFERER='/',
        )
        count = Subscriber.objects.filter(email='existing@example.com').count()
        self.assertEqual(count, 1)

    def test_subscribe_reactivates_inactive_subscriber(self):
        """Subscribing with a previously unsubscribed email reactivates them."""
        subscriber = Subscriber.objects.create(email='inactive@example.com', is_active=False)
        self.client.post(
            reverse('newsletter:subscribe'),
            {'email': 'inactive@example.com'},
            HTTP_REFERER='/',
        )
        subscriber.refresh_from_db()
        self.assertTrue(subscriber.is_active)

    def test_subscribe_invalid_email_does_not_create_subscriber(self):
        """Posting an invalid email does not create a subscriber."""
        self.client.post(
            reverse('newsletter:subscribe'),
            {'email': 'not-an-email'},
            HTTP_REFERER='/',
        )
        self.assertFalse(Subscriber.objects.filter(email='not-an-email').exists())

    def test_subscribe_redirects_to_referer(self):
        """Subscribe view redirects back to the HTTP_REFERER."""
        response = self.client.post(
            reverse('newsletter:subscribe'),
            {'email': 'redirect@example.com'},
            HTTP_REFERER='/products/',
        )
        self.assertRedirects(
            response, '/products/', fetch_redirect_response=False
        )

    def test_subscribe_redirects_to_home_when_no_referer(self):
        """Subscribe view redirects to / when no HTTP_REFERER is present."""
        response = self.client.post(
            reverse('newsletter:subscribe'),
            {'email': 'noref@example.com'},
        )
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_subscribe_get_not_allowed(self):
        """GET request to subscribe view returns 405 Method Not Allowed."""
        response = self.client.get(reverse('newsletter:subscribe'))
        self.assertEqual(response.status_code, 405)
