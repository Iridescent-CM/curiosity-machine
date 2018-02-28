from django.dispatch import Signal

created_account = Signal(providing_args=[])
created_profile = Signal(providing_args=[])
account_activation_confirmed = Signal(providing_args=[])
underage_activation_confirmed = Signal(providing_args=[])
completed_training = Signal(providing_args=[])
member_password_changed = Signal(providing_args=['member', 'resetter'])
