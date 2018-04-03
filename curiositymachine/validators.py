from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

class UsernameUniquenessValidator:
    def __call__(self, value):
        if get_user_model().objects.filter(username__iexact=value).exists():
            raise ValidationError('A user with that username already exists.', code='duplicate')

    def __eq__(self, other):
        return isinstance(other, self.__class__)

username_validators = [
    UsernameUniquenessValidator(),
    get_user_model().username_validator,
]

lower_slug_re = re.compile(r'^[-a-z0-9_]+\Z')
validate_lowercase_slug = RegexValidator(
    lower_slug_re,
    "Enter a valid 'slug' consisting of lowercase letters, numbers, underscores or hyphens.",
    'invalid'
)

def validate_simple_latin(value):
    invalids = [
        char
        for char in value
        if not (
            '\u0000' <= char <= '\u007F'        # Basic Latin
            or '\u0080' <= char <= '\u00FF'     # Latin-1 Supplement
        )
    ]
    if invalids:
        raise ValidationError(
            'Value contains invalid characters: %s' % ' '.join(invalids),
            code='invalid_chars'
        )
