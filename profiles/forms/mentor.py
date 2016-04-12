from profiles.forms.common import UserAndProfileForm

class MentorUserAndProfileForm(UserAndProfileForm):
    profile_fields = [
        'city',
        'source'
    ]
    profile_fields_force = {
        'is_mentor': True
    }
    make_required = ['email', 'city']

    form_fields = [
        'image_url',
        'about_me_filepicker_url',
        'about_research_filepicker_url',
        'welcome'
    ]

    class Meta(UserAndProfileForm.Meta):
        fields = [
            'username',
            'password',
            'email',
            'first_name',
            'last_name'
        ]

class MentorUserAndProfileChangeForm(MentorUserAndProfileForm):
    profile_fields = [
        'city',
        'title',
        'employer',
        'expertise',
        'about_me',
        'about_research'
    ]

    