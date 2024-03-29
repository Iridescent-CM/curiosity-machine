from django.forms import widgets, Widget
from django.conf import settings
from django.template.loader import render_to_string
from django.forms.utils import flatatt

class FilePickerPickWidget(Widget):
    """
    A Filepicker widget similar to <input type="file"> with optional media preview.
    Value is a dictionary of media URL and mimetype information, must be used with
    a field type that can parse this, like MediaURLField.
    """

    class Media:
        js = ()

    def __init__(self, attrs=None, preview=False, text=None):
        self.text = text
        _attrs = {
            'data-fp-apikey': settings.FILEPICKER_API_KEY,
            'class': 'btn btn-primary pickwidget-button'
        }
        if (attrs):
            _attrs.update(attrs)
        super(FilePickerPickWidget, self).__init__(_attrs)

    def render(self, name, value, attrs={}, renderer=None):
        id = attrs.pop('id', None)
        context = {
            "id": id,
            "name": name,
            "value": value,
            "button_text": self.text,
            "attrs": flatatt(self.build_attrs(self.attrs, attrs))
        }
        return render_to_string('widgets/pickwidget.html', context)

    def value_from_datadict(self, data, files, name):
        return [
            data.get(name + '_url', None),
            data.get(name + '_mimetype', None),
            data.get(name + '_filename', None),
        ]