from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import UserProfile


class UserProfileForm(forms.ModelForm):
    """
    Lets a logged-in user update their default delivery information.
    The `user` OneToOneField is excluded — it is set automatically
    and should never be editable by the user themselves.
    """

    class Meta:
        model = UserProfile
        exclude = ('user',)
        widgets = {
            'default_country': CountrySelectWidget(
                attrs={'class': 'form-select'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'default_full_name': 'Full Name',
            'default_phone_number': 'Phone Number',
            'default_street_address1': 'Street Address 1',
            'default_street_address2': 'Street Address 2',
            'default_town_or_city': 'Town or City',
            'default_county': 'County, State or Locality',
            'default_postcode': 'Postcode',
        }

        for field_name, field in self.fields.items():
            # Apply Bootstrap classes to every field
            if field_name == 'default_country':
                # CountrySelectWidget handles its own attrs above
                pass
            else:
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = placeholders.get(field_name, '')

            # Remove the auto-generated label — placeholders carry the UX
            field.label = False
