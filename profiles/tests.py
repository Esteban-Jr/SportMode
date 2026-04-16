from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123',
        )

    def test_profile_created_automatically_on_user_creation(self):
        """A UserProfile is auto-created when a User is created."""
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

    def test_profile_str_returns_username(self):
        """UserProfile __str__ includes the username."""
        profile = self.user.userprofile
        self.assertEqual(str(profile), f'{self.user.username} profile')

    def test_one_profile_per_user(self):
        """Each user has exactly one profile."""
        profile_count = UserProfile.objects.filter(user=self.user).count()
        self.assertEqual(profile_count, 1)


class ProfileViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123',
        )
        self.client.login(username='profileuser', password='testpass123')

    def test_profile_page_returns_200_when_logged_in(self):
        """Profile page returns 200 for authenticated user."""
        response = self.client.get(reverse('profiles:profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_page_redirects_when_logged_out(self):
        """Profile page redirects unauthenticated users to login."""
        self.client.logout()
        response = self.client.get(reverse('profiles:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_profile_page_uses_correct_template(self):
        """Profile page uses profiles/profile.html."""
        response = self.client.get(reverse('profiles:profile'))
        self.assertTemplateUsed(response, 'profiles/profile.html')

    def test_profile_update_saves_phone_number(self):
        """Posting to profile page saves updated delivery details."""
        self.client.post(reverse('profiles:profile'), {
            'default_full_name': 'Test Name',
            'default_phone_number': '07711223344',
            'default_street_address1': '1 Test Road',
            'default_street_address2': '',
            'default_town_or_city': 'Manchester',
            'default_county': '',
            'default_postcode': 'M1 1AA',
            'default_country': 'GB',
        })
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.default_phone_number, '07711223344')

    def test_profile_context_contains_form(self):
        """Profile page context includes the profile form."""
        response = self.client.get(reverse('profiles:profile'))
        self.assertIn('form', response.context)

    def test_profile_context_contains_orders(self):
        """Profile page context includes an orders key."""
        response = self.client.get(reverse('profiles:profile'))
        self.assertIn('orders', response.context)

    def test_order_detail_returns_404_for_nonexistent_order(self):
        """Order detail view returns 404 for a made-up order number."""
        response = self.client.get(
            reverse('profiles:order_detail', args=['DOESNOTEXIST12345678901234567890'])
        )
        self.assertEqual(response.status_code, 404)
