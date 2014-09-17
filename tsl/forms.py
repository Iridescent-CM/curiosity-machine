from django.forms.formsets import formset_factory
from curiositymachine.forms import FilePickerURLField
from django import forms


class AnswerForm(forms.Form):
    question_id = forms.CharField(widget=forms.HiddenInput)
    answer = forms.CharField(widget=forms.TextInput, required=False)
    video_filepicker_url = FilePickerURLField(mimetypes="video/*", openTo='VIDEO', services='VIDEO,COMPUTER', required=False)
    picture_filepicker_url = FilePickerURLField(mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER', required=False)