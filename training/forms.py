from django import forms
from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    visual_media = MediaURLField(
        widget=FilePickerPickWidget(
            preview=True,
            attrs={
                "data-fp-opento": 'WEBCAM',
                "data-fp-services": 'VIDEO,WEBCAM,COMPUTER,CONVERT',
                "data-fp-conversions": 'crop,rotate',
            }
        ),
        mimetypes="video/*,image/*",
        required=False
    )

    def clean(self):
        cleaned_data = super(CommentForm, self).clean()
        media = cleaned_data['visual_media']
        text = cleaned_data['text']

        if not media and not text:
            raise forms.ValidationError("Comments must contain text, image, or video")
