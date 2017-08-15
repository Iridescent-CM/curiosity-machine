from django.apps import AppConfig

class CuriosityMachineConfig(AppConfig):
    name = 'curiositymachine'
    verbose_name = 'Curiosity Machine'

    def ready(self):
        import curiositymachine.signals.handlers
