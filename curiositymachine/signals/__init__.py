from django.dispatch import Signal

created_account = Signal(providing_args=[])
created_profile = Signal(providing_args=[])
underage_activation_confirmed = Signal(providing_args=[])
inspiration_gallery_submission_created = Signal(providing_args=['example'])
inspiration_gallery_submissions_approved = Signal(providing_args=['queryset'])
inspiration_gallery_submissions_rejected = Signal(providing_args=['queryset'])
started_first_project = Signal(providing_args=['progress'])
posted_comment = Signal(providing_args=['comment'])
progress_considered_complete = Signal(providing_args=['progress'])
completed_training = Signal(providing_args=[])
student_password_changed = Signal(providing_args=['student', 'resetter'])
