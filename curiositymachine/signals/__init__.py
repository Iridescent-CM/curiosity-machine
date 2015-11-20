from django.dispatch import Signal

approved_project_for_gallery = Signal(providing_args=['example'])
started_first_project = Signal(providing_args=['progress'])
posted_comment = Signal(providing_args=['comment'])
