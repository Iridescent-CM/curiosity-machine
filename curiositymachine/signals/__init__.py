from django.dispatch import Signal

created_account = Signal(providing_args=[])
underage_activation_confirmed = Signal(providing_args=['account'])
approved_project_for_gallery = Signal(providing_args=['example'])
started_first_project = Signal(providing_args=['progress'])
posted_comment = Signal(providing_args=['comment'])
progress_considered_complete = Signal(providing_args=['progress'])
approved_training_task = Signal(providing_args=['user', 'task'])
completed_training = Signal(providing_args=['approver'])
