from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Order


class OrderForm(forms.ModelForm):
    """
    The delivery and contact form shown on the checkout page.
    Payment is handled entirely by Stripe Elements — no card fields here.
    """

    class Meta:
        model = Order
        fields = (
            'full_name', 'email', 'phone_number',
            'street_address1', 'street_address2',
            'town_or_city', 'county', 'postcode', 'country',
        )
        widgets = {
            'country': CountrySelectWidget(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'street_address1': 'Street Address 1',
            'street_address2': 'Street Address 2',
            'town_or_city': 'Town or City',
            'county': 'County, State or Locality',
            'postcode': 'Postcode',
        }

        self.fields['full_name'].widget.attrs['autofocus'] = True

        for field_name, field in self.fields.items():
            if field_name == 'country':
                pass  # CountrySelectWidget manages its own attrs
            else:
                required_marker = ' *' if field.required else ''
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = (
                    placeholders.get(field_name, '') + required_marker
                )
            field.label = False
