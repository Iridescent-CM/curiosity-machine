from django.dispatch import Signal

started_first_project = Signal(providing_args=['progress'])
posted_comment = Signal(providing_args=['comment'])