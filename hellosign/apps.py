from django.apps import AppConfig


class HellosignConfig(AppConfig):
    name = 'hellosign'
    verbose_name = 'Curiosity Machine e-signatures'

    def ready(self):
        import hellosign.signals.handlers
