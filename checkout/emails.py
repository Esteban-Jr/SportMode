from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_order_confirmation(order):
    """
    Send a transactional order confirmation email to the customer.

    Called from two places:
    - checkout_success view  (form POST reached the server)
    - StripeWH_Handler       (webhook fallback — form POST never arrived)

    Because these two paths are mutually exclusive, the email is always
    sent exactly once per order.
    """
    context = {
        'order': order,
        'site_domain': settings.SITE_DOMAIN,
    }

    subject = render_to_string(
        'emails/order_confirmation_subject.txt', context
    ).strip()

    body_txt = render_to_string('emails/order_confirmation.txt', context)
    body_html = render_to_string('emails/order_confirmation.html', context)

    send_mail(
        subject=subject,
        message=body_txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.email],
        html_message=body_html,
        fail_silently=False,
    )
