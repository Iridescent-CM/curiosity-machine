from profiles.forms.common import UserAndProfileForm

class ParentUserAndProfileForm(UserAndProfileForm):
    profile_fields = [
        'city'
    ]
    profile_fields_force = {
        'is_parent': True
    }
    make_required = ['email', 'city']

    form_fields = ['image_url']

    class Meta(UserAndProfileForm.Meta):
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        ]
