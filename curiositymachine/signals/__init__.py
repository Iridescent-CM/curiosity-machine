from django.dispatch import Signal

created_account = Signal(providing_args=[])
created_profile = Signal(providing_args=[])
account_activation_confirmed = Signal(providing_args=[])
underage_activation_confirmed = Signal(providing_args=[])
inspiration_gallery_submission_created = Signal(providing_args=['example'])
inspiration_gallery_submissions_approved = Signal(providing_args=['queryset'])
inspiration_gallery_submissions_rejected = Signal(providing_args=['queryset'])
completed_training = Signal(providing_args=[])
member_password_changed = Signal(providing_args=['member', 'resetter'])
