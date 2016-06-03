from django import forms
from django.conf import settings
from django.template.defaultfilters import filesizeformat

class ImportForm(forms.Form):
    csv_file = forms.FileField(
        required=True,
        allow_empty_file=False,
        help_text="File must be UTF-8 encoded, and less than %s" % filesizeformat(settings.FILE_UPLOAD_MAX_MEMORY_SIZE)
    )

    def clean_csv_file(self):
        csv_file = self.cleaned_data.get('csv_file')
        if csv_file.multiple_chunks():
            raise forms.ValidationError("File is too large (%s)" % filesizeformat(csv_file.size))
        contents = csv_file.read()
        csv_file.seek(0)
        try:
            contents = contents.decode('utf-8')
        except UnicodeDecodeError:
            raise forms.ValidationError("File does not appear to be UTF-8 encoded")
        except:
            raise forms.ValidationError("Unknown error while decoding file")

        return csv_file
