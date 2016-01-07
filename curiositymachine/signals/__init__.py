from django.dispatch import Signal

created_account = Signal(providing_args=[])
underage_activation_confirmed = Signal(providing_args=['account'])
approved_project_for_gallery = Signal(providing_args=['example'])
approved_project_for_reflection = Signal(providing_args=['progress'])
started_first_project = Signal(providing_args=['progress'])
posted_comment = Signal(providing_args=['comment'])
approved_training_task = Signal(providing_args=['user', 'task'])
completed_training = Signal(providing_args=['approver'])
