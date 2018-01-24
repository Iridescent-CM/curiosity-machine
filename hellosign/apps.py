from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class HellosignConfig(AppConfig):
    name = 'hellosign'
    verbose_name = 'E-signatures'

    def ready(self):
        import hellosign.signals.handlers
        if not settings.HELLOSIGN_ENVIRONMENT_NAME:
            raise ImproperlyConfigured("Please configure a HELLOSIGN_ENVIRONMENT_NAME. See hellosign/README.md for details.")
