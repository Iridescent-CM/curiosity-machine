from django import forms
from curiositymachine.forms import FilePickerMediaField
from curiositymachine.widgets import FilePickerPickWidget

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    visual_media = FilePickerMediaField(
        widget=FilePickerPickWidget(preview=True),
        mimetypes="video/*,image/*",
        openTo='WEBCAM',
        services='VIDEO,WEBCAM,COMPUTER,CONVERT',
        conversions='crop,rotate',
        required=False
    )
    question_text = forms.CharField(widget=forms.HiddenInput, required=False)
