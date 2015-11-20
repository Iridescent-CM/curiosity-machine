from django.dispatch import Signal

approved_project_for_gallery = Signal(providing_args=['example'])
posted_comment = Signal(providing_args=['comment'])

