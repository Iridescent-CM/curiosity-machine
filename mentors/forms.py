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
    title = forms.CharField(
        label="What Is My Profession",
        required=False
    )
    employer = forms.CharField(
        label="Where Do I Work",
        required=False
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

    def get_role(self):
        return UserRole.mentor
