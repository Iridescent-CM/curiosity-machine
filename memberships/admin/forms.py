from django import forms
from s3direct.widgets import S3DirectWidget

class ImportForm(forms.Form):
    csv_file = forms.URLField(widget=S3DirectWidget(dest='member-import'))
