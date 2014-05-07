from django import forms
from curiositymachine.forms import FilePickerURLField

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    video_filepicker_url = FilePickerURLField(mimetypes="video/*", openTo='VIDEO', services='VIDEO,COMPUTER', required=False)
    picture_filepicker_url = FilePickerURLField(mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER', required=False)
    question_text = forms.CharField(widget=forms.HiddenInput, required=False)
