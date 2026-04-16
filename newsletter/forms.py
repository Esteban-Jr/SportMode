from django import forms
from .models import Subscriber


class SubscriberForm(forms.ModelForm):
    """
    A single-field form that collects an email address.

    Validation is intentionally minimal — Django's EmailField handles
    format checking. Duplicate detection is done in the view so the
    message can be tailored (rather than showing a raw form error
    that exposes whether an address is in the database).
    """

    class Meta:
        model = Subscriber
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your email address',
                'aria-label': 'Email address for newsletter',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = False

    def validate_unique(self):
        # Uniqueness is intentionally handled in the view so we can
        # return tailored messages (already subscribed / reactivated)
        # instead of a raw form error that would bypass that logic.
        pass
