from django import forms
from django_bleach.forms import BleachField
from django.conf import settings
from .validators import validate_color
from django.utils.safestring import mark_safe

class MaterialsForm(forms.Form):
    materials = BleachField(required=True,
                        allowed_tags=settings.BLEACH_ALLOWED_TAGS,
                        allowed_attributes=settings.BLEACH_LIB_ATTRIBUTES,
                        allowed_styles=settings.BLEACH_ALLOWED_STYLES)

    def __init__(self, *args, **kwargs):
        progress = kwargs.pop('progress')
        super(MaterialsForm, self).__init__(*args, **kwargs)
        self.fields['materials'].initial = progress.materials_list

class ThemeForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput, required=True, help_text="Name")
    icon = forms.CharField(widget=forms.TextInput, required=False, help_text=mark_safe("This determines the icon that displays on the theme. Choose and icon by entering one of the following icon classes:<br><strong>icon-satellite icon-robotics icon-ocean icon-neuroscience icon-inventor icon-food icon-engineer icon-electrical icon-civil icon-builder icon-biomimicry icon-biomechanics icon-art icon-aerospace icon-compsci</strong><br /><br />Additionally available are the set of icons located here: <a href='http://getbootstrap.com/components/'>Bootstrap Glyphicons</a>. Enter both class names separated with a space. for example \"glyphicon glyphicon-film\" without quotes."))
    color = forms.CharField(widget=forms.TextInput, required=False, validators=[validate_color], help_text=mark_safe("Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>"))


class FilterForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput, required=True, help_text="Name")
    color = forms.CharField(widget=forms.TextInput, required=True, validators=[validate_color], help_text=mark_safe("Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>"))
    visible = forms.BooleanField()