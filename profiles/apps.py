from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'profiles'

    def ready(self):
        # Importing signals here ensures the receiver decorators are
        # registered once Django has fully loaded all models.
        import profiles.signals  # noqa: F401
