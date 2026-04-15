from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_welcome_email(user):
    """
    Send a welcome email to a newly registered user.

    Triggered by the allauth user_signed_up signal in profiles/signals.py,
    which fires exactly once when a new account is confirmed — never on
    subsequent logins or profile updates.
    """
    context = {
        'user': user,
        'site_domain': settings.SITE_DOMAIN,
    }

    subject = render_to_string(
        'emails/welcome_subject.txt', context
    ).strip()

    body_txt = render_to_string('emails/welcome.txt', context)
    body_html = render_to_string('emails/welcome.html', context)

    send_mail(
        subject=subject,
        message=body_txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=body_html,
        fail_silently=False,
    )
