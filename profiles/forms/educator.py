from profiles.forms.common import UserAndProfileForm
from profiles.models import UserRole


class EducatorUserAndProfileForm(UserAndProfileForm):
    profile_fields = [
        'city',
        'source',
        'organization'
    ]
    profile_fields_force = {
        'role': UserRole.educator.value
    }
    make_required = ['email', 'city', 'organization']

    form_fields = ['image_url', 'welcome']

    class Meta(UserAndProfileForm.Meta):
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        ]

class EducatorUserAndProfileChangeForm(EducatorUserAndProfileForm):
    make_required = ['email', 'city']
