from django import forms
from django.conf import settings
from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    visual_media = MediaURLField(
        widget=FilePickerPickWidget(
            preview=False,
            attrs={
                "data-fp-opento": 'WEBCAM',
                "data-fp-services": 'VIDEO,WEBCAM,COMPUTER,CONVERT',
                "data-fp-conversions": 'crop,rotate',
                "data-fp-video-length": settings.FILEPICKER_MAX_VIDEO_LENGTH_SECONDS,
                "data-auto-submit": "true",
            }
        ),
        mimetypes="video/*,image/*",
        required=False
    )
    question_text = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        media = cleaned_data['visual_media']
        text = cleaned_data['text']

        if not media and not text:
            raise forms.ValidationError("Comments must contain text, image, or video")
