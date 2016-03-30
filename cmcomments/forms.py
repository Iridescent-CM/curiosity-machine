from django import forms
from curiositymachine.forms import FilePickerMediaField

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)
    visual_media = FilePickerMediaField(
        mimetypes="video/*,image/*",
        openTo='WEBCAM',
        services='VIDEO,WEBCAM,COMPUTER',
        required=False
    )
    question_text = forms.CharField(widget=forms.HiddenInput, required=False)
