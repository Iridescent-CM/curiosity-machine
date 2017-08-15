from copy import copy
from datetime import datetime, date
from django import forms
from django.contrib.auth import get_user_model
from django.forms.models import fields_for_model, model_to_dict
from django.forms.extras.widgets import SelectDateWidget
from profiles.models import Profile
from images.models import Image
from videos.models import Video
from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget

User = get_user_model()

BIRTH_YEAR_CHOICES = list(range(datetime.today().year, datetime.today().year - 100, -1))

class UserAndProfileForm(forms.ModelForm):
    """Base class for forms handling account creation/modification.

    UserAndProfileForm extends ModelForm, and builds form fields from the User model as a normal ModelForm would.
    It also introduces additional class attributes that let subclasses build form fields from the Profile model, or include
    useful fields defined within this base class itself.

    UserAndProfileForm's save method returns a User model, but will build the connected Profile and Image models as well.

    Defining a new UserAndProfileForm with an `instance` keyword argument will modify the form slightly to drop the
    username field, since that's never editable, and to make password and confirm_password optional, since they are not
    retrievable to be pre-populated.

    Configuration example:

        class DescendantUserAndProfileForm(UserAndProfileForm):
            class Meta(UserAndProfileForm.Meta):
                fields = [...]                  # fields to include from User
                UserAndProfileForm.Meta.widgets.update({...})     # consider adding widget definitions, etc.
                                                                    to the base class, unless different ones
                                                                    are needed for different subclasses in which
                                                                    case this approach should work

            profile_fields = [...]              # fields to include from Profile
            profile_fields_force = {...}        # dictionary of fields and values to set on Profile model

            form_fields = []                    # fields from _form_field_definitions to include

            make_required = []                  # list of fields to make required in this form (even if not
                                                  required in underlying model)
    """

    profile_fields = []
    profile_fields_force = {}
    make_required = []

    form_fields = []

    _form_field_definitions = {
        'image_url': MediaURLField(
            label="Photo",
            mimetypes="image/*",
            widget=FilePickerPickWidget(attrs={
                "data-fp-opento": "WEBCAM",
                "data-fp-services": "WEBCAM,COMPUTER,CONVERT",
                "data-fp-conversions": "crop,rotate",
                "data-fp-cropratio": 1,
                "data-fp-cropforce": "force",
            }),
            required=False
        ),
        'about_me_filepicker_url': MediaURLField(
            label="About Me Photo or Video",
            mimetypes="video/*,image/*",
            widget=FilePickerPickWidget(attrs={
                "data-fp-opento": 'WEBCAM',
                "data-fp-services": 'VIDEO,WEBCAM,COMPUTER,CONVERT',
                "data-fp-conversions": "crop,rotate",
            }),
            required=False,
        ),
        'about_research_filepicker_url': MediaURLField(
            label="About My Research Photo or Video",
            mimetypes="video/*,image/*",
            widget=FilePickerPickWidget(attrs={
                'data-fp-opento': 'WEBCAM',
                'data-fp-services': 'VIDEO,WEBCAM,COMPUTER,CONVERT',
                "data-fp-conversions": "crop,rotate",
            }),
            required=False,
        ),
        'welcome': forms.CharField(
            required=False,
            widget=forms.HiddenInput(attrs={"id":"welcome"})
        )
    }

    class Meta:
        model = User
        fields = []

        widgets = {
            'password': forms.PasswordInput(render_value=False),
            'city': forms.TextInput,
            'birthday': SelectDateWidget(years=BIRTH_YEAR_CHOICES),
            'parent_first_name': forms.TextInput,
            'parent_last_name': forms.TextInput,
            'title': forms.TextInput,
            'employer': forms.TextInput,
            'source': forms.HiddenInput,
            'welcome': forms.HiddenInput,
        }

        labels = {
            'title': "What Is My Profession",
            'employer': "Where Do I Work?",
            'expertise': "Expertise In",
            'organization': "School/Organization",
        }

        error_messages = {
            'username': {
                'invalid': "Username can only include letters, digits and @/./+/-/_"
            }
        }

    def __init__(self, *args, **kwargs):
        super(UserAndProfileForm, self).__init__(*args, **kwargs)
        instance = kwargs.get('instance')

        if "password" in self.fields and not instance:
            self.fields['confirm_password'] = copy(self.fields['password'])
            self.fields['confirm_password'].label = "Confirm password"

        profile_fields = fields_for_model(
            Profile,
            self.profile_fields,
            [],
            self._meta.widgets,
            None,
            [],
            self._meta.labels,
            self._meta.help_texts,
            self._meta.error_messages
        )
        if instance:
            initial = model_to_dict(instance.profile, self.profile_fields)
            for fieldname, value in initial.items():
                profile_fields.get(fieldname).initial = value
        self.fields.update(profile_fields)

        self.fields.update({key: self._form_field_definitions[key] for key in self.form_fields})

        for fieldname in self.make_required:
            self.fields[fieldname].required = True

        if "birthday" in self.fields and not instance:
            self.fields['birthday'].initial = date(date.today().year, 1, 1)

        if instance:
            if "password" in self.fields:
                del self.fields['password']
            if "username" in self.fields:
                del self.fields['username']

    def clean_birthday(self):
        birthday = self.cleaned_data['birthday']
        if birthday == date(date.today().year, 1, 1):
            # birthday hasn't been set
            raise forms.ValidationError('Please set your birthday.')
        return birthday

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            password = password.strip()
            if len(password) < 6:
                raise forms.ValidationError('Password must be at least 6 characters long')
        return password

    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')
        if confirm_password:
            confirm_password = confirm_password.strip()
        return confirm_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('A user with that username already exists.', code='duplicate')
        return username

    def clean(self):
        super(UserAndProfileForm, self).clean()

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self.add_error('password', "Passwords do not match.")

        return self.cleaned_data

    def save(self, commit=True):
        user = super(UserAndProfileForm, self).save(commit=False)
        if "password" in self.cleaned_data:
            user.set_password(self.cleaned_data["password"])

        if hasattr(self.instance, "profile"):
            profile = self.instance.profile
        else:
            profile = Profile()
        profile_data = {key: self.cleaned_data[key] for key in self.profile_fields}
        profile_data.update(self.profile_fields_force)
        for key, value in profile_data.items():
            setattr(profile, key, value)
        profile.user = user

        if self.cleaned_data.get("about_me_filepicker_url"):
            media = self.cleaned_data.get("about_me_filepicker_url")
            if media['mimetype'].startswith('image'):
                image = Image.from_source_with_job(media['url'])
                profile.about_me_image_id = image.id
                profile.about_me_video_id = None

            elif media['mimetype'].startswith('video'):
                video = Video.from_source_with_job(media['url'])
                profile.about_me_image_id = None
                profile.about_me_video_id = video.id

        if self.cleaned_data.get('about_research_filepicker_url'):
            media = self.cleaned_data.get("about_research_filepicker_url")
            if media['mimetype'].startswith('image'):
                image = Image.from_source_with_job(media['url'])
                profile.about_research_image_id = image.id
                profile.about_research_video_id = None

            elif media['mimetype'].startswith('video'):
                video = Video.from_source_with_job(media['url'])
                profile.about_research_image_id = None
                profile.about_research_video_id = video.id

        profile_image = None
        if self.cleaned_data.get("image_url"):
            profile_image = Image(source_url=self.cleaned_data['image_url']['url'])
            profile.image = profile_image

        if commit:
            user.save()
            profile.user = user # no user_id otherwise
            if profile_image:
                profile_image.save()
                profile_image.fetch_from_source()
                profile.image = profile_image # no image_id otherwise

            profile.save()

        return user
