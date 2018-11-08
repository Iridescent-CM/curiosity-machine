from django import forms
from .models import *

class PermissionSlipSignatureForm(forms.ModelForm):
    class Meta:
        model = PermissionSlip
        fields = ['signature',]