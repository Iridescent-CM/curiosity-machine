from django.apps import AppConfig


class HellosignConfig(AppConfig):
    name = 'hellosign'
    verbose_name = 'E-signatures'

    def ready(self):
        import hellosign.signals.handlers
