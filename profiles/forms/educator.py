from profiles.forms.common import UserAndProfileForm


class EducatorUserAndProfileForm(UserAndProfileForm):
    profile_fields = [
        'city',
        'source'
    ]
    profile_fields_force = {
        'is_educator': True
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
