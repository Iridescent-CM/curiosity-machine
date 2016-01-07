from django.apps import AppConfig

class CMEmailsConfig(AppConfig):
    name = 'cmemails'
    verbose_name = 'Curiosity Machine Emails'

    def ready(self):
        import cmemails.signals.handlers
