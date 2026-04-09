from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    Stores a user's default delivery address and acts as the anchor
    for their order history. Created automatically via a post_save
    signal whenever a new User is saved (see signals.py).

    All delivery fields are optional so the profile can be created
    immediately on registration and filled in later at checkout or
    on the profile page.
    """

    # One-to-one link to Django's built-in User.
    # on_delete=CASCADE means the profile is deleted when the user is deleted.
    # related_name='userprofile' lets us do user.userprofile from anywhere.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile',
    )

    # --- Default delivery fields ---
    # Prefixed with "default_" to distinguish them from the live
    # order address fields that will live on the Order model.

    # Full name may differ from the User's first/last name
    # (e.g. a gift recipient) so it is stored separately.
    default_full_name = models.CharField(max_length=100, blank=True)

    default_phone_number = models.CharField(max_length=20, blank=True)

    default_street_address1 = models.CharField(max_length=80, blank=True)
    default_street_address2 = models.CharField(max_length=80, blank=True)

    default_town_or_city = models.CharField(max_length=40, blank=True)

    # County / state — not required in all countries
    default_county = models.CharField(max_length=80, blank=True)

    default_postcode = models.CharField(max_length=20, blank=True)

    # CountryField stores the ISO 3166-1 alpha-2 code (e.g. "GB")
    # and renders a select widget with all country names in forms.
    # blank_label is shown as the placeholder option.
    default_country = CountryField(
        blank_label='Select country',
        null=True,
        blank=True,
    )

    def __str__(self):
        return f'{self.user.username} profile'
