from allauth.account.signals import user_signed_up
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .emails import send_welcome_email
from .models import UserProfile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Listen for User saves.

    - On first save (created=True): create a blank UserProfile so
      every User always has a profile from the moment of registration.
    - On subsequent saves (e.g. password change, email update):
      save the existing profile to keep it in sync. This is a no-op
      unless something on the profile itself depends on the user record.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()


@receiver(user_signed_up)
def on_user_signed_up(request, user, **kwargs):
    """
    Send a welcome email when a new account is created via allauth.

    allauth's user_signed_up fires exactly once per registration —
    never on login, password change, or any other User save — so
    there is no risk of duplicate welcome emails.
    """
    if user.email:
        send_welcome_email(user)
