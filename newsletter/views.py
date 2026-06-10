from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import SubscriberForm
from .models import Subscriber


@require_POST
def subscribe(request):
    """
    Handle newsletter signup from any page.

    Three outcomes, each with a distinct user-facing message:

    1. New valid email  → create Subscriber, success message.
    2. Already active   → info message (no duplicate, no error shown to user).
    3. Previously unsubscribed → reactivate record, success message.
    4. Invalid email    → error message with the form validation reason.

    After handling, redirect back to the page the form was submitted from
    (HTTP_REFERER), falling back to the homepage if the header is absent.
    The redirect-after-POST pattern prevents duplicate submissions on refresh.
    """
    redirect_url = request.META.get('HTTP_REFERER', '/')
    form = SubscriberForm(request.POST)

    if form.is_valid():
        email = form.cleaned_data['email']

        try:
            subscriber = Subscriber.objects.get(email__iexact=email)
            # Record exists — check active status
            if subscriber.is_active:
                messages.info(
                    request,
                    f'{email} is already subscribed to our newsletter.'
                )
            else:
                # Reactivate a previously unsubscribed address
                subscriber.is_active = True
                subscriber.save()
                messages.success(
                    request,
                    "Welcome back! You've been re-subscribed to the SportMode newsletter."
                )

        except Subscriber.DoesNotExist:
            # Brand new subscriber
            Subscriber.objects.create(email=email)
            messages.success(
                request,
                "You're subscribed! Thanks for joining the SportMode newsletter."
            )

    else:
        # Form invalid (e.g. malformed email)
        email_errors = form.errors.get('email', [])
        error_text = email_errors[0] if email_errors else 'Please enter a valid email address.'
        messages.error(request, error_text)

    return redirect(redirect_url)


def unsubscribe(request):
    """
    GET  → show confirmation form, pre-populated with ?email= param if present.
    POST → mark the subscriber inactive (soft delete) and confirm to the user.

    No login required so links in emails work for anyone.
    """
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        if email:
            try:
                subscriber = Subscriber.objects.get(email__iexact=email)
                if subscriber.is_active:
                    subscriber.is_active = False
                    subscriber.save()
                    messages.success(
                        request,
                        f'{email} has been unsubscribed. '
                        'You will no longer receive emails from us.'
                    )
                else:
                    messages.info(
                        request,
                        f'{email} is not currently subscribed.'
                    )
            except Subscriber.DoesNotExist:
                messages.info(
                    request,
                    "We couldn't find that email address in our list."
                )
        else:
            messages.error(request, 'Please enter your email address.')
        return redirect('newsletter:unsubscribe')

    prefill_email = request.GET.get('email', '')
    return render(request, 'newsletter/unsubscribe.html', {'prefill_email': prefill_email})
