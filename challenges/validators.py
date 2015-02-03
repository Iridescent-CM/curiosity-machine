from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re

def validate_color(value):
    regex = r"^#?[0-9a-fA-F]+$"
    if not re.match(regex, value):
    	raise ValidationError(_('Invalid Color. Use a hex color like #44b1cc.'), code='invalid')
