from django import forms
from curiositymachine.widgets import FilePickerFileWidget
from django.conf import settings

class FilePickerURLField(forms.URLField):
    widget = FilePickerFileWidget
    default_mimetypes = "*/*"

    def __init__(self, *args, **kwargs):
        self.apikey = kwargs.pop('apikey', settings.FILEPICKER_API_KEY)
        self.mimetypes = kwargs.pop('mimetypes', self.default_mimetypes)
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        return {'data-fp-apikey': self.apikey, 'data-fp-mimetypes': self.mimetypes,}

class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)
    filepicker_url = FilePickerURLField()
