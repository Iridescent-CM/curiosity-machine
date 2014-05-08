from django import forms
from curiositymachine.forms import FilePickerURLField

class ChallengeVideoForm(forms.Form):
    video_filepicker_url = FilePickerURLField(mimetypes="video/*", openTo='VIDEO')
