from django.apps import AppConfig

class CMCommentsConfig(AppConfig):
    name = 'cmcomments'
    verbose_name = 'Curiosity Machine Comments'

    def ready(self):
        import cmcomments.signals.handlers

