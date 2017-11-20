from django.apps import AppConfig

class ProfilesConfig(AppConfig):
    name = 'profiles'
    verbose_name = 'Authentication and Authorization'

    def ready(self):
        import profiles.signals.handlers
