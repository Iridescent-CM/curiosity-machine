from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget
from django import forms
from images.models import Image
from profiles.forms import ProfileModelForm
from profiles.models import UserRole
from videos.models import Video
from .models import MentorProfile

class MentorProfileForm(ProfileModelForm):
    class Meta:
        model = MentorProfile
        fields = [
            'city',
            'title',
            'employer',
            'expertise',
            'about_me',
            'about_research',
        ]

    city = forms.CharField(required=True)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    title = forms.CharField(
        label="What Is My Profession",
        required=True
    )
    employer = forms.CharField(
        label="Where Do I Work",
        required=True
    )
    expertise = forms.CharField(
        widget=forms.Textarea,
        label="Expertise In",
        required=False
    )

    image_url = MediaURLField(
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
    )

    about_me_media_url = MediaURLField(
        label="About Me Photo or Video",
        mimetypes="video/*,image/*",
        widget=FilePickerPickWidget(attrs={
            "data-fp-opento": 'WEBCAM',
            "data-fp-services": 'VIDEO,WEBCAM,COMPUTER,CONVERT',
            "data-fp-conversions": "crop,rotate",
        }),
        required=False,
    )

    about_research_media_url = MediaURLField(
        label="About My Research Photo or Video",
        mimetypes="video/*,image/*",
        widget=FilePickerPickWidget(attrs={
            'data-fp-opento': 'WEBCAM',
            'data-fp-services': 'VIDEO,WEBCAM,COMPUTER,CONVERT',
            "data-fp-conversions": "crop,rotate",
        }),
        required=False,
    )

    def save_related(self, obj):
        if self.cleaned_data.get("image_url"):
            img = Image(source_url=self.cleaned_data['image_url']['url'])
            img.save()
            obj.image = img

        if self.cleaned_data.get("about_me_media_url"):
            media = self.cleaned_data.get("about_me_media_url")
            if media['mimetype'].startswith('image'):
                image = Image.from_source_with_job(media['url'])
                obj.about_me_image_id = image.id
                obj.about_me_video_id = None
            elif media['mimetype'].startswith('video'):
                video = Video.from_source_with_job(media['url'])
                obj.about_me_image_id = None
                obj.about_me_video_id = video.id

        if self.cleaned_data.get("about_research_media_url"):
            media = self.cleaned_data.get("about_research_media_url")
            if media['mimetype'].startswith('image'):
                image = Image.from_source_with_job(media['url'])
                obj.about_research_image_id = image.id
                obj.about_research_video_id = None
            elif media['mimetype'].startswith('video'):
                video = Video.from_source_with_job(media['url'])
                obj.about_research_image_id = None
                obj.about_research_video_id = video.id

        return obj

    def update_user(self):
        if self.cleaned_data.get('first_name'):
            self.user.first_name = self.cleaned_data['first_name']
        if self.cleaned_data.get('last_name'):
            self.user.last_name = self.cleaned_data['last_name']

    def get_initial(self, user, instance):
        return super().get_initial(
            user,
            instance,
            first_name=user.first_name,
            last_name=user.last_name,
        )

    def get_role(self):
        return UserRole.mentor
