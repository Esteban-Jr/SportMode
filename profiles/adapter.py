from django.conf import settings
from django.urls import reverse
from allauth.account.adapter import DefaultAccountAdapter


class SportModeAccountAdapter(DefaultAccountAdapter):
    """
    Custom allauth adapter for SportMode.

    Overrides get_login_redirect_url so that staff members and
    superusers land on the Django admin panel after login, while
    regular users are sent to their profile page.

    How this fits into allauth's login flow:
    1. User submits login credentials.
    2. allauth validates and authenticates the user.
    3. allauth calls adapter.get_login_redirect_url(request) to decide
       where to redirect — unless a ?next= parameter was present, which
       always takes priority (allauth handles this before calling this method).
    4. Django redirects to the returned URL.

    Nothing else in the authentication system is changed.
    """

    def get_login_redirect_url(self, request):
        user = request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return reverse('admin:index')
        return settings.LOGIN_REDIRECT_URL
