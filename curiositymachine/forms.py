from django import forms
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget
from curiositymachine.widgets import FilePickerFileWidget, FilePickerDragDropWidget

class FilePickerField(forms.URLField):
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
        return {'data-fp-apikey': self.apikey, 'data-fp-mimetypes': self.mimetypes, 'data-fp-openTo': self.openTo, 'data-fp-services': self.services, 'data-fp-button-class': 'btn btn-primary'}

class FilePickerURLField(FilePickerField):
    widget = FilePickerFileWidget
    
class FilePickerDragDropField(FilePickerField):
    widget = FilePickerDragDropWidget
    
class AnalyticsForm(forms.Form):
    start_date = forms.DateField(widget=SelectDateWidget())
    end_date = forms.DateField(widget=SelectDateWidget())