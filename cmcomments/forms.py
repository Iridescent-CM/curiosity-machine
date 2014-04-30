from django import forms
from curiositymachine.widgets import FilePickerFileWidget
from django.conf import settings

class FilePickerURLField(forms.URLField):
    widget = FilePickerFileWidget
    default_mimetypes = "*/*"
    default_openTo = 'COMPUTER'
    default_services = ''

    def __init__(self, *args, **kwargs):
        self.apikey = kwargs.pop('apikey', settings.FILEPICKER_API_KEY)
        self.mimetypes = kwargs.pop('mimetypes', self.default_mimetypes)
        self.openTo = kwargs.pop('openTo', self.default_openTo)
        self.services = kwargs.pop('services', self.default_services)
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        return {'data-fp-apikey': self.apikey, 'data-fp-mimetypes': self.mimetypes, 'data-fp-openTo': self.openTo, 'data-fp-services': self.services, 'data-fp-button-class': 'btn btn-lg btn-primary'}

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    video_filepicker_url = FilePickerURLField(mimetypes="video/*", openTo='VIDEO', services='VIDEO,COMPUTER', required=False)
    picture_filepicker_url = FilePickerURLField(mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER', required=False)
    question_text = forms.CharField(widget=forms.HiddenInput, required=False)
