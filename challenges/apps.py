from django.apps import AppConfig

class ChallengesConfig(AppConfig):
    name = 'challenges'
    verbose_name = 'Challenges'

    def ready(self):
        import challenges.signals.handlers
