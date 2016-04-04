from django import forms
from curiositymachine.forms import MediaURLField
from curiositymachine.widgets import FilePickerPickWidget

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    visual_media = MediaURLField(
        widget=FilePickerPickWidget(preview=True, attrs={
            "data-fp-opento": 'WEBCAM',
            "data-fp-services": 'VIDEO,WEBCAM,COMPUTER,CONVERT',
            "data-fp-conversions": 'crop,rotate',
        }),
        mimetypes="video/*,image/*",
        required=False
    )
    question_text = forms.CharField(widget=forms.HiddenInput, required=False)
