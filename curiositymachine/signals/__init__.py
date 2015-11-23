from django.dispatch import Signal

created_account = Signal(providing_args=[])
approved_project_for_gallery = Signal(providing_args=['example'])
approved_project_for_reflection = Signal(providing_args=['progress'])
started_first_project = Signal(providing_args=['progress'])
posted_comment = Signal(providing_args=['comment'])
